"""
Link wiring script for Open Brain demo database.
Reads node_id_map.json to resolve spec labels → real DB IDs, then inserts all links.
Run AFTER seed_demo.py.
Usage: python wire_links.py
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ob_demo.db")
MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "node_id_map.json")
AUDIT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "degree_audit.json")

# ---------------------------------------------------------------------------
# ALL LINKS — ordered by priority per spec:
# 1. Cross-cluster bridges (15)
# 2. Hub node links (M1, T1, CON1, V1, PORT1)
# 3. Sub-hub links
# 4. Remaining intra-cluster links
# ---------------------------------------------------------------------------

LINKS = [
    # ── PRIORITY 1: CROSS-CLUSTER BRIDGES (15) ───────────────────────────
    ("M4",    "V9",     "related"),    # Synthesis value ↔ decision logging
    ("M5",    "T3",     "related"),    # Cross-tool capability ↔ cross-tool journey
    ("M19",   "PORT15", "related"),    # The demo ↔ Open Brain origin story
    ("T2",    "M3",     "related"),    # Vector embeddings ↔ how nodes work
    ("T3",    "V24",    "related"),    # MCP cross-tool ↔ skills as callable processes
    ("T7",    "T3",     "related"),    # Always-on deployment ↔ cross-tool journey
    ("CON1",  "PORT22", "related"),    # Sushi Media as lab ↔ why build your own
    ("CON2",  "PORT6",  "related"),    # SMB adoption ↔ enterprise taught about building
    ("CON20", "PORT22", "related"),    # Lab lessons ↔ building under constraint
    ("V1",    "PORT5",  "related"),    # VBOD concept ↔ rarest combination
    ("V3",    "M4",     "related"),    # Decision logging → synthesis
    ("V9",    "M7",     "related"),    # Decision logging ↔ graph as map of thinking
    ("PORT3", "CON1",   "related"),    # Why pharma ↔ Sushi Media lab
    ("PORT5", "T1",     "related"),    # Rarest combination ↔ local-first architecture
    ("PORT22","T11",    "related"),    # Why build your own ↔ what failed first

    # ── PRIORITY 2: META CLUSTER LINKS ──────────────────────────────────
    ("M1",  "M2",  "related"),
    ("M1",  "M3",  "related"),
    ("M1",  "M5",  "related"),
    ("M1",  "M6",  "related"),
    ("M1",  "M19", "related"),
    ("M2",  "M8",  "related"),
    ("M2",  "M21", "related"),
    ("M3",  "M9",  "related"),
    ("M3",  "M11", "related"),
    ("M3",  "M15", "related"),
    ("M3",  "M22", "related"),
    ("M4",  "M10", "derived_from"),
    ("M4",  "M24", "related"),
    ("M5",  "M16", "related"),
    ("M6",  "M18", "related"),
    ("M7",  "M12", "related"),
    ("M7",  "M24", "related"),
    ("M9",  "M17", "related"),
    ("M10", "M12", "related"),
    ("M13", "M7",  "related"),
    ("M13", "M23", "related"),
    ("M14", "M8",  "related"),
    ("M19", "M4",  "related"),
    ("M20", "M18", "related"),
    ("M25", "M23", "related"),

    # ── PRIORITY 3: TECHNICAL CLUSTER LINKS ─────────────────────────────
    ("T1",  "T2",  "related"),
    ("T1",  "T6",  "related"),
    ("T1",  "T7",  "related"),
    ("T1",  "T15", "related"),
    ("T2",  "T8",  "related"),
    ("T2",  "T10", "related"),
    ("T2",  "T13", "related"),
    ("T3",  "T12", "supersedes"),
    ("T3",  "T14", "related"),
    ("T3",  "T16", "related"),
    ("T4",  "T11", "related"),
    ("T5",  "T11", "related"),
    ("T5",  "T22", "related"),
    ("T6",  "T9",  "related"),
    ("T6",  "T23", "related"),
    ("T6",  "T24", "related"),
    ("T7",  "T15", "related"),
    ("T8",  "T10", "related"),
    ("T8",  "T17", "related"),
    ("T9",  "T23", "related"),
    ("T13", "T15", "related"),
    ("T14", "T16", "related"),
    ("T18", "T16", "related"),
    ("T19", "T17", "related"),
    ("T21", "T22", "related"),

    # ── PRIORITY 4: CONSULTING CLUSTER LINKS ─────────────────────────────
    ("CON1",  "CON2",  "related"),
    ("CON1",  "CON8",  "related"),
    ("CON1",  "CON15", "related"),
    ("CON1",  "CON20", "related"),
    ("CON1",  "CON25", "related"),
    ("CON2",  "CON9",  "related"),
    ("CON2",  "CON17", "related"),
    ("CON3",  "CON10", "related"),
    ("CON3",  "CON19", "related"),
    ("CON4",  "CON11", "related"),
    ("CON4",  "CON8",  "related"),
    ("CON5",  "CON7",  "related"),
    ("CON5",  "CON3",  "related"),
    ("CON6",  "CON18", "related"),
    ("CON6",  "CON4",  "related"),
    ("CON7",  "CON5",  "related"),
    ("CON8",  "CON9",  "related"),
    ("CON8",  "CON22", "related"),
    ("CON9",  "CON21", "related"),
    ("CON10", "CON24", "related"),
    ("CON12", "CON9",  "related"),
    ("CON13", "CON23", "related"),
    ("CON15", "CON16", "related"),
    ("CON15", "CON22", "related"),
    ("CON20", "CON21", "related"),

    # ── PRIORITY 5: VBOD CLUSTER LINKS ──────────────────────────────────
    ("V1",  "V2",  "related"),
    ("V1",  "V3",  "related"),
    ("V1",  "V7",  "related"),
    ("V1",  "V8",  "related"),
    ("V1",  "V20", "related"),
    ("V1",  "V21", "related"),
    ("V2",  "V8",  "related"),
    ("V2",  "V13", "related"),
    ("V3",  "V4",  "related"),
    ("V4",  "V5",  "related"),
    ("V5",  "V6",  "related"),
    ("V7",  "V16", "related"),
    ("V8",  "V14", "related"),
    ("V9",  "V22", "related"),
    ("V9",  "V15", "related"),
    ("V10", "V11", "related"),
    ("V10", "V12", "related"),
    ("V12", "V13", "related"),
    ("V14", "V19", "related"),
    ("V15", "V18", "related"),
    ("V16", "V22", "related"),
    ("V17", "V23", "related"),
    ("V20", "V24", "related"),
    ("V24", "V25", "related"),
    ("V25", "V9",  "related"),

    # ── PRIORITY 6: PORTFOLIO CLUSTER LINKS ─────────────────────────────
    ("PORT1",  "PORT2",  "related"),
    ("PORT1",  "PORT3",  "related"),
    ("PORT1",  "PORT5",  "related"),
    ("PORT1",  "PORT6",  "related"),
    ("PORT1",  "PORT22", "related"),
    ("PORT2",  "PORT3",  "related"),
    ("PORT3",  "PORT23", "related"),
    ("PORT4",  "PORT12", "related"),
    ("PORT4",  "PORT18", "related"),
    ("PORT5",  "PORT9",  "related"),
    ("PORT6",  "PORT11", "related"),
    ("PORT7",  "PORT22", "related"),
    ("PORT8",  "PORT10", "related"),
    ("PORT8",  "PORT24", "related"),
    ("PORT9",  "PORT22", "related"),
    ("PORT10", "PORT17", "related"),
    ("PORT11", "PORT14", "related"),
    ("PORT12", "PORT18", "related"),
    ("PORT13", "PORT4",  "related"),
    ("PORT15", "PORT22", "related"),
    ("PORT15", "PORT21", "related"),
    ("PORT16", "PORT22", "related"),
    ("PORT19", "PORT3",  "related"),
    ("PORT21", "PORT7",  "related"),
    ("PORT25", "PORT8",  "related"),
]

# ---------------------------------------------------------------------------
# HUB CLASSIFICATION — for degree audit
# ---------------------------------------------------------------------------

HUB_LABELS = {"M1", "T1", "CON1", "V1", "PORT1"}
SUB_HUB_LABELS = {
    "M2", "M4", "M5", "M6", "M13", "M19",
    "T2", "T3", "T8", "T15",
    "CON2", "CON8", "CON15", "CON20",
    "V2", "V9", "V14", "V20",
    "PORT3", "PORT8", "PORT15", "PORT22",
}


def wire(db_path, map_path, audit_path):
    # Load ID map
    with open(map_path) as f:
        id_map = json.load(f)

    conn = sqlite3.connect(db_path)
    now = datetime.utcnow().isoformat()
    inserted = 0
    skipped = 0
    errors = []

    print(f"Wiring {len(LINKS)} links...")
    for from_label, to_label, link_type in LINKS:
        from_id = id_map.get(from_label)
        to_id = id_map.get(to_label)

        if from_id is None or to_id is None:
            errors.append(f"  MISSING: {from_label} → {to_label} (label not in map)")
            continue

        # Check for existing
        existing = conn.execute(
            "SELECT id FROM memory_links WHERE from_id=? AND to_id=? AND link_type=?",
            (from_id, to_id, link_type),
        ).fetchone()
        if existing:
            skipped += 1
            continue

        conn.execute(
            "INSERT INTO memory_links (from_id, to_id, link_type, created_at) VALUES (?, ?, ?, ?)",
            (from_id, to_id, link_type, now),
        )
        inserted += 1

    conn.commit()

    # ── DEGREE AUDIT ─────────────────────────────────────────────────────
    print("\nRunning degree audit...")
    audit = []
    label_by_id = {v: k for k, v in id_map.items()}

    all_node_ids = conn.execute("SELECT id FROM memory_nodes").fetchall()
    for (node_id,) in all_node_ids:
        # Count undirected degree (both from and to)
        out_deg = conn.execute(
            "SELECT COUNT(*) FROM memory_links WHERE from_id=?", (node_id,)
        ).fetchone()[0]
        in_deg = conn.execute(
            "SELECT COUNT(*) FROM memory_links WHERE to_id=?", (node_id,)
        ).fetchone()[0]
        degree = out_deg + in_deg

        label = label_by_id.get(node_id, f"id:{node_id}")

        if label in HUB_LABELS:
            classification = "hub"
        elif label in SUB_HUB_LABELS:
            classification = "sub-hub"
        else:
            classification = "leaf"

        audit.append({
            "node_label": label,
            "db_id": node_id,
            "degree": degree,
            "hub_classification": classification,
        })

    # Sort by degree descending
    audit.sort(key=lambda x: x["degree"], reverse=True)

    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2)

    conn.close()

    print(f"\n✓ Links wired: {inserted} inserted, {skipped} skipped (duplicates)")
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(e)

    # Print degree summary
    hubs = [a for a in audit if a["hub_classification"] == "hub"]
    sub_hubs = [a for a in audit if a["hub_classification"] == "sub-hub"]
    leaves = [a for a in audit if a["hub_classification"] == "leaf"]

    print(f"\n── Degree Audit Summary ──────────────────────")
    hub_summary = ["{0}({1})".format(a['node_label'], a['degree']) for a in hubs]
    print(f"  Hubs     ({len(hubs)}):    {hub_summary}")
    sub_avg = sum(a['degree'] for a in sub_hubs)/max(len(sub_hubs),1)
    leaf_avg = sum(a['degree'] for a in leaves)/max(len(leaves),1)
    print(f"  Sub-hubs ({len(sub_hubs)}): avg degree = {sub_avg:.1f}")
    print(f"  Leaves   ({len(leaves)}):  avg degree = {leaf_avg:.1f}")
    print(f"\n✓ degree_audit.json saved to: {audit_path}")

    # Warn if any hub node has degree < 8
    low_hubs = [a for a in hubs if a["degree"] < 8]
    if low_hubs:
        print(f"\n⚠ Hub nodes with degree < 8 (target 8-12):")
        for a in low_hubs:
            print(f"   {a['node_label']}: degree {a['degree']}")

    low_sub = [a for a in sub_hubs if a["degree"] < 4]
    if low_sub:
        print(f"\n⚠ Sub-hub nodes with degree < 4 (target 4-6):")
        for a in low_sub:
            print(f"   {a['node_label']}: degree {a['degree']}")


if __name__ == "__main__":
    wire(DB_PATH, MAP_PATH, AUDIT_PATH)
