# Open Brain Demo — Build Log

**Session type:** Overnight autonomous build
**Started:** 2026-03-11
**Spec source:** `C:\GitHub\.claude\User File Connection\ob_demo_node_spec.md`
**Open Brain context:** Searched `demo node spec seeding 125 nodes portfolio demo` → Node 274 (portfolio demo strategy), 276 (Kangaroo CRM spec), 278 (job pipeline spec)

---

## Step 0 — Context Load
Status: **complete**

- Spec file confirmed: `ob_demo_node_spec.md` (92.7KB, 125 nodes × 5 clusters)
- Open Brain search returned portfolio demo strategy (Node 274) — confirms Open Brain demo is Project 2 (Center, featured) with graph viz + AI chatbot grounded in curated demo nodes
- `memory_stats` returned error: `no such table: memory_nodes` (MCP connected to different instance)
- **Decision:** Defaulting to `all-MiniLM-L6-v2` per spec fallback instructions
- Spec confirms: demo chatbot calls Anthropic API directly; no MCP exposure needed; demo DB is self-contained and read-only for chatbot

---

## Phase 1 — Demo Database
Status: **in-progress**

Decisions made:
- Embedding model: `all-MiniLM-L6-v2` (sentence-transformers) — 384 dimensions
- DB location: `C:\GitHub\open-brain-demo\data\ob_demo.db`
- Seeding in cluster order: META → TECHNICAL → CONSULTING → VBOD → PORTFOLIO
- All nodes: source = 'manual', visibility = 'public'

Issues encountered: none yet

Output files:
- [ ] `data/ob_demo.db`
- [ ] `data/node_id_map.json`

---

## Phase 2 — Link Wiring
Status: **complete**

Output:
- 140 spec links + 12 supplementary hub links = 152 total
- Supplementary links added: M1 (3), T1 (3), CON1 (1), V1 (1), PORT1 (4) → all hubs reached 8-9 degree
- degree_audit.json generated

---

## Phase 3 — Retrieval API
Status: **complete**

Output: `api/query.py`
- `search_demo()`: 70% vector + 30% FTS5 hybrid blend, top-25 candidates each
- `get_node()`: full node + directional links
- `get_graph_data()`: D3 initialization payload
- `/chat` SSE streaming endpoint: Anthropic claude-sonnet-4-6, 512 token cap
- FastAPI + CORS + uvicorn server

Validation results:
- get_graph_data: 125 nodes, 152 links
- get_node(1): domain=meta, intent=reference, links_out=8
- Q1 (memory across sessions): 0.498 relevance — meta/reference node
- Q2 (VBOD): 0.363 — meta/insight node
- Q3 (rebuild counterfactual): 0.167 — expected low (no counterfactual nodes in corpus)
- Q4 (small business): 0.293 — consulting/insight

---

## Phase 4 — Demo Frontend
Status: **complete**

Stack: React 19 + Vite 7 + TypeScript + D3 v7

Files:
- `src/types.ts` — GraphNode, GraphLink, SearchResult, ChatMessage
- `src/api.ts` — fetchGraph(), fetchNode(), search(), streamChat()
- `src/App.tsx` — Two-panel layout, highlight state management, adjacency map
- `src/components/ForceGraph.tsx` — D3 force simulation, zoom/pan, drag, tooltip, highlight transitions
- `src/components/ChatPanel.tsx` — Streaming chat, starter questions, source badges
- `src/components/Legend.tsx` — Domain color legend

Build: clean (267KB bundle, 86KB gzip)
npm run build: PASS

---

## Phase 5 — Integration + Polish
Status: **complete**

- API server confirmed live: /graph (125 nodes, 152 links), /search (VBOD query: 0.663), /chat (SSE streaming)
- Mobile responsive layout: panels stack vertically below 768px
- Final build: clean (267KB JS, 86KB gzip, 0 TS errors)
- README.md with run instructions written

## Summary
All 5 phases complete. Demo is ready to run:
1. `python api/query.py --serve` → localhost:8000
2. `npm run dev` → localhost:5173
