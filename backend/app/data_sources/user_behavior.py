"""
FusionGuardNet – User Behaviour Data Source
Detects behavioural anomalies (off-hours access, geo jumps, unusual data volume)
and returns a BehaviourSignal for the Fusion Layer.
"""

import random
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.ml.fusion_layer import BehaviourSignal

logger = logging.getLogger(__name__)

# Business hours (local 24h clock)
BUSINESS_HOUR_START = 8
BUSINESS_HOUR_END   = 18

# Thresholds
VOLUME_THRESHOLD_MB  = 500.0   # MB in one session
RAPID_ACCESS_REQS    = 100     # requests in 60 s


def analyse(event: Dict[str, Any]) -> BehaviourSignal:
    """
    Convert a user event dict into a BehaviourSignal.

    Expected keys:
        hour        (int)   – local hour of access (0–23)
        country     (str)   – ISO country code of current session
        home_country(str)   – user's registered country
        session_mb  (float) – data transferred in this session (MB)
        requests_per_min (int)
        is_new_device (bool)
    """
    hour        = event.get("hour", datetime.now(timezone.utc).hour)
    off_hours   = not (BUSINESS_HOUR_START <= hour < BUSINESS_HOUR_END)
    geo_anomaly = (
        bool(event.get("country")) and
        bool(event.get("home_country")) and
        event["country"] != event["home_country"]
    )
    return BehaviourSignal(
        off_hours_access  = off_hours,
        unusual_volume    = float(event.get("session_mb", 0)) > VOLUME_THRESHOLD_MB,
        new_device        = bool(event.get("is_new_device", False)),
        geo_anomaly       = geo_anomaly,
        rapid_data_access = int(event.get("requests_per_min", 0)) > RAPID_ACCESS_REQS,
    )


def simulate_behaviour(inject_anomaly: bool = False) -> Dict[str, Any]:
    """Return a synthetic behaviour event dict."""
    rng = random.Random()
    if inject_anomaly:
        return {
            "hour":             rng.choice([2, 3, 23, 0]),
            "country":          "RU",
            "home_country":     "US",
            "session_mb":       rng.uniform(600, 2000),
            "requests_per_min": rng.randint(120, 500),
            "is_new_device":    True,
        }
    return {
        "hour":             rng.randint(9, 17),
        "country":          "US",
        "home_country":     "US",
        "session_mb":       rng.uniform(1, 100),
        "requests_per_min": rng.randint(1, 30),
        "is_new_device":    False,
    }
