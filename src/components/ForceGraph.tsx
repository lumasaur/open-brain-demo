import { useEffect, useRef, useCallback } from "react";
import * as d3 from "d3";
import type { GraphData, GraphNode, GraphLink } from "../types";

interface Props {
  data: GraphData;
  highlightIds: Set<number>;
  connectedIds: Set<number>;
  filterDomain: string | null;
  onNodeClick: (node: GraphNode) => void;
}

const DOMAIN_COLORS: Record<string, string> = {
  meta: "#6366f1",        // indigo
  technical: "#06b6d4",   // cyan
  consulting: "#10b981",  // emerald
  vbod: "#f59e0b",        // amber
  portfolio: "#ec4899",   // pink
  personal: "#8b5cf6",    // violet
};

function domainColor(d: string): string {
  return DOMAIN_COLORS[d] ?? "#94a3b8";
}

function nodeRadius(degree: number): number {
  return Math.max(4, Math.min(14, 4 + degree * 0.7));
}

export default function ForceGraph({ data, highlightIds, connectedIds, filterDomain, onNodeClick }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  const handleClick = useCallback((node: GraphNode) => {
    onNodeClick(node);
  }, [onNodeClick]);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth || 800;
    const height = svgRef.current.clientHeight || 600;

    svg.selectAll("*").remove();

    // Zoom container
    const g = svg.append("g");

    svg.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {
          g.attr("transform", event.transform);
        })
    );

    // Deep-copy nodes/links for simulation (D3 mutates them)
    const nodes: GraphNode[] = data.nodes.map((n) => ({ ...n }));
    const nodeById = new Map(nodes.map((n) => [n.id, n]));

    const links: GraphLink[] = data.links.map((l) => ({
      ...l,
      source: nodeById.get(l.source as number) ?? l.source,
      target: nodeById.get(l.target as number) ?? l.target,
    }));

    // Links layer
    const linkSel = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#334155")
      .attr("stroke-width", 0.8)
      .attr("stroke-opacity", 0.5);

    // Nodes layer
    const nodeSel = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (d) => nodeRadius(d.degree))
      .attr("fill", (d) => domainColor(d.domain))
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 0.8)
      .style("cursor", "pointer")
      .on("click", (_event, d) => handleClick(d))
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on("start", (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any);

    // Tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "ob-tooltip")
      .style("position", "fixed")
      .style("pointerEvents", "none")
      .style("background", "#1e293b")
      .style("color", "#e2e8f0")
      .style("padding", "8px 12px")
      .style("borderRadius", "6px")
      .style("fontSize", "12px")
      .style("maxWidth", "240px")
      .style("lineHeight", "1.4")
      .style("zIndex", "9999")
      .style("opacity", "0")
      .style("transition", "opacity 0.15s");

    nodeSel
      .on("mouseenter", (_, d) => {
        tooltip
          .style("opacity", "1")
          .html(`<strong>${d.domain}</strong><br/>${d.label.slice(0, 120)}`);
      })
      .on("mousemove", (event) => {
        tooltip
          .style("left", `${event.clientX + 14}px`)
          .style("top", `${event.clientY - 10}px`);
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", "0");
      });

    // Force simulation
    const sim = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links).id((d) => d.id).distance(60).strength(0.4))
      .force("charge", d3.forceManyBody().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide<GraphNode>().radius((d) => nodeRadius(d.degree) + 2));

    simRef.current = sim;

    sim.on("tick", () => {
      linkSel
        .attr("x1", (d) => (d.source as GraphNode).x ?? 0)
        .attr("y1", (d) => (d.source as GraphNode).y ?? 0)
        .attr("x2", (d) => (d.target as GraphNode).x ?? 0)
        .attr("y2", (d) => (d.target as GraphNode).y ?? 0);

      nodeSel
        .attr("cx", (d) => d.x ?? 0)
        .attr("cy", (d) => d.y ?? 0);
    });

    return () => {
      sim.stop();
      tooltip.remove();
    };
  }, [data, handleClick]);

  // Highlight + domain filter effect — separate from layout to avoid re-simulation
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const anyHighlight = highlightIds.size > 0;

    svg.selectAll<SVGCircleElement, GraphNode>("circle")
      .transition()
      .duration(300)
      .attr("opacity", (d) => {
        const matchesDomain = filterDomain === null || d.domain === filterDomain;
        if (anyHighlight) {
          if (highlightIds.has(d.id)) return 1;
          if (connectedIds.has(d.id)) return matchesDomain ? 0.5 : 0.15;
          return matchesDomain ? 0.15 : 0.05;
        }
        return matchesDomain ? 1 : 0.1;
      })
      .attr("stroke-width", (d) => highlightIds.has(d.id) ? 2.5 : 0.8)
      .attr("stroke", (d) => highlightIds.has(d.id) ? "#ffffff" : "#0f172a");

    svg.selectAll<SVGLineElement, GraphLink>("line")
      .transition()
      .duration(300)
      .attr("stroke-opacity", () => anyHighlight ? 0.15 : 0.5);
  }, [highlightIds, connectedIds, filterDomain]);

  return (
    <svg
      ref={svgRef}
      style={{ width: "100%", height: "100%", background: "#0f172a" }}
    />
  );
}
