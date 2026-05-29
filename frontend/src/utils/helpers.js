/** Utility helpers for FusionGuardNet UI */

export const SEVERITY_COLORS = {
  critical: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400",
  high:     "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400",
  medium:   "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400",
  low:      "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
};

export const SEVERITY_BORDER = {
  critical: "border-red-500",
  high:     "border-orange-500",
  medium:   "border-yellow-400",
  low:      "border-blue-400",
};

export const ATTACK_ICONS = {
  "DDoS":           "💥",
  "Port Scanning":  "🔍",
  "Port Scan":      "🔍",
  "Brute Force":    "🔑",
  "Malware Traffic":"🦠",
  "Malware":        "🦠",
  "SQL Injection":  "💉",
  "Unknown":        "⚠️",
};

// Infer icon from a descriptive attack name string
const _ICON_KEYWORDS = [
  { icon: "💥", keys: ["flood","amplification","smurf","slowloris","volumetric","reflection","hijack","ddos"] },
  { icon: "🔍", keys: ["scan","probe","reconnaissance","fingerprint","enumeration","nmap"] },
  { icon: "🔑", keys: ["brute","spray","dictionary","credential","stuffing","pre-auth","kerberos"] },
  { icon: "🦠", keys: ["trojan","ransomware","botnet","keylogger","rootkit","spyware","worm","rat","cryptominer","exfiltration","malware","c2","beacon"] },
  { icon: "💉", keys: ["sqli","sql","injection","union","blind","boolean","stacked","schema","dump","procedure"] },
];

export function attackIcon(name) {
  if (!name) return "⚠️";
  const lower = name.toLowerCase();
  const exact = ATTACK_ICONS[name];
  if (exact) return exact;
  for (const { icon, keys } of _ICON_KEYWORDS) {
    if (keys.some(k => lower.includes(k))) return icon;
  }
  return "⚠️";
}

export function formatTime(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function formatDate(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString();
}

export function pct(value, max) {
  return max > 0 ? Math.min((value / max) * 100, 100).toFixed(1) : 0;
}

export function severityLabel(confidence) {
  if (confidence >= 0.90) return "critical";
  if (confidence >= 0.75) return "high";
  if (confidence >= 0.60) return "medium";
  return "low";
}

export function formatBytes(bytes) {
  if (bytes < 1024)       return bytes + " B";
  if (bytes < 1048576)    return (bytes / 1024).toFixed(1) + " KB";
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + " MB";
  return (bytes / 1073741824).toFixed(1) + " GB";
}
