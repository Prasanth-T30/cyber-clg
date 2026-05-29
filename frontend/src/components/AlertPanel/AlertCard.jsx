import { SEVERITY_COLORS, attackIcon, formatTime } from "@/utils/helpers";
import { CheckCircle, Clock } from "lucide-react";

export default function AlertCard({ alert, onAcknowledge }) {
  const sev    = alert.severity || "low";
  const icon   = attackIcon(alert.attack_type);
  const isAcked = alert.status === "acknowledged";

  const borderColor = {
    critical: "border-l-red-500",
    high:     "border-l-orange-500",
    medium:   "border-l-yellow-400",
    low:      "border-l-blue-400",
  }[sev] || "border-l-gray-400";

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 border-l-4 ${borderColor} rounded-lg p-4 flex items-start justify-between gap-3 hover:shadow-md dark:hover:shadow-none transition-shadow animate-slide-in ${isAcked ? "opacity-60" : ""}`}>
      <div className="flex items-start gap-3 min-w-0">
        <span className="text-xl leading-none mt-0.5 shrink-0">{icon}</span>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-gray-900 dark:text-white font-semibold text-sm">{alert.attack_type || "Unknown"}</span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${SEVERITY_COLORS[sev]}`}>
              {sev}
            </span>
            {isAcked && (
              <span className="text-[10px] text-green-600 dark:text-green-400 font-medium">✓ Acknowledged</span>
            )}
          </div>
          <p className="text-gray-500 dark:text-gray-400 text-xs mt-1 font-mono truncate">
            {alert.src_ip} → {alert.dst_ip}
          </p>
          {alert.details && (
            <p className="text-gray-400 dark:text-gray-500 text-xs mt-0.5 truncate">{alert.details}</p>
          )}
        </div>
      </div>

      <div className="flex flex-col items-end gap-2 shrink-0">
        <div className="flex items-center gap-1 text-gray-400 dark:text-gray-500 text-[11px]">
          <Clock size={11} />
          {formatTime(alert.timestamp)}
        </div>
        <span className="text-brand-500 dark:text-brand-400 text-xs font-mono font-bold">
          {(alert.confidence * 100).toFixed(0)}%
        </span>
        {!isAcked && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="text-gray-400 hover:text-green-500 transition-colors"
            title="Mark as acknowledged"
          >
            <CheckCircle size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
