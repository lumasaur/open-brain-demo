const DOMAINS = [
  { label: "Meta", color: "#6366f1" },
  { label: "Technical", color: "#06b6d4" },
  { label: "Consulting", color: "#10b981" },
  { label: "VBOD", color: "#f59e0b" },
  { label: "Portfolio", color: "#ec4899" },
  { label: "Personal", color: "#8b5cf6" },
];

export default function Legend() {
  return (
    <div style={{
      position: "absolute",
      bottom: "16px",
      left: "16px",
      background: "#0f172acc",
      backdropFilter: "blur(8px)",
      border: "1px solid #1e293b",
      borderRadius: "8px",
      padding: "10px 14px",
      display: "flex",
      flexDirection: "column",
      gap: "5px",
    }}>
      {DOMAINS.map((d) => (
        <div key={d.label} style={{ display: "flex", alignItems: "center", gap: "7px" }}>
          <div style={{
            width: "9px", height: "9px", borderRadius: "50%",
            background: d.color, flexShrink: 0,
          }} />
          <span style={{ color: "#94a3b8", fontSize: "11px" }}>{d.label}</span>
        </div>
      ))}
      <div style={{ marginTop: "4px", color: "#475569", fontSize: "10px" }}>
        Node size = degree
      </div>
    </div>
  );
}
