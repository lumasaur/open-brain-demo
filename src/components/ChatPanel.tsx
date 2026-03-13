import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, SearchResult } from "../types";
import { search, streamChat } from "../api";

const STARTERS = [
  "How would I build my own memory layer?",
  "Walk me through a decision this system influenced",
  "How could this help a small business stay organized?",
  "What's the VBOD and how does it change decisions?",
];

// Rotating pool shown after each assistant response
const FOLLOW_UP_POOL = [
  // Architecture & retrieval
  "How does graph structure improve retrieval?",
  "How does the 70/30 hybrid search blend vector and text?",
  "Why store embeddings locally instead of using a cloud vector DB?",
  "How does FTS5 keyword search complement the vector similarity?",
  "What's the role of the memory graph — why link nodes at all?",
  // Comparison & differentiation
  "What makes this different from a notes app like Notion?",
  "How is this different from RAG on a document store?",
  "Could this replace a CRM for a solo consultant?",
  "Why not just use ChatGPT memory or Claude Projects?",
  // Design decisions
  "What happens when two memories contradict each other?",
  "How do you decide what's worth storing?",
  "What would you add if you rebuilt this from scratch?",
  "What's the hardest part of building persistent AI memory?",
  "How do you prevent the memory store from getting noisy over time?",
  // Practical use & workflow
  "Walk me through how the VBOD personas work together",
  "How does decision logging change the way you work?",
  "What does a typical week look like using this system?",
  "How would you scale this to a whole team?",
  "What kind of person would benefit most from this system?",
  // Technical depth
  "How are the embeddings generated and why all-MiniLM-L6-v2?",
  "What does the SQLite schema look like under the hood?",
  "How does the streaming chat endpoint work?",
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
  onHighlight?: (ids: number[]) => void;
  onClear: () => void;
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

function FollowUpChip({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: "transparent",
        border: "1px solid #334155",
        borderRadius: "20px",
        color: "#64748b",
        padding: "4px 10px",
        fontSize: "11px",
        cursor: "pointer",
        whiteSpace: "nowrap",
        transition: "all 0.15s",
        flexShrink: 0,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "#6366f1";
        e.currentTarget.style.color = "#a5b4fc";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "#334155";
        e.currentTarget.style.color = "#64748b";
      }}
    >
      {label}
    </button>
  );
}

function pickFollowUps(used: Set<string>, count = 3): string[] {
  const available = FOLLOW_UP_POOL.filter((q) => !used.has(q));
  const pool = available.length >= count ? available : FOLLOW_UP_POOL;
  const shuffled = [...pool].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

export default function ChatPanel({ onResults, onHighlight, onClear }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [usedQuestions, setUsedQuestions] = useState<Set<string>>(new Set(STARTERS));
  const [followUps, setFollowUps] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, followUps]);

  const buildContext = useCallback((results: SearchResult[]): string => {
    return results
      .map((r, i) => `[${i + 1}] (${r.domain}/${r.intent}) ${r.content}`)
      .join("\n\n");
  }, []);

  const send = useCallback(async (query: string) => {
    if (!query.trim() || loading) return;
    setInput("");
    setLoading(true);
    setFollowUps([]); // Clear follow-ups while streaming

    const nextUsed = new Set([...usedQuestions, query]);
    setUsedQuestions(nextUsed);
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      const results: SearchResult[] = await search(query, 5);
      onResults(results);
      const context = buildContext(results);
      const nodeIds = results.map((r) => r.id);

      let assistantContent = "";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "", sources: results },
      ]);

      await streamChat(
        query,
        context,
        nodeIds,
        (chunk) => {
          assistantContent += chunk;
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              updated[updated.length - 1] = { ...last, content: assistantContent };
            }
            return updated;
          });
        },
        onHighlight,
        abortRef.current?.signal
      );

      // Show follow-ups after response completes
      setFollowUps(pickFollowUps(nextUsed));
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

  const handleClear = useCallback(() => {
    setMessages([]);
    setFollowUps([]);
    setUsedQuestions(new Set(STARTERS));
    onResults([]);
    onClear();
  }, [onResults, onClear]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  const hasMessages = messages.length > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#111827" }}>
      {/* Header */}
      <div style={{
        padding: "16px 20px",
        borderBottom: "1px solid #1e293b",
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
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

        {hasMessages && (
          <button
            onClick={handleClear}
            style={{
              background: "transparent",
              border: "none",
              color: "#475569",
              fontSize: "12px",
              cursor: "pointer",
              padding: "4px 8px",
              borderRadius: "4px",
              transition: "color 0.15s",
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "#94a3b8"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "#475569"; }}
          >
            Clear
          </button>
        )}
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
        {!hasMessages && (
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

        {/* Follow-up suggestions — shown after last response completes */}
        {followUps.length > 0 && !loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", paddingTop: "4px" }}>
            <span style={{ color: "#475569", fontSize: "11px" }}>Keep exploring:</span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {followUps.map((q) => (
                <FollowUpChip key={q} label={q} onClick={() => send(q)} />
              ))}
            </div>
          </div>
        )}

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
