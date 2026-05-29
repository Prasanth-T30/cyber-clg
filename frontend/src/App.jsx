import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider }  from "@/contexts/ThemeContext";
import { AuthProvider, useAuth }   from "@/contexts/AuthContext";
import { AlertsProvider } from "@/contexts/AlertsContext";
import AppLayout  from "@/components/Layout/AppLayout";
import Home       from "@/pages/Home";
import Alerts     from "@/pages/Alerts";
import Analytics  from "@/pages/Analytics";
import Simulate   from "@/pages/Simulate";
import Settings   from "@/pages/Settings";
import Login      from "@/pages/Login";
import Register   from "@/pages/Register";
import CyberCursor from "@/components/CyberCursor/CyberCursor";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      {/* Protected */}
      <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index          element={<Home />}      />
        <Route path="alerts"    element={<Alerts />}    />
        <Route path="analytics" element={<Analytics />} />
        <Route path="simulate"  element={<Simulate />}  />
        <Route path="settings"  element={<Settings />}  />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AlertsProvider>
            <CyberCursor />
            <AppRoutes />
          </AlertsProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
