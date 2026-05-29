/**
 * FusionGuardNet – InstantDB Client Setup
 * Initialises @instantdb/react and exports the db instance.
 * The APP_ID must match the one in your InstantDB dashboard.
 *
 * Usage:
 *   import { db } from "@/services/instantdb";
 *   const { data } = db.useQuery({ alerts: {} });
 */

import { init } from "@instantdb/react";

const APP_ID = import.meta.env.VITE_INSTANTDB_APP_ID || "YOUR_INSTANTDB_APP_ID";

export const db = init({ appId: APP_ID });

/**
 * Helper: subscribe to real-time alerts from InstantDB.
 * Returns { data, isLoading, error }.
 */
export function useInstantAlerts(limit = 50) {
  return db.useQuery({
    alerts: {
      $: { limit, order: { createdAt: "desc" } },
    },
  });
}
