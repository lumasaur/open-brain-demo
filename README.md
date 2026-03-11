# Open Brain — Portfolio Demo

Interactive visualization of a persistent AI memory system.
Two-panel layout: D3 force graph (125 nodes, 152 links) + AI chatbot grounded in retrieved memory.

## Quick Start

### 1. API Server (terminal 1)
```bash
cd C:/GitHub/open-brain-demo
python api/query.py --serve
# → http://localhost:8000
```
Requires: `pip install -r requirements.txt` and `ANTHROPIC_API_KEY` in environment.

### 2. Frontend Dev Server (terminal 2)
```bash
cd C:/GitHub/open-brain-demo
npm install
npm run dev
# → http://localhost:5173
```

## Architecture

```
open-brain-demo/
├── api/
│   ├── seed_demo.py     # Seeds 125 nodes with all-MiniLM-L6-v2 embeddings
│   ├── wire_links.py    # Wires 152 graph links + degree audit
│   └── query.py         # Retrieval API + FastAPI server + /chat streaming
├── data/
│   ├── ob_demo.db       # SQLite: memory_nodes + memory_links (125 nodes, 152 links)
│   ├── node_id_map.json # Label → DB ID map
│   └── degree_audit.json
├── src/
│   ├── types.ts         # GraphNode, GraphLink, SearchResult, ChatMessage
│   ├── api.ts           # Frontend API client
│   ├── App.tsx          # Two-panel layout orchestrator
│   └── components/
│       ├── ForceGraph.tsx  # D3 v7 force simulation
│       ├── ChatPanel.tsx   # Streaming chatbot with source badges
│       └── Legend.tsx      # Domain color legend
└── requirements.txt
```

## Graph Interaction
- **Hover** node → tooltip with domain + content preview
- **Click** node → highlights node + its direct neighbors
- **Drag** node → pins position (releases on drop)
- **Scroll** → zoom; **drag background** → pan
- **Chat query** → highlights top-5 retrieved nodes + neighbors

## Clusters
| Color | Domain | Hub |
|-------|--------|-----|
| Indigo | Meta | M1 |
| Cyan | Technical | T1 |
| Emerald | Consulting | CON1 |
| Amber | VBOD | V1 |
| Pink | Portfolio | PORT1 |
