import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldAlert, Eye, EyeOff, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";

const strengthLabel = (pwd) => {
  if (!pwd) return null;
  const score = [pwd.length >= 8, /[A-Z]/.test(pwd), /[0-9]/.test(pwd), /[^A-Za-z0-9]/.test(pwd)]
    .filter(Boolean).length;
  const map   = ["", "Weak", "Fair", "Good", "Strong"];
  const color = ["", "#ef4444", "#f97316", "#eab308", "#22c55e"];
  const bar   = ["", "#ef4444", "#f97316", "#eab308", "#22c55e"];
  return { label: map[score], color: color[score], bar: bar[score], score };
};

/* Shared cyber input style helper */
const cyberInput = (hasError, hasSuccess) => ({
  background: "rgba(0,255,100,0.04)",
  border: `1px solid ${hasError ? "#ef4444" : hasSuccess ? "#22c55e" : "#00ff4433"}`,
  color: "#00ff88",
  caretColor: "#00ff88",
});

export default function Register() {
  const { register, loading, error, clearError } = useAuth();
  const { toggleTheme, isDark } = useTheme();
  const navigate = useNavigate();

  const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "", full_name: "" });
  const [showPwd,  setShowPwd]  = useState(false);
  const [showConf, setShowConf] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  const strength = strengthLabel(form.password);

  const validate = () => {
    const e = {};
    if (!form.username.trim()) e.username = "Username is required";
    else if (form.username.length < 3) e.username = "At least 3 characters";
    if (!form.email.trim() || !/\S+@\S+\.\S+/.test(form.email)) e.email = "Valid email is required";
    if (!form.password) e.password = "Password is required";
    else if (form.password.length < 6) e.password = "At least 6 characters";
    if (form.password !== form.confirm) e.confirm = "Passwords do not match";
    setFieldErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    clearError();
    if (!validate()) return;
    const res = await register(form.username.trim(), form.email.trim(), form.password, form.full_name.trim());
    if (res.ok) navigate("/", { replace: true });
  };

  const set = (field) => (e) => {
    setForm(f => ({ ...f, [field]: e.target.value }));
    setFieldErrors(f => ({ ...f, [field]: undefined }));
    clearError();
  };

  const focusStyle = (e, err, ok) => {
    e.target.style.borderColor = err ? "#ef4444" : ok ? "#22c55e" : "#00ff88";
    e.target.style.boxShadow   = `0 0 12px ${err ? "#ef444422" : ok ? "#22c55e22" : "#00ff4422"}`;
  };
  const blurStyle  = (e, err, ok) => {
    e.target.style.borderColor = err ? "#ef4444" : ok ? "#22c55e" : "#00ff4433";
    e.target.style.boxShadow   = "none";
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-10 relative overflow-hidden"
      style={{ background: "#020b07", cursor: "default" }}
    >
      <style>{`
        @keyframes floatNodeR {
          0%   { transform: translate(0,0) scale(1); }
          100% { transform: translate(12px,-14px) scale(1.3); }
        }
        @keyframes pulseGlowR {
          0%,100% { box-shadow: 0 0 20px #00ff6644, 0 0 60px #00ff6622; }
          50%      { box-shadow: 0 0 35px #00ff88aa, 0 0 90px #00ff6644; }
        }
        @keyframes borderSpinR {
          0%   { background-position: 0% 50%; }
          100% { background-position: 200% 50%; }
        }
        @keyframes fadeSlideUpR {
          from { opacity:0; transform: translateY(24px); }
          to   { opacity:1; transform: translateY(0); }
        }
        @keyframes matrixFall {
          0%   { transform: translateY(-100%); opacity: 0; }
          10%  { opacity: 0.6; }
          90%  { opacity: 0.6; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
        * { cursor: default !important; }
        button:not(:disabled), a { cursor: pointer !important; }
      `}</style>

      {/* Matrix column strips background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ cursor: "default" }}>
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute top-0 text-xs font-mono select-none whitespace-nowrap"
            style={{
              left: `${i * 5.2}%`,
              color: i % 3 === 0 ? "#00ff4444" : "#00ff2222",
              animation: `matrixFall ${6 + (i % 5) * 1.5}s ${i * 0.4}s linear infinite`,
              writingMode: "vertical-rl",
              letterSpacing: "0.2em",
            }}
          >
            {Array.from({ length: 20 }, () => "01アイウ#$AB"[Math.floor(Math.random() * 11)]).join(" ")}
          </div>
        ))}
      </div>

      {/* Floating threat nodes */}
      <div className="fixed inset-0 pointer-events-none" style={{ cursor: "default" }}>
        {[...Array(14)].map((_, i) => (
          <div key={i} className="absolute rounded-full"
            style={{
              left: `${5 + i * 6.8}%`, top: `${10 + (i * 37) % 80}%`,
              width: 4 + (i % 4), height: 4 + (i % 4),
              background: ["#ef4444","#f97316","#22c55e","#06b6d4","#a855f7"][i % 5],
              boxShadow: `0 0 ${10 + i % 8}px ${["#ef4444","#f97316","#22c55e","#06b6d4","#a855f7"][i % 5]}`,
              opacity: 0.5,
              animation: `floatNodeR ${5 + i % 4}s ${i * 0.3}s ease-in-out infinite alternate`,
            }}
          />
        ))}
      </div>

      {/* Scanlines */}
      <div className="fixed inset-0 pointer-events-none"
        style={{ background: "repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,100,0.012) 2px,rgba(0,255,100,0.012) 4px)", cursor: "default" }}
      />

      {/* Theme toggle */}
      <button onClick={toggleTheme}
        className="fixed top-4 right-4 z-50 p-2 rounded-full border"
        style={{ background: "rgba(0,20,10,0.8)", borderColor: "#00ff4422", color: "#00ff88" }}
        title="Toggle theme"
      >
        {isDark
          ? <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" /></svg>
          : <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" /></svg>
        }
      </button>

      {/* Card */}
      <div className="relative z-20 w-full max-w-sm" style={{ animation: "fadeSlideUpR 0.6s ease both" }}>
        {/* Logo */}
        <div className="text-center mb-6">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-3"
            style={{ background: "linear-gradient(135deg,#003d1a,#001a0d)", animation: "pulseGlowR 3s ease-in-out infinite", border: "1px solid #00ff4433" }}
          >
            <ShieldAlert size={30} style={{ color: "#00ff88" }} />
          </div>
          <h1 className="text-xl font-bold font-mono" style={{ color: "#00ff88", letterSpacing: "0.05em" }}>FusionGuardNet</h1>
          <p className="text-xs font-mono mt-0.5" style={{ color: "#00cc6688" }}>◈ CREATE ANALYST ACCOUNT ◈</p>
        </div>

        <div
          className="relative rounded-xl p-px overflow-hidden"
          style={{ background: "linear-gradient(135deg,#00ff4433,#00aaff22,#ff004422,#00ff4433)", backgroundSize: "300% 300%", animation: "borderSpinR 4s linear infinite" }}
        >
          <div className="rounded-xl p-7" style={{ background: "rgba(2,14,8,0.95)", backdropFilter: "blur(12px)" }}>
            <div className="flex items-center gap-2 mb-5">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs font-mono" style={{ color: "#00ff88" }}>NEW USER ENROLLMENT</span>
              <div className="flex-1 h-px" style={{ background: "#00ff4422" }} />
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg p-3 mb-4 border" style={{ background: "rgba(239,68,68,0.1)", borderColor: "#ef444433", color: "#fca5a5" }}>
                <AlertCircle size={15} className="shrink-0" />
                <p className="text-xs font-mono">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {/* Full Name */}
              <div>
                <label className="block text-xs font-mono mb-1.5" style={{ color: "#00cc88" }}>&gt; FULL NAME <span style={{ color: "#00ff4455" }}>(optional)</span></label>
                <input
                  type="text" className="w-full rounded-lg px-3 py-2 text-sm font-mono outline-none transition-all"
                  style={cyberInput(false, false)}
                  onFocus={e => focusStyle(e, false, false)} onBlur={e => blurStyle(e, false, false)}
                  placeholder="John Doe" value={form.full_name} onChange={set("full_name")} autoComplete="name" autoFocus
                />
              </div>

              {/* Username */}
              <div>
                <label className="block text-xs font-mono mb-1.5" style={{ color: "#00cc88" }}>&gt; USERNAME *</label>
                <input
                  type="text" className="w-full rounded-lg px-3 py-2 text-sm font-mono outline-none transition-all"
                  style={cyberInput(fieldErrors.username, false)}
                  onFocus={e => focusStyle(e, fieldErrors.username, false)} onBlur={e => blurStyle(e, fieldErrors.username, false)}
                  placeholder="analyst_01" value={form.username} onChange={set("username")} autoComplete="username"
                />
                {fieldErrors.username && <p className="text-xs font-mono mt-1" style={{ color: "#ef4444" }}>⚠ {fieldErrors.username}</p>}
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-mono mb-1.5" style={{ color: "#00cc88" }}>&gt; EMAIL *</label>
                <input
                  type="email" className="w-full rounded-lg px-3 py-2 text-sm font-mono outline-none transition-all"
                  style={cyberInput(fieldErrors.email, false)}
                  onFocus={e => focusStyle(e, fieldErrors.email, false)} onBlur={e => blurStyle(e, fieldErrors.email, false)}
                  placeholder="you@example.com" value={form.email} onChange={set("email")} autoComplete="email"
                />
                {fieldErrors.email && <p className="text-xs font-mono mt-1" style={{ color: "#ef4444" }}>⚠ {fieldErrors.email}</p>}
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-mono mb-1.5" style={{ color: "#00cc88" }}>&gt; PASSWORD *</label>
                <div className="relative">
                  <input
                    type={showPwd ? "text" : "password"} className="w-full rounded-lg px-3 py-2 pr-10 text-sm font-mono outline-none transition-all"
                    style={cyberInput(fieldErrors.password, false)}
                    onFocus={e => focusStyle(e, fieldErrors.password, false)} onBlur={e => blurStyle(e, fieldErrors.password, false)}
                    placeholder="Min. 6 characters" value={form.password} onChange={set("password")} autoComplete="new-password"
                  />
                  <button type="button" onClick={() => setShowPwd(v => !v)} className="absolute inset-y-0 right-0 px-3" style={{ color: "#00ff6688" }}>
                    {showPwd ? <EyeOff size={15}/> : <Eye size={15}/>}
                  </button>
                </div>
                {form.password && strength && (
                  <div className="flex items-center gap-2 mt-1.5">
                    <div className="flex gap-0.5 flex-1">
                      {[1,2,3,4].map(i => (
                        <div key={i} className="h-1 flex-1 rounded-full transition-all"
                          style={{ background: i <= strength.score ? strength.bar : "#00ff4411", boxShadow: i <= strength.score ? `0 0 4px ${strength.bar}` : "none" }}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-mono" style={{ color: strength.color }}>{strength.label}</span>
                  </div>
                )}
                {fieldErrors.password && <p className="text-xs font-mono mt-1" style={{ color: "#ef4444" }}>⚠ {fieldErrors.password}</p>}
              </div>

              {/* Confirm */}
              <div>
                <label className="block text-xs font-mono mb-1.5" style={{ color: "#00cc88" }}>&gt; CONFIRM PASSWORD *</label>
                <div className="relative">
                  <input
                    type={showConf ? "text" : "password"} className="w-full rounded-lg px-3 py-2 pr-16 text-sm font-mono outline-none transition-all"
                    style={cyberInput(fieldErrors.confirm, form.confirm && form.confirm === form.password)}
                    onFocus={e => focusStyle(e, fieldErrors.confirm, form.confirm === form.password && !!form.confirm)}
                    onBlur={e  => blurStyle(e, fieldErrors.confirm, form.confirm === form.password && !!form.confirm)}
                    placeholder="Repeat password" value={form.confirm} onChange={set("confirm")} autoComplete="new-password"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-1 gap-0.5">
                    {form.confirm && form.confirm === form.password && (
                      <CheckCircle2 size={14} style={{ color: "#22c55e" }} />
                    )}
                    <button type="button" onClick={() => setShowConf(v => !v)} className="px-2" style={{ color: "#00ff6688" }}>
                      {showConf ? <EyeOff size={15}/> : <Eye size={15}/>}
                    </button>
                  </div>
                </div>
                {fieldErrors.confirm && <p className="text-xs font-mono mt-1" style={{ color: "#ef4444" }}>⚠ {fieldErrors.confirm}</p>}
              </div>

              {/* Submit */}
              <button
                type="submit" disabled={loading}
                className="w-full flex items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-mono font-semibold transition-all disabled:opacity-50 mt-1"
                style={{ background: "linear-gradient(135deg,#006633,#003d1a)", color: "#00ff88", border: "1px solid #00ff4444", letterSpacing: "0.1em", boxShadow: "0 0 20px #00ff4422" }}
                onMouseEnter={e => { if (!loading) { e.currentTarget.style.boxShadow = "0 0 30px #00ff4466"; e.currentTarget.style.background = "linear-gradient(135deg,#008844,#004d22)"; }}}
                onMouseLeave={e => { e.currentTarget.style.boxShadow = "0 0 20px #00ff4422"; e.currentTarget.style.background = "linear-gradient(135deg,#006633,#003d1a)"; }}
              >
                {loading ? <><Loader2 size={16} className="animate-spin"/>ENROLLING…</> : <>▶ CREATE ACCOUNT</>}
              </button>
            </form>

            <div className="flex items-center gap-2 mt-5">
              <div className="flex-1 h-px" style={{ background: "#00ff4411" }} />
              <span className="text-xs font-mono" style={{ color: "#00ff4444" }}>ENCRYPTED CHANNEL</span>
              <div className="flex-1 h-px" style={{ background: "#00ff4411" }} />
            </div>
          </div>
        </div>

        <p className="text-center text-xs font-mono mt-4" style={{ color: "#00cc6688" }}>
          Already have an account?{" "}
          <Link to="/login" className="font-semibold" style={{ color: "#00ff88" }}
            onMouseEnter={e => e.currentTarget.style.color = "#66ffaa"}
            onMouseLeave={e => e.currentTarget.style.color = "#00ff88"}
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
