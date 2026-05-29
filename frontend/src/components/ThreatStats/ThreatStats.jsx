import { useEffect, useState } from "react";
import { getStats } from "@/services/api";
import { ATTACK_ICONS } from "@/utils/helpers";
import { RefreshCw } from "lucide-react";

const ATTACK_COLORS = {
  "DDoS":            "bg-red-500",
  "Port Scanning":   "bg-orange-500",
  "Brute Force":     "bg-yellow-500",
  "Malware Traffic": "bg-purple-500",
  "SQL Injection":   "bg-pink-500",
};

const SEV_CONFIG = [
  { key: "critical", bg: "bg-red-100 dark:bg-red-900/20",     dot: "bg-red-500",     text: "text-red-700 dark:text-red-400",     label: "Critical" },
  { key: "high",     bg: "bg-orange-100 dark:bg-orange-900/20",dot: "bg-orange-500",  text: "text-orange-700 dark:text-orange-400",label: "High"     },
  { key: "medium",   bg: "bg-yellow-100 dark:bg-yellow-900/20",dot: "bg-yellow-400",  text: "text-yellow-700 dark:text-yellow-400",label: "Medium"   },
  { key: "low",      bg: "bg-blue-100 dark:bg-blue-900/20",    dot: "bg-blue-400",    text: "text-blue-700 dark:text-blue-400",   label: "Low"      },
];

export default function ThreatStats() {
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try { setStats(await getStats()); } catch {} finally { setLoading(false); }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 6000);
    return () => clearInterval(id);
  }, []);

  const entries    = Object.entries(stats?.attack_breakdown || {});
  const totalAttacks = entries.reduce((s, [, v]) => s + v, 0);
  const sevBreakdown = stats?.severity_breakdown || {};

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="page-title">Threat Statistics</h2>
        <button onClick={load} disabled={loading} className="p-1.5 rounded-lg text-gray-400 hover:text-brand-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-40">
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Attack distribution */}
      <div className="card p-5">
        <h3 className="section-title mb-4">Attack Distribution</h3>
        {entries.length === 0 ? (
          <p className="text-gray-400 dark:text-gray-500 text-sm py-4">No attacks detected yet — monitoring…</p>
        ) : (
          <div className="space-y-4">
            {entries.map(([type, count]) => {
              const pct = totalAttacks > 0 ? Math.round((count / totalAttacks) * 100) : 0;
              return (
                <div key={type}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-gray-700 dark:text-gray-300 font-medium">
                      {ATTACK_ICONS[type] || "⚠️"} {type}
                    </span>
                    <span className="text-gray-500 dark:text-gray-400 font-mono">{count} <span className="text-xs">({pct}%)</span></span>
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`${ATTACK_COLORS[type] || "bg-brand-500"} h-2 rounded-full transition-all duration-700`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Severity breakdown */}
      <div className="card p-5">
        <h3 className="section-title mb-4">Severity Breakdown</h3>
        <div className="grid grid-cols-2 gap-3">
          {SEV_CONFIG.map(({ key, bg, dot, text, label }) => (
            <div key={key} className={`flex items-center gap-2.5 ${bg} rounded-xl px-4 py-3`}>
              <div className={`w-3 h-3 rounded-full ${dot} shrink-0`} />
              <div>
                <p className={`text-xs font-medium ${text}`}>{label}</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white tabular-nums">{sevBreakdown[key] || 0}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top attack */}
      {stats?.top_attack && (
        <div className="card p-4 flex items-center gap-3">
          <span className="text-2xl">{ATTACK_ICONS[stats.top_attack] || "⚠️"}</span>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide font-medium">Top Threat</p>
            <p className="font-bold text-gray-900 dark:text-white">{stats.top_attack}</p>
          </div>
        </div>
      )}
    </div>
  );
}
