"""
FusionGuardNet – InstantDB Client
Wraps InstantDB's REST API for server-side writes (alerts, events).
Frontend uses @instantdb/react for real-time subscriptions.
"""

import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


class InstantDBClient:
    """
    Thin async wrapper around InstantDB's Admin REST API.
    Endpoint: POST https://api.instantdb.com/admin/transact
    """

    def __init__(self):
        self.app_id = settings.INSTANTDB_APP_ID
        self.admin_token = settings.INSTANTDB_ADMIN_TOKEN
        self.base_url = settings.INSTANTDB_BASE_URL
        self._headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json",
        }

    # ── Internal helper ─────────────────────────────────────────────────────

    async def _transact(self, steps: List[Dict]) -> Dict:
        """Post a transaction to InstantDB."""
        payload = {"steps": steps}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/admin/transact",
                    headers=self._headers,
                    json=payload,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("InstantDB transact failed (running in local-only mode): %s", exc)
            return {"status": "local-only", "error": str(exc)}

    # ── Public helpers ───────────────────────────────────────────────────────

    async def save_alert(self, alert: Dict[str, Any]) -> Dict:
        """Persist a detection alert to InstantDB."""
        step = {
            "action": "update",
            "e": "alerts",
            "eid": alert["id"],
            "data": {
                **alert,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self._transact([step])

    async def save_network_event(self, event: Dict[str, Any]) -> Dict:
        """Persist a raw network event."""
        step = {
            "action": "update",
            "e": "network_events",
            "eid": event["id"],
            "data": event,
        }
        return await self._transact([step])

    async def save_stats_snapshot(self, stats: Dict[str, Any]) -> Dict:
        """Save aggregated detection statistics."""
        step = {
            "action": "update",
            "e": "stats_snapshots",
            "eid": stats["id"],
            "data": {
                **stats,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self._transact([step])


# Singleton instance
db = InstantDBClient()
