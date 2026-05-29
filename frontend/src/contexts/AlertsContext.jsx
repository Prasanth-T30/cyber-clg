/**
 * FusionGuardNet – Alerts Context
 * Single shared WebSocket connection for the entire app.
 * Components consume via useAlertsContext() instead of useAlerts().
 */
import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import { clearAlerts as apiClearAlerts } from "@/services/api";

const AlertsContext = createContext(null);
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/alerts";
const RECONNECT_DELAY_MS = 3000;

export function AlertsProvider({ children }) {
  const [alerts,    setAlerts]    = useState([]);
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);
  const wsRef         = useRef(null);
  const reconnectRef  = useRef(null);
  const MAX_ALERTS    = 500;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      clearTimeout(reconnectRef.current);
    };
    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === "history") {
          setAlerts(msg.alerts || []);
        } else if (msg.type === "alert") {
          setLastEvent(msg.alert);
          setAlerts(prev => [msg.alert, ...prev].slice(0, MAX_ALERTS));
        }
      } catch {}
    };
    ws.onclose = () => {
      setConnected(false);
      reconnectRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
    };
    ws.onerror = () => ws.close();
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      clearTimeout(reconnectRef.current);
    };
  }, [connect]);

  const clearLocal = useCallback(() => setAlerts([]), []);

  const clearAll = useCallback(async () => {
    try { await apiClearAlerts(); } catch {}
    setAlerts([]);
  }, []);

  return (
    <AlertsContext.Provider value={{ alerts, connected, lastEvent, clearLocal, clearAll }}>
      {children}
    </AlertsContext.Provider>
  );
}

export function useAlertsContext() {
  const ctx = useContext(AlertsContext);
  if (!ctx) throw new Error("useAlertsContext must be used within AlertsProvider");
  return ctx;
}
