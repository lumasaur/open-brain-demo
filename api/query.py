"""
Open Brain Demo — Retrieval API
Provides hybrid search (70% vector + 30% FTS), node lookup, and graph data
for the demo frontend.

Functions:
  search_demo(query, limit=5) -> list[dict]
  get_node(node_id) -> dict
  get_graph_data() -> dict

Usage (standalone):
  python query.py --test   # Run validation queries
  python query.py --serve  # Start FastAPI server (optional)
"""

import sqlite3
import json
import os
import struct
import math
import argparse

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ob_demo.db")

# ---------------------------------------------------------------------------
# EMBEDDING HELPER
# ---------------------------------------------------------------------------

_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _embed(text: str) -> list[float]:
    return _get_model().encode(text).tolist()


def _blob_to_vec(blob: bytes) -> list[float]:
    """Deserialize float32 blob to list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# CORE API FUNCTIONS
# ---------------------------------------------------------------------------

def search_demo(query: str, limit: int = 5) -> list[dict]:
    """
    Hybrid search: 70% vector similarity + 30% FTS rank.
    Returns top `limit` results with node content, metadata, and linked node IDs.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query_vec = _embed(query)

    # ── Vector candidates (top 25 by cosine similarity) ──────────────────
    rows = conn.execute(
        "SELECT id, content, domain, intent, source_file, embedding FROM memory_nodes"
    ).fetchall()

    vector_scores = []
    for row in rows:
        if row["embedding"] is None:
            continue
        node_vec = _blob_to_vec(row["embedding"])
        sim = _cosine_similarity(query_vec, node_vec)
        vector_scores.append((row["id"], sim, dict(row)))

    vector_scores.sort(key=lambda x: x[1], reverse=True)
    top_vector = {row_id: (sim, meta) for row_id, sim, meta in vector_scores[:25]}

    # ── FTS candidates ───────────────────────────────────────────────────
    try:
        fts_rows = conn.execute(
            """SELECT rowid, rank FROM nodes_fts
               WHERE nodes_fts MATCH ?
               ORDER BY rank LIMIT 25""",
            (query,),
        ).fetchall()
    except Exception:
        fts_rows = []

    # Normalize FTS ranks (rank is negative in FTS5; more negative = better)
    fts_scores = {}
    if fts_rows:
        ranks = [abs(r["rank"]) for r in fts_rows]
        max_rank = max(ranks) if ranks else 1
        for r in fts_rows:
            fts_scores[r["rowid"]] = abs(r["rank"]) / max_rank

    # ── Blend: 70% vector + 30% FTS ─────────────────────────────────────
    # Collect candidate IDs from both sources
    candidate_ids = set(top_vector.keys()) | set(fts_scores.keys())

    # For each candidate, compute blended score
    blended = []
    for node_id in candidate_ids:
        vec_score = top_vector.get(node_id, (0.0, None))[0]
        fts_score = fts_scores.get(node_id, 0.0)
        combined = 0.7 * vec_score + 0.3 * fts_score
        blended.append((node_id, combined))

    blended.sort(key=lambda x: x[1], reverse=True)
    top_ids = [node_id for node_id, _ in blended[:limit]]
    top_scores = {node_id: score for node_id, score in blended[:limit]}

    # ── Fetch full node data + linked node IDs ───────────────────────────
    results = []
    for node_id in top_ids:
        node = conn.execute(
            "SELECT id, content, domain, intent, source_file, created_at FROM memory_nodes WHERE id=?",
            (node_id,),
        ).fetchone()
        if not node:
            continue

        # Get linked node IDs for graph highlight
        linked = conn.execute(
            """SELECT DISTINCT
                   CASE WHEN from_id = ? THEN to_id ELSE from_id END AS linked_id
               FROM memory_links
               WHERE from_id = ? OR to_id = ?""",
            (node_id, node_id, node_id),
        ).fetchall()
        linked_ids = [r["linked_id"] for r in linked]

        results.append({
            "id": node["id"],
            "content": node["content"],
            "domain": node["domain"],
            "intent": node["intent"],
            "source_file": node["source_file"],
            "relevance_score": round(top_scores[node_id], 4),
            "linked_node_ids": linked_ids,
        })

    conn.close()
    return results


def get_node(node_id: int) -> dict:
    """Return full node by ID including all metadata."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    node = conn.execute(
        """SELECT id, content, domain, intent, source, source_file,
                  content_hash, model_id, created_at, visibility
           FROM memory_nodes WHERE id=?""",
        (node_id,),
    ).fetchone()

    if not node:
        conn.close()
        return {}

    links_out = conn.execute(
        "SELECT to_id, link_type FROM memory_links WHERE from_id=?", (node_id,)
    ).fetchall()
    links_in = conn.execute(
        "SELECT from_id, link_type FROM memory_links WHERE to_id=?", (node_id,)
    ).fetchall()

    conn.close()
    return {
        "id": node["id"],
        "content": node["content"],
        "domain": node["domain"],
        "intent": node["intent"],
        "source": node["source"],
        "source_file": node["source_file"],
        "content_hash": node["content_hash"],
        "model_id": node["model_id"],
        "created_at": node["created_at"],
        "visibility": node["visibility"],
        "links_out": [{"to_id": r["to_id"], "link_type": r["link_type"]} for r in links_out],
        "links_in": [{"from_id": r["from_id"], "link_type": r["link_type"]} for r in links_in],
    }


def get_graph_data() -> dict:
    """
    Return D3 initialization payload:
      nodes: [{id, label, domain, degree}]
      links: [{source, target, link_type}]
    Label = first 60 chars of content.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    raw_nodes = conn.execute(
        "SELECT id, content, domain FROM memory_nodes"
    ).fetchall()

    raw_links = conn.execute(
        "SELECT from_id, to_id, link_type FROM memory_links"
    ).fetchall()

    # Compute degree map
    degree_map: dict[int, int] = {}
    for link in raw_links:
        degree_map[link["from_id"]] = degree_map.get(link["from_id"], 0) + 1
        degree_map[link["to_id"]] = degree_map.get(link["to_id"], 0) + 1

    nodes = [
        {
            "id": n["id"],
            "label": n["content"][:60].rstrip() + ("…" if len(n["content"]) > 60 else ""),
            "domain": n["domain"],
            "degree": degree_map.get(n["id"], 0),
        }
        for n in raw_nodes
    ]

    links = [
        {
            "source": lnk["from_id"],
            "target": lnk["to_id"],
            "link_type": lnk["link_type"],
        }
        for lnk in raw_links
    ]

    conn.close()
    return {"nodes": nodes, "links": links}


# ---------------------------------------------------------------------------
# VALIDATION — 4 SAMPLE QUERIES
# ---------------------------------------------------------------------------

VALIDATION_QUERIES = [
    "How does Open Brain handle memory across sessions?",
    "What's the VBOD and why does it work?",
    "What would you do differently if you rebuilt this?",
    "How could this help a small business owner?",
]


def run_validation():
    print("=" * 60)
    print("RETRIEVAL API VALIDATION")
    print("=" * 60)

    # Test get_graph_data
    graph = get_graph_data()
    print(f"\n✓ get_graph_data(): {len(graph['nodes'])} nodes, {len(graph['links'])} links")

    # Test get_node
    if graph["nodes"]:
        first_id = graph["nodes"][0]["id"]
        node = get_node(first_id)
        print(f"✓ get_node({first_id}): domain={node.get('domain')}, intent={node.get('intent')}")

    # Test search_demo
    print("\nValidation queries:")
    for q in VALIDATION_QUERIES:
        results = search_demo(q, limit=5)
        print(f"\n  Q: {q!r}")
        for r in results:
            snippet = r["content"][:80].replace("\n", " ")
            print(f"    [{r['relevance_score']:.3f}] {r['domain']}/{r['intent']} — {snippet}…")
            print(f"       linked_ids: {r['linked_node_ids'][:5]}")

    print("\n✓ Validation complete")


# ---------------------------------------------------------------------------
# OPTIONAL FASTAPI SERVER
# ---------------------------------------------------------------------------

def run_server():
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
        import anthropic
        import uvicorn
    except ImportError:
        print("FastAPI/uvicorn/anthropic not installed.")
        print("Run: pip install fastapi uvicorn anthropic")
        return

    app = FastAPI(title="Open Brain Demo API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/graph")
    def graph_endpoint():
        return get_graph_data()

    @app.get("/node/{node_id}")
    def node_endpoint(node_id: int):
        return get_node(node_id)

    @app.get("/search")
    def search_endpoint(q: str, limit: int = 5):
        return {"results": search_demo(q, limit)}

    class ChatRequest(BaseModel):
        query: str
        context: str

    SYSTEM_PROMPT = """You are the Open Brain demo assistant. You answer questions about an AI-powered
persistent memory system called Open Brain, grounded strictly in the provided memory excerpts.

Rules:
- Answer concisely and specifically based on the memory context.
- If the context doesn't contain relevant information, say so briefly.
- Do not invent facts not in the provided context.
- Write in a clear, direct tone — this is a portfolio demo.
- Keep responses under 250 words unless a detailed explanation is genuinely needed."""

    def sse_stream(query: str, context: str):
        client = anthropic.Anthropic()
        prompt = f"""Memory context:\n{context}\n\nQuestion: {query}"""
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"

    @app.post("/chat")
    def chat_endpoint(req: ChatRequest):
        return StreamingResponse(
            sse_stream(req.query, req.context),
            media_type="text/event-stream",
        )

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting API server at http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run validation queries")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI server")
    args = parser.parse_args()

    if args.serve:
        run_server()
    else:
        run_validation()
