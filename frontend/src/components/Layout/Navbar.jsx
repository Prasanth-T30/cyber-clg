import { ShieldAlert, Wifi, WifiOff, Sun, Moon, LogOut, User, Bell } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth }  from "@/contexts/AuthContext";
import { useAlertsContext } from "@/contexts/AlertsContext";
import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  const { theme, toggleTheme, isDark } = useTheme();
  const { user, logout } = useAuth();
  const { alerts, connected } = useAlertsContext();
  const activeCount = alerts.filter(a => a.status === "active").length;

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const initials = user?.full_name
    ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.username?.slice(0, 2).toUpperCase() || "??";

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-5 py-3 flex items-center justify-between z-40 shadow-sm">
      {/* Left: Logo */}
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-9 h-9 bg-brand-600 rounded-lg shadow">
          <ShieldAlert className="text-white" size={20} />
        </div>
        <div>
          <h1 className="text-gray-900 dark:text-white font-bold text-base leading-none">FusionGuardNet</h1>
          <p className="text-gray-400 text-[11px] leading-none mt-0.5">Intrusion Detection System</p>
        </div>
      </div>

      {/* Right: controls */}
      <div className="flex items-center gap-3">
        {/* Alert badge */}
        {activeCount > 0 && (
          <Link to="/alerts" className="flex items-center gap-1.5 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors">
            <Bell size={12} className="animate-pulse" />
            {activeCount} Active
          </Link>
        )}

        {/* WS status */}
        <div className={`hidden sm:flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-full ${
          connected
            ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
            : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
        }`}>
          {connected ? <Wifi size={12}/> : <WifiOff size={12}/>}
          {connected ? "Live" : "Reconnecting…"}
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-brand-500 transition-colors"
          title={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDark
            ? <Sun size={18} />
            : <Moon size={18} />
          }
        </button>

        {/* User menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(v => !v)}
            className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="w-7 h-7 bg-brand-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
              {initials}
            </div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200 hidden sm:block">
              {user?.username || "User"}
            </span>
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1.5 w-52 card shadow-xl py-1 z-50 animate-fade-in">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{user?.full_name || user?.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{user?.email}</p>
                <span className="inline-block mt-1.5 text-xs bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 px-2 py-0.5 rounded-full capitalize">
                  {user?.role || "analyst"}
                </span>
              </div>
              <Link
                to="/settings"
                className="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                <User size={15} /> Profile & Settings
              </Link>
              <button
                onClick={() => { logout(); setMenuOpen(false); }}
                className="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <LogOut size={15} /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
