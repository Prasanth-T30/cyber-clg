/**
 * FusionGuardNet – Auth Context
 * JWT-based auth: login, register, logout with localStorage persistence.
 */
import { createContext, useContext, useState, useCallback } from "react";
import { loginUser, registerUser } from "@/services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(() => {
    try { const u = localStorage.getItem("fgn-user"); return u ? JSON.parse(u) : null; }
    catch { return null; }
  });
  const [token, setToken] = useState(() => {
    try { return localStorage.getItem("fgn-token") || null; }
    catch { return null; }
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const saveSession = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);
    try {
      localStorage.setItem("fgn-user",  JSON.stringify(userData));
      localStorage.setItem("fgn-token", accessToken);
    } catch {}
  };

  const login = useCallback(async (username, password) => {
    setLoading(true); setError(null);
    try {
      const data = await loginUser(username, password);
      saveSession(data.user, data.access_token);
      return { ok: true };
    } catch (e) {
      const msg = e.message || "Login failed";
      setError(msg);
      return { ok: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (username, email, password, fullName) => {
    setLoading(true); setError(null);
    try {
      const data = await registerUser(username, email, password, fullName);
      saveSession(data.user, data.access_token);
      return { ok: true };
    } catch (e) {
      const msg = e.message || "Registration failed";
      setError(msg);
      return { ok: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null); setToken(null);
    try { localStorage.removeItem("fgn-user"); localStorage.removeItem("fgn-token"); } catch {}
  }, []);

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, register, logout, clearError, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
