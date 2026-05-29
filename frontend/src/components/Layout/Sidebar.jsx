import { NavLink } from "react-router-dom";
import { LayoutDashboard, Bell, BarChart3, Settings, Activity, ChevronRight } from "lucide-react";
import { useAlertsContext } from "@/contexts/AlertsContext";

const links = [
  { to: "/",          icon: LayoutDashboard, label: "Dashboard"  },
  { to: "/alerts",    icon: Bell,            label: "Alerts"     },
  { to: "/analytics", icon: BarChart3,       label: "Analytics"  },
  { to: "/simulate",  icon: Activity,        label: "Simulate"   },
  { to: "/settings",  icon: Settings,        label: "Settings"   },
];

export default function Sidebar() {
  const { alerts } = useAlertsContext();
  const activeCount = alerts.filter(a => a.status === "active").length;

  return (
    <aside className="w-56 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col py-5 gap-0.5 shrink-0">
      <div className="px-3 mb-2">
        <p className="text-[11px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider px-2">Navigation</p>
      </div>
      {links.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            `group flex items-center gap-3 px-5 py-2.5 mx-2 text-sm font-medium rounded-lg transition-all
             ${isActive
               ? "bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 shadow-sm"
               : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800"}`
          }
        >
          {({ isActive }) => (
            <>
              <Icon size={17} />
              <span className="flex-1">{label}</span>
              {label === "Alerts" && activeCount > 0 && (
                <span className="text-[10px] font-bold bg-red-500 text-white px-1.5 py-0.5 rounded-full">{activeCount}</span>
              )}
              {isActive && <ChevronRight size={14} className="opacity-50" />}
            </>
          )}
        </NavLink>
      ))}

      {/* Footer */}
      <div className="mt-auto px-5 py-3 mx-2 border-t border-gray-100 dark:border-gray-800">
        <p className="text-[11px] text-gray-400 dark:text-gray-500">FusionGuardNet v1.0</p>
        <p className="text-[10px] text-gray-300 dark:text-gray-600 mt-0.5">CNN · LSTM · Random Forest</p>
      </div>
    </aside>
  );
}
