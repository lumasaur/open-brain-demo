import { useState, useEffect, useCallback, useMemo } from "react";
import ForceGraph from "./components/ForceGraph";
import ChatPanel from "./components/ChatPanel";
import Legend from "./components/Legend";
import { fetchGraph } from "./api";
import type { GraphData, GraphNode, SearchResult } from "./types";

export default function App() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightIds, setHighlightIds] = useState<Set<number>>(new Set());
  const [connectedIds, setConnectedIds] = useState<Set<number>>(new Set());
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    fetchGraph()
      .then((data: GraphData) => {
        setGraphData(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message + " — is the API server running? (python api/query.py --serve)");
        setLoading(false);
      });
  }, []);

  const adjacencyMap = useMemo(() => {
    const map = new Map<number, Set<number>>();
    for (const link of graphData.links) {
      const s = typeof link.source === "object" ? (link.source as GraphNode).id : link.source as number;
      const t = typeof link.target === "object" ? (link.target as GraphNode).id : link.target as number;
      if (!map.has(s)) map.set(s, new Set());
      if (!map.has(t)) map.set(t, new Set());
      map.get(s)!.add(t);
      map.get(t)!.add(s);
    }
    return map;
  }, [graphData.links]);

  const handleResults = useCallback((results: SearchResult[]) => {
    const ids = new Set(results.map((r) => r.id));
    setHighlightIds(ids);
    const connected = new Set<number>();
    for (const id of ids) {
      const neighbors = adjacencyMap.get(id);
      if (neighbors) {
        for (const n of neighbors) {
          if (!ids.has(n)) connected.add(n);
        }
      }
    }
    setConnectedIds(connected);
    setSelectedNode(null);
  }, [adjacencyMap]);

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    setHighlightIds(new Set([node.id]));
    const connected = adjacencyMap.get(node.id) ?? new Set<number>();
    setConnectedIds(new Set(connected));
  }, [adjacencyMap]);

  const handleClearHighlight = useCallback(() => {
    setHighlightIds(new Set());
    setConnectedIds(new Set());
    setSelectedNode(null);
  }, []);

  // Responsive: stack panels on mobile
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;

  return (
    <div style={{
      display: "flex",
      flexDirection: isMobile ? "column" : "row",
      height: "100vh",
      width: "100vw",
      overflow: "hidden",
      background: "#0f172a",
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>
      {/* LEFT — Force Graph */}
      <div
        style={{
          flex: isMobile ? "0 0 50%" : "0 0 58%",
          position: "relative",
          overflow: "hidden",
        }}
        onClick={handleClearHighlight}
      >
        {loading && (
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center",
            color: "#64748b", fontSize: "14px",
          }}>
            Loading graph…
          </div>
        )}
        {error && (
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            flexDirection: "column",
            alignItems: "center", justifyContent: "center", padding: "32px",
            color: "#f87171", fontSize: "13px", textAlign: "center", gap: "12px",
          }}>
            <div style={{ fontSize: "24px" }}>!</div>
            {error}
          </div>
        )}
        {!loading && !error && (
          <ForceGraph
            data={graphData}
            highlightIds={highlightIds}
            connectedIds={connectedIds}
            onNodeClick={handleNodeClick}
          />
        )}

        <div style={{
          position: "absolute", top: "16px", left: "16px",
          color: "#94a3b8", fontSize: "12px", pointerEvents: "none",
        }}>
          <span style={{ color: "#e2e8f0", fontWeight: 600 }}>Memory Graph</span>
          {!loading && !error && (
            <span style={{ marginLeft: "8px" }}>
              {graphData.nodes.length} nodes · {graphData.links.length} links
            </span>
          )}
        </div>

        {selectedNode && (
          <div
            style={{
              position: "absolute", top: "16px", right: "16px",
              background: "#1e293bdd", backdropFilter: "blur(8px)",
              border: "1px solid #334155", borderRadius: "8px",
              padding: "12px 16px", maxWidth: "260px",
              color: "#e2e8f0", fontSize: "12px", lineHeight: "1.5",
              pointerEvents: "none",
            }}
          >
            <div style={{ color: "#94a3b8", fontSize: "11px", marginBottom: "4px" }}>
              {selectedNode.domain} · degree {selectedNode.degree}
            </div>
            <div>{selectedNode.label}</div>
          </div>
        )}

        <Legend />
      </div>

      {/* Divider */}
      <div style={{
        width: isMobile ? "100%" : "1px",
        height: isMobile ? "1px" : "100%",
        background: "#1e293b",
        flexShrink: 0,
      }} />

      {/* RIGHT — Chat */}
      <div style={{
        flex: isMobile ? "0 0 50%" : "0 0 42%",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
      }}>
        <ChatPanel onResults={handleResults} onClear={handleClearHighlight} />
      </div>
    </div>
  );
}
