import { useEffect, useState } from "react";
import { getStats, getTimeline } from "@/services/api";
import { ShieldCheck, ShieldX, Activity, Clock, TrendingUp, AlertTriangle } from "lucide-react";
import { attackIcon } from "@/utils/helpers";

function StatCard({ label, value, icon: Icon, color, trend }) {
  const colorMap = {
    red:    { bg: "bg-red-100 dark:bg-red-900/20",    text: "text-red-600 dark:text-red-400"    },
    orange: { bg: "bg-orange-100 dark:bg-orange-900/20", text: "text-orange-600 dark:text-orange-400" },
    cyan:   { bg: "bg-brand-50 dark:bg-brand-900/20",  text: "text-brand-600 dark:text-brand-400"   },
    green:  { bg: "bg-green-100 dark:bg-green-900/20", text: "text-green-600 dark:text-green-400"  },
  };
  const c = colorMap[color] || colorMap.cyan;

  return (
    <div className="card p-5 flex items-center gap-4 hover:shadow-md transition-shadow">
      <div className={`p-3 rounded-xl ${c.bg} ${c.text}`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value ?? <span className="text-gray-400">—</span>}</p>
      </div>
    </div>
  );
}

function MiniBar({ label, count, max }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  const lower = (label || "").toLowerCase();
  const barColor =
    lower.includes("flood") || lower.includes("ddos") || lower.includes("amplification") ? "bg-red-500" :
    lower.includes("scan")  || lower.includes("probe") || lower.includes("recon")        ? "bg-orange-500" :
    lower.includes("brute") || lower.includes("spray") || lower.includes("cred")         ? "bg-yellow-500" :
    lower.includes("trojan")|| lower.includes("malware")|| lower.includes("ransomware") ||
    lower.includes("botnet")|| lower.includes("worm")  || lower.includes("rat")          ? "bg-purple-500" :
    lower.includes("sql")   || lower.includes("inject") || lower.includes("blind")       ? "bg-pink-500"   :
    "bg-brand-500";

  return (
    <div className="flex items-center gap-3 py-1.5">
      <span className="text-gray-700 dark:text-gray-300 text-sm w-36 truncate">
        {attackIcon(label)} {label}
      </span>
      <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-2">
        <div
          className={`${barColor} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-gray-500 dark:text-gray-400 text-xs w-6 text-right font-mono">{count}</span>
    </div>
  );
}

export default function Dashboard() {
  const [stats,    setStats]    = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [error,    setError]    = useState(null);

  const load = async () => {
    try {
      setError(null);
      const [s, t] = await Promise.all([getStats(), getTimeline()]);
      setStats(s);
      setTimeline(t.timeline || []);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, []);

  const attackEntries = Object.entries(stats?.attack_breakdown || {});
  const maxCount      = Math.max(...attackEntries.map(([, v]) => v), 1);
  const maxTimeline   = Math.max(...timeline.map(x => x.count), 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="page-title">Overview</h2>
        {error && (
          <div className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 text-xs">
            <AlertTriangle size={13}/>
            <span>Backend connecting…</span>
          </div>
        )}
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Total Alerts"  value={stats?.total_alerts}    icon={ShieldX}     color="red"    />
        <StatCard label="Last 24 Hours" value={stats?.alerts_last_24h} icon={Clock}       color="orange" />
        <StatCard label="Active Now"    value={stats?.active_alerts}   icon={Activity}    color="cyan"   />
        <StatCard label="Packets Seen"  value={stats?.total_packets}   icon={ShieldCheck} color="green"  />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Attack breakdown */}
        <div className="card p-5">
          <h3 className="section-title mb-4">Attack Breakdown</h3>
          {attackEntries.length === 0 ? (
            <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500 text-sm py-4">
              <TrendingUp size={16}/>
              <span>Monitoring — no attacks detected yet</span>
            </div>
          ) : (
            <div className="space-y-0.5">
              {attackEntries.map(([k, v]) => <MiniBar key={k} label={k} count={v} max={maxCount} />)}
            </div>
          )}
        </div>

        {/* Timeline chart */}
        <div className="card p-5">
          <h3 className="section-title mb-4">Alert Timeline <span className="text-xs font-normal text-gray-400">(30 min)</span></h3>
          <div className="flex items-end gap-0.5 h-24">
            {timeline.slice(-30).map((b, i) => {
              const h = Math.round((b.count / maxTimeline) * 100);
              return (
                <div key={i} className="flex-1 flex flex-col justify-end group relative" title={`${b.label}: ${b.count}`}>
                  <div
                    className={`rounded-t transition-all duration-300 cursor-default ${b.count > 0 ? "bg-brand-500 hover:bg-brand-400" : "bg-gray-100 dark:bg-gray-700"}`}
                    style={{ height: `${Math.max(h, 4)}%` }}
                  />
                  {b.count > 0 && (
                    <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block bg-gray-800 text-white text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap z-10">
                      {b.count}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          <p className="text-gray-400 dark:text-gray-500 text-[11px] mt-2 text-right">← 30 min ago · now →</p>
        </div>
      </div>
    </div>
  );
}
