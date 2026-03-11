import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, SearchResult } from "../types";
import { search, streamChat } from "../api";

const STARTERS = [
  "How would I build my own memory layer?",
  "Walk me through a decision this system influenced",
  "How could this help a small business stay organized?",
  "What's the VBOD and how does it change decisions?",
];

const DOMAIN_BADGE_COLORS: Record<string, string> = {
  meta: "#6366f1",
  technical: "#06b6d4",
  consulting: "#10b981",
  vbod: "#f59e0b",
  portfolio: "#ec4899",
  personal: "#8b5cf6",
};

interface Props {
  onResults: (results: SearchResult[]) => void;
}

function SourceBadge({ result }: { result: SearchResult }) {
  const color = DOMAIN_BADGE_COLORS[result.domain] ?? "#94a3b8";
  return (
    <span
      title={result.content}
      style={{
        display: "inline-block",
        background: color + "22",
        border: `1px solid ${color}55`,
        color,
        borderRadius: "4px",
        padding: "1px 6px",
        fontSize: "11px",
        marginRight: "4px",
        marginTop: "4px",
        cursor: "default",
      }}
    >
      {result.domain} · {(result.relevance_score * 100).toFixed(0)}%
    </span>
  );
}

export default function ChatPanel({ onResults }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const buildContext = useCallback((results: SearchResult[]): string => {
    return results
      .map((r, i) => `[${i + 1}] (${r.domain}/${r.intent}) ${r.content}`)
      .join("\n\n");
  }, []);

  const send = useCallback(async (query: string) => {
    if (!query.trim() || loading) return;
    setInput("");
    setLoading(true);

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      // Retrieve context
      const results: SearchResult[] = await search(query, 5);
      onResults(results);
      const context = buildContext(results);

      // Streaming assistant response
      let assistantContent = "";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "", sources: results },
      ]);

      await streamChat(
        query,
        context,
        (chunk) => {
          assistantContent += chunk;
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                content: assistantContent,
              };
            }
            return updated;
          });
        },
        abortRef.current?.signal
      );
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Something went wrong. Make sure the API server is running (`python api/query.py --serve`).",
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  }, [loading, buildContext, onResults]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#111827" }}>
      {/* Header */}
      <div style={{
        padding: "16px 20px",
        borderBottom: "1px solid #1e293b",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "8px", height: "8px", borderRadius: "50%",
            background: "#10b981", boxShadow: "0 0 6px #10b981",
          }} />
          <span style={{ color: "#e2e8f0", fontWeight: 600, fontSize: "15px" }}>
            Open Brain
          </span>
          <span style={{ color: "#64748b", fontSize: "12px" }}>
            125 nodes · hybrid retrieval
          </span>
        </div>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
      }}>
        {messages.length === 0 && (
          <div style={{ marginTop: "auto", paddingBottom: "24px" }}>
            <p style={{ color: "#64748b", fontSize: "13px", marginBottom: "12px", textAlign: "center" }}>
              Ask anything about this memory system
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {STARTERS.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  style={{
                    background: "#1e293b",
                    border: "1px solid #334155",
                    borderRadius: "8px",
                    color: "#94a3b8",
                    padding: "10px 14px",
                    textAlign: "left",
                    cursor: "pointer",
                    fontSize: "13px",
                    lineHeight: "1.4",
                    transition: "all 0.15s",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "#273549";
                    e.currentTarget.style.color = "#e2e8f0";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "#1e293b";
                    e.currentTarget.style.color = "#94a3b8";
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                maxWidth: "85%",
                background: msg.role === "user" ? "#1e40af" : "#1e293b",
                borderRadius: msg.role === "user" ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
                padding: "10px 14px",
                color: "#e2e8f0",
                fontSize: "13px",
                lineHeight: "1.6",
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.content}
              {msg.role === "assistant" && msg.content === "" && loading && (
                <span style={{ color: "#64748b" }}>▋</span>
              )}
            </div>
            {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
              <div style={{ maxWidth: "85%", marginTop: "6px" }}>
                <span style={{ color: "#475569", fontSize: "11px" }}>Sources: </span>
                {msg.sources.map((s) => (
                  <SourceBadge key={s.id} result={s} />
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: "16px 20px",
          borderTop: "1px solid #1e293b",
          display: "flex",
          gap: "8px",
          flexShrink: 0,
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about memory, decisions, architecture…"
          disabled={loading}
          style={{
            flex: 1,
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "8px",
            color: "#e2e8f0",
            padding: "10px 14px",
            fontSize: "13px",
            outline: "none",
          }}
          onFocus={(e) => { e.currentTarget.style.borderColor = "#6366f1"; }}
          onBlur={(e) => { e.currentTarget.style.borderColor = "#334155"; }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? "#1e293b" : "#6366f1",
            border: "none",
            borderRadius: "8px",
            color: loading || !input.trim() ? "#475569" : "#fff",
            padding: "10px 16px",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontSize: "13px",
            fontWeight: 600,
            transition: "background 0.15s",
          }}
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
