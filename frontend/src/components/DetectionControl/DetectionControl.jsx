import { useState } from "react";
import { useDetection } from "@/hooks/useDetection";
import { Play, Loader2, Zap, Code2, CheckCircle, XCircle } from "lucide-react";

const ATTACK_OPTIONS = [
  { value: null,          label: "Random",         icon: "🎲" },
  { value: "ddos",        label: "DDoS",           icon: "💥" },
  { value: "port_scan",   label: "Port Scanning",  icon: "🔍" },
  { value: "brute_force", label: "Brute Force",    icon: "🔑" },
  { value: "malware",     label: "Malware Traffic",icon: "🦠" },
  { value: "sqli",        label: "SQL Injection",  icon: "💉" },
];

function ResultView({ result }) {
  const detected = result?.detections
    ? Object.values(result.detections).some(d => d.attack_type)
    : result?.result?.attack_type;

  return (
    <div className="card p-5 animate-fade-in">
      <div className="flex items-center gap-2 mb-3">
        {detected
          ? <XCircle size={18} className="text-red-500" />
          : <CheckCircle size={18} className="text-green-500" />}
        <h3 className="section-title">
          {detected ? "Threat Detected" : "No Threat Found"}
        </h3>
      </div>
      <pre className="bg-gray-50 dark:bg-gray-900 text-green-700 dark:text-green-400 text-xs rounded-lg p-4 overflow-x-auto whitespace-pre-wrap font-mono border border-gray-200 dark:border-gray-700 max-h-56">
        {JSON.stringify(result, null, 2)}
      </pre>
    </div>
  );
}

export default function DetectionControl() {
  const [selectedType, setSelectedType] = useState(null);
  const [sqliInput,    setSqliInput]    = useState("' OR '1'='1' --");
  const { loading, result, error, simulate, detectSqli } = useDetection();

  return (
    <div className="space-y-6">
      <h2 className="page-title">Attack Simulator</h2>

      {/* Attack type picker */}
      <div className="card p-6 space-y-5">
        <div>
          <h3 className="section-title mb-1">Simulate Network Attack</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Inject a synthetic attack packet into the detection pipeline</p>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {ATTACK_OPTIONS.map(opt => (
            <button
              key={String(opt.value)}
              onClick={() => setSelectedType(opt.value)}
              className={`flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl border text-sm font-medium transition-all
                ${selectedType === opt.value
                  ? "bg-brand-600 border-brand-500 text-white shadow-md shadow-brand-500/20"
                  : "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900/20"}`}
            >
              <span className="text-lg">{opt.icon}</span>
              <span className="text-xs leading-tight text-center">{opt.label}</span>
            </button>
          ))}
        </div>

        <button
          onClick={() => simulate(selectedType)}
          disabled={loading}
          className="btn-primary w-full justify-center"
        >
          {loading ? <><Loader2 size={16} className="animate-spin"/>Running…</> : <><Zap size={16}/>Launch Simulation</>}
        </button>
      </div>

      {/* SQLi tester */}
      <div className="card p-6 space-y-4">
        <div>
          <h3 className="section-title mb-1">SQL Injection Analyser</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Test a payload string against the SQL injection detector</p>
        </div>
        <div>
          <label className="label">Suspicious payload</label>
          <textarea
            value={sqliInput}
            onChange={e => setSqliInput(e.target.value)}
            rows={3}
            className="input font-mono resize-none"
            placeholder="Enter suspicious query or payload…"
          />
        </div>
        <button
          onClick={() => detectSqli(sqliInput)}
          disabled={loading || !sqliInput.trim()}
          className="btn-primary bg-purple-600 hover:bg-purple-700 w-full justify-center"
        >
          {loading ? <><Loader2 size={16} className="animate-spin"/>Analysing…</> : <><Code2 size={16}/>Analyse Payload</>}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-4">
          <XCircle size={16} className="text-red-500 mt-0.5 shrink-0" />
          <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && <ResultView result={result} />}
    </div>
  );
}
