import { useState } from "react";
import { useAuth }  from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { Save, Sun, Moon, ShieldCheck, Server, Info, CheckCircle } from "lucide-react";

function Section({ icon: Icon, title, children }) {
  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-700 pb-3">
        <Icon size={17} className="text-brand-500" />
        <h3 className="section-title">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  );
}

export default function Settings() {
  const { user } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();

  const [apiUrl, setApiUrl] = useState(
    () => localStorage.getItem("fgn-api-url") || import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"
  );
  const [wsUrl, setWsUrl] = useState(
    () => localStorage.getItem("fgn-ws-url") || import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/alerts"
  );
  const [threshold, setThreshold] = useState(
    () => localStorage.getItem("fgn-threshold") || "0.65"
  );
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    try {
      localStorage.setItem("fgn-api-url",   apiUrl);
      localStorage.setItem("fgn-ws-url",    wsUrl);
      localStorage.setItem("fgn-threshold", threshold);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {}
  };

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="page-title">Settings</h2>

      {/* Profile */}
      <Section icon={ShieldCheck} title="Account">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-brand-600 rounded-2xl flex items-center justify-center text-white text-xl font-bold shrink-0">
            {(user?.full_name || user?.username || "U").slice(0, 2).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-900 dark:text-white">{user?.full_name || user?.username}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
            <span className="inline-block mt-1 text-xs bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 px-2 py-0.5 rounded-full capitalize">
              {user?.role || "analyst"}
            </span>
          </div>
        </div>
      </Section>

      {/* Appearance */}
      <Section icon={Sun} title="Appearance">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">UI Theme</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              Currently: <span className="font-medium capitalize">{theme}</span> mode
            </p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative inline-flex items-center w-14 h-7 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 ${
              isDark ? "bg-gray-700" : "bg-brand-500"
            }`}
            aria-label="Toggle theme"
          >
            <span className={`absolute left-1 flex items-center justify-center w-5 h-5 bg-white rounded-full shadow transition-transform ${isDark ? "translate-x-0" : "translate-x-7"}`}>
              {isDark ? <Moon size={11} className="text-gray-700"/> : <Sun size={11} className="text-brand-500"/>}
            </span>
          </button>
        </div>
      </Section>

      {/* Connection */}
      <Section icon={Server} title="Connection">
        <Field label="Backend API URL">
          <input type="text" className="input" value={apiUrl} onChange={e => setApiUrl(e.target.value)} />
        </Field>
        <Field label="WebSocket URL">
          <input type="text" className="input" value={wsUrl} onChange={e => setWsUrl(e.target.value)} />
        </Field>
        <Field label="Detection Confidence Threshold">
          <div className="flex items-center gap-3">
            <input
              type="range" min="0.5" max="0.99" step="0.01"
              value={threshold}
              onChange={e => setThreshold(e.target.value)}
              className="flex-1 accent-brand-500"
            />
            <span className="text-gray-900 dark:text-white font-mono text-sm w-12 text-right">{parseFloat(threshold).toFixed(2)}</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">Alerts below this confidence level are suppressed</p>
        </Field>

        <button onClick={handleSave} className="btn-primary">
          {saved ? <><CheckCircle size={15}/>Saved!</> : <><Save size={15}/>Save Settings</>}
        </button>
      </Section>

      {/* About */}
      <Section icon={Info} title="About">
        <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex justify-between"><span>Application</span><span className="font-medium text-gray-900 dark:text-white">FusionGuardNet</span></div>
          <div className="flex justify-between"><span>Version</span><span className="font-medium text-gray-900 dark:text-white">1.0.0</span></div>
          <div className="flex justify-between"><span>Frontend</span><span className="font-medium text-gray-900 dark:text-white">React + Vite + Tailwind</span></div>
          <div className="flex justify-between"><span>Backend</span><span className="font-medium text-gray-900 dark:text-white">FastAPI + Python 3.11</span></div>
          <div className="flex justify-between"><span>Models</span><span className="font-medium text-gray-900 dark:text-white">CNN · LSTM · Random Forest</span></div>
          <div className="flex justify-between"><span>Database</span><span className="font-medium text-gray-900 dark:text-white">SQLite (users) · In-memory (alerts)</span></div>
        </div>
      </Section>
    </div>
  );
}
