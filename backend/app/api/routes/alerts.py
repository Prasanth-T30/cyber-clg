"""
FusionGuardNet – Alerts Router
NOTE: /clear DELETE must be declared BEFORE /{alert_id} to avoid FastAPI
treating "clear" as an alert ID.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.packet_sniffer.sniffer import RECENT_ALERTS

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", summary="List recent alerts")
async def list_alerts(
    limit:       int           = Query(50, ge=1, le=500),
    attack_type: Optional[str] = Query(None),
    severity:    Optional[str] = Query(None),
):
    alerts = list(RECENT_ALERTS)
    if attack_type:
        alerts = [a for a in alerts if a.get("attack_type", "").lower() == attack_type.lower()]
    if severity:
        alerts = [a for a in alerts if a.get("severity", "").lower() == severity.lower()]
    return {"total": len(alerts), "alerts": alerts[:limit]}


# ── IMPORTANT: declare /clear BEFORE /{alert_id} ────────────────────────────
@router.delete("/clear", summary="Clear all alerts (dev/testing)")
async def clear_alerts():
    RECENT_ALERTS.clear()
    return {"message": "All alerts cleared", "cleared": True}


@router.get("/{alert_id}", summary="Get a single alert by ID")
async def get_alert(alert_id: str):
    for alert in RECENT_ALERTS:
        if alert.get("id") == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


@router.patch("/{alert_id}/acknowledge", summary="Acknowledge an alert")
async def acknowledge_alert(alert_id: str):
    for alert in RECENT_ALERTS:
        if alert.get("id") == alert_id:
            alert["status"] = "acknowledged"
            return {"message": "Alert acknowledged", "alert": alert}
    raise HTTPException(status_code=404, detail="Alert not found")
