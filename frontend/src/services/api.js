/**
 * FusionGuardNet – API Service
 * All calls to the FastAPI backend with optional JWT Bearer token.
 */

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

function getToken() {
  try { return localStorage.getItem("fgn-token"); } catch { return null; }
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = `API ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const loginUser    = (username, password) =>
  request("/auth/login",    { method: "POST", body: JSON.stringify({ username, password }) });

export const registerUser = (username, email, password, full_name = "") =>
  request("/auth/register", { method: "POST", body: JSON.stringify({ username, email, password, full_name }) });

export const getMe = () => request("/auth/me");

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const getStats          = ()         => request("/dashboard/stats");
export const getTimeline       = ()         => request("/dashboard/attack-timeline");
export const getRecentActivity = (n = 20)  => request(`/dashboard/recent-activity?limit=${n}`);

// ── Alerts ────────────────────────────────────────────────────────────────────
export const getAlerts        = (limit = 50) => request(`/alerts/?limit=${limit}`);
export const getAlert         = (id)          => request(`/alerts/${id}`);
export const acknowledgeAlert = (id)          => request(`/alerts/${id}/acknowledge`, { method: "PATCH" });
export const clearAlerts      = ()            => request("/alerts/clear", { method: "DELETE" });

// ── Simulate / Detect ─────────────────────────────────────────────────────────
export const simulateAttack = (attack_type) =>
  request("/detect/simulate", { method: "POST", body: JSON.stringify({ attack_type }) });

export const detectDdos = (flow) =>
  request("/detect/ddos", { method: "POST", body: JSON.stringify(flow) });

export const detectSqli = (payload) =>
  request("/detect/sqli", { method: "POST", body: JSON.stringify({
    payload, dst_port: 80, src_ip: "127.0.0.1", dst_ip: "10.0.0.1",
  }) });
