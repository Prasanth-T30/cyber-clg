/**
 * FusionGuardNet – useDetection hook
 */
import { useState, useCallback } from "react";
import { simulateAttack, detectDdos, detectSqli } from "@/services/api";

export function useDetection() {
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  const run = useCallback(async (fn, ...args) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fn(...args);
      setResult(res);
      return res;
    } catch (e) {
      const msg = e.message || "Detection request failed";
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    result,
    error,
    simulate:   (type)    => run(simulateAttack, type),
    detectDdos: (flow)    => run(detectDdos, flow),
    detectSqli: (payload) => run(detectSqli, payload),
    reset:      ()        => { setResult(null); setError(null); },
  };
}
