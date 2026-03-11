// Shared types for Open Brain demo

export interface GraphNode {
  id: number;
  label: string;
  domain: string;
  degree: number;
  // D3 simulation adds these
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphLink {
  source: number | GraphNode;
  target: number | GraphNode;
  link_type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface SearchResult {
  id: number;
  content: string;
  domain: string;
  intent: string;
  source_file: string;
  relevance_score: number;
  linked_node_ids: number[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SearchResult[];
}
