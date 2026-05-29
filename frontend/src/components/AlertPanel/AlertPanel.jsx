import { useCallback, useState } from "react";
import AlertCard from "./AlertCard";
import { acknowledgeAlert } from "@/services/api";
import { useAlertsContext } from "@/contexts/AlertsContext";
import { Filter, Trash2, RefreshCw } from "lucide-react";

const ATTACK_TYPES = ["All", "DDoS", "Port Scan", "Brute Force", "Malware", "SQL Injection"];
const SEVERITIES   = ["All", "critical", "high", "medium", "low"];

export default function AlertPanel() {
  const { alerts, connected, clearAll } = useAlertsContext();
  const [typeFilter, setTypeFilter] = useState("All");
  const [sevFilter,  setSevFilter]  = useState("All");
  const [clearing,   setClearing]   = useState(false);

  const handleAck = useCallback(async (id) => {
    try { await acknowledgeAlert(id); } catch {}
  }, []);

  const handleClear = async () => {
    setClearing(true);
    try { await clearAll(); } finally { setClearing(false); }
  };

  // Map filter label → keywords that appear in realistic attack_type names
  const TYPE_KEYWORDS = {
    "DDoS":          ["flood","amplification","icmp","smurf","slowloris","volumetric","reflection","hijack","ddos"],
    "Port Scan":     ["scan","probe","reconnaissance","fingerprint","enumeration","nmap"],
    "Brute Force":   ["brute","spray","dictionary","credential","stuffing","pre-auth","kerberos"],
    "Malware":       ["trojan","ransomware","botnet","keylogger","rootkit","spyware","worm","rat","cryptominer","exfiltration","malware","c2","beacon"],
    "SQL Injection": ["sqli","sql","injection","union","blind","boolean","stacked","schema","credential dump"],
  };

  const filtered = alerts.filter(a => {
    if (typeFilter !== "All") {
      const kws = TYPE_KEYWORDS[typeFilter] || [];
      const name = (a.attack_type || "").toLowerCase();
      if (!kws.some(k => name.includes(k))) return false;
    }
    if (sevFilter !== "All" && a.severity !== sevFilter) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Alert Feed</h2>
          <span className={`inline-block w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-red-500"} animate-pulse`} />
        </div>
        <button
          onClick={handleClear}
          disabled={clearing || alerts.length === 0}
          className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 disabled:opacity-40 transition-colors"
        >
          {clearing ? <RefreshCw size={13} className="animate-spin"/> : <Trash2 size={13}/>}
          Clear all
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap items-center">
        <Filter size={13} className="text-gray-400" />
        <select
          value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
          className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          {ATTACK_TYPES.map(t => <option key={t}>{t}</option>)}
        </select>
        <select
          value={sevFilter} onChange={e => setSevFilter(e.target.value)}
          className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          {SEVERITIES.map(s => <option key={s}>{s}</option>)}
        </select>
        <span className="text-gray-400 dark:text-gray-500 text-xs ml-1">
          {filtered.length} of {alerts.length}
        </span>
      </div>

      {/* List */}
      <div className="space-y-2 max-h-[72vh] overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-3">
              <Filter size={20} className="text-gray-400" />
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {alerts.length === 0 ? "No alerts yet — monitoring network traffic…" : "No alerts match the current filters."}
            </p>
          </div>
        ) : (
          filtered.map(a => <AlertCard key={a.id} alert={a} onAcknowledge={handleAck} />)
        )}
      </div>
    </div>
  );
}
