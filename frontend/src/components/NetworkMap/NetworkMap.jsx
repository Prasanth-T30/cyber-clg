import { useEffect, useRef } from "react";
import { useAlertsContext } from "@/contexts/AlertsContext";
import { useTheme } from "@/contexts/ThemeContext";

export default function NetworkMap() {
  const canvasRef = useRef(null);
  const { alerts, lastEvent } = useAlertsContext();
  const { isDark } = useTheme();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width  = canvas.offsetWidth;
    const H = canvas.height = canvas.offsetHeight;

    const bg     = isDark ? "#111827" : "#f8fafc";
    const grid   = isDark ? "#1f2937" : "#e5e7eb";
    const center = isDark ? "#0891b2" : "#0891b2";
    const txt    = isDark ? "#d1d5db" : "#374151";

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = grid;
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    const cx = W / 2, cy = H / 2;

    // Server node glow
    const grad = ctx.createRadialGradient(cx, cy, 10, cx, cy, 40);
    grad.addColorStop(0, center + "40");
    grad.addColorStop(1, "transparent");
    ctx.fillStyle = grad;
    ctx.fillRect(cx - 40, cy - 40, 80, 80);

    ctx.beginPath();
    ctx.arc(cx, cy, 22, 0, Math.PI * 2);
    ctx.fillStyle = center;
    ctx.fill();

    ctx.font = "bold 8px monospace";
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.fillText("SERVER", cx, cy + 3);

    const uniqueIPs = [...new Set(alerts.slice(0, 18).map(a => a.src_ip).filter(Boolean))];
    const angleStep = (2 * Math.PI) / Math.max(uniqueIPs.length, 1);
    const radius    = Math.min(W, H) * 0.32;

    const sevColors = { critical: "#ef4444", high: "#f97316", medium: "#facc15", low: "#60a5fa" };

    uniqueIPs.forEach((ip, i) => {
      const angle = angleStep * i - Math.PI / 2;
      const x     = cx + radius * Math.cos(angle);
      const y     = cy + radius * Math.sin(angle);
      const topAlert = alerts.find(a => a.src_ip === ip);
      const sev      = topAlert?.severity || "low";
      const lineColor = sevColors[sev] || "#60a5fa";

      // Animated dashed line
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(cx, cy);
      ctx.strokeStyle = lineColor + "70";
      ctx.lineWidth   = sev === "critical" ? 2 : 1;
      ctx.stroke();
      ctx.setLineDash([]);

      // IP node
      const nodeGrad = ctx.createRadialGradient(x, y, 2, x, y, 10);
      nodeGrad.addColorStop(0, lineColor);
      nodeGrad.addColorStop(1, lineColor + "00");
      ctx.fillStyle = nodeGrad;
      ctx.fillRect(x - 10, y - 10, 20, 20);

      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fillStyle = lineColor;
      ctx.fill();
      ctx.strokeStyle = bg;
      ctx.lineWidth = 2;
      ctx.stroke();

      // IP label
      ctx.fillStyle  = txt;
      ctx.font       = "9px monospace";
      ctx.textAlign  = "center";
      ctx.fillText(ip.split(".").slice(-2).join("."), x, y - 14);
    });

    if (uniqueIPs.length === 0) {
      ctx.fillStyle = isDark ? "#4b5563" : "#9ca3af";
      ctx.font      = "13px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Monitoring network traffic…", cx, cy + 52);
    }
  }, [alerts, lastEvent, isDark]);

  const uniqueIPs = [...new Set(alerts.map(a => a.src_ip).filter(Boolean))].length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="page-title">Network Map</h2>
        <span className="text-xs text-gray-500 dark:text-gray-400">{uniqueIPs} source IPs</span>
      </div>
      <div className="card overflow-hidden" style={{ height: 340 }}>
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
    </div>
  );
}
