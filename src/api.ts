// API client — reads VITE_API_URL env var; falls back to localhost:8000 for local dev

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchGraph() {
  const res = await fetch(`${BASE}/graph`);
  if (!res.ok) throw new Error("Failed to fetch graph data");
  return res.json();
}

export async function fetchNode(id: number) {
  const res = await fetch(`${BASE}/node/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch node ${id}`);
  return res.json();
}

export async function search(query: string, limit = 5) {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error("Search failed");
  const data = await res.json();
  return data.results;
}

export async function streamChat(
  query: string,
  context: string,
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, context }),
    signal,
  });

  if (!res.ok) throw new Error("Chat request failed");

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    // Parse SSE lines: "data: <text>\n\n"
    for (const line of chunk.split("\n")) {
      if (line.startsWith("data: ")) {
        const text = line.slice(6);
        if (text !== "[DONE]") onChunk(text);
      }
    }
  }
}
