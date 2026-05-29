/**
 * FusionGuardNet – useAlerts hook
 * Connects to the FastAPI WebSocket for real-time alerts
 * and exposes the alert list + helpers.
 */

import { useState, useEffect, useCallback, useRef } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/alerts";
const RECONNECT_DELAY_MS = 3000;

export function useAlerts(maxAlerts = 100) {
  const [alerts, setAlerts]         = useState([]);
  const [connected, setConnected]   = useState(false);
  const [lastEvent, setLastEvent]   = useState(null);
  const wsRef                       = useRef(null);
  const reconnectTimer              = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === "history") {
          setAlerts(msg.alerts || []);
        } else if (msg.type === "alert") {
          setLastEvent(msg.alert);
          setAlerts((prev) => [msg.alert, ...prev].slice(0, maxAlerts));
        }
      } catch { /* ignore parse errors */ }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
    };

    ws.onerror = () => ws.close();
  }, [maxAlerts]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  const clearLocalAlerts = useCallback(() => setAlerts([]), []);

  return { alerts, connected, lastEvent, clearLocalAlerts };
}
