"""
FusionGuardNet – Dashboard Router
Aggregated statistics for the React dashboard.
"""

import time
from collections import Counter
from fastapi import APIRouter

from app.packet_sniffer.sniffer import RECENT_ALERTS, RECENT_PACKETS

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", summary="Aggregated detection statistics")
async def get_stats():
    alerts = list(RECENT_ALERTS)
    packets = list(RECENT_PACKETS)

    attack_counts = Counter(
        a["attack_type"] for a in alerts if a.get("attack_type")
    )
    severity_counts = Counter(a.get("severity", "low") for a in alerts)

    # Last 24 h vs older
    cutoff = time.time() - 86400
    recent = [a for a in alerts if a.get("timestamp", 0) >= cutoff]

    return {
        "total_alerts":        len(alerts),
        "alerts_last_24h":     len(recent),
        "total_packets":       len(packets),
        "attack_breakdown":    dict(attack_counts),
        "severity_breakdown":  dict(severity_counts),
        "top_attack":          attack_counts.most_common(1)[0][0] if attack_counts else None,
        "active_alerts":       sum(1 for a in alerts if a.get("status") == "active"),
    }


@router.get("/recent-activity", summary="Last N packets and alerts")
async def recent_activity(limit: int = 20):
    return {
        "packets": list(RECENT_PACKETS)[:limit],
        "alerts":  list(RECENT_ALERTS)[:limit],
    }


@router.get("/attack-timeline", summary="Alert counts grouped by minute (last 30 min)")
async def attack_timeline():
    now = time.time()
    window = 30 * 60   # 30 minutes
    bucket_size = 60   # 1-minute buckets

    buckets: dict = {}
    for alert in RECENT_ALERTS:
        ts = alert.get("timestamp", 0)
        if now - ts <= window:
            minute = int((now - ts) // bucket_size)
            key = f"-{minute}m"
            buckets[key] = buckets.get(key, 0) + 1

    # Fill missing minutes with 0
    timeline = [
        {"label": f"-{i}m", "count": buckets.get(f"-{i}m", 0)}
        for i in range(30, -1, -1)
    ]
    return {"timeline": timeline}
