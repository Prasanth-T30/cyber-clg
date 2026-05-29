"""
FusionGuardNet – Brute Force Detector
Detects repeated authentication failures using LSTM on login-attempt sequences
plus a sliding-window rule: N failed logins from the same IP within T seconds.
"""

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np

from app.ml.models.lstm_model import train_lstm, predict_lstm
from app.ml.feature_extractor import build_sequence

logger = logging.getLogger(__name__)

# Rule thresholds
RULE_FAIL_COUNT  = 5      # failed attempts
RULE_WINDOW_SEC  = 60.0   # within 60 seconds

# In-memory sliding window: {src_ip: [(timestamp, success)]}
_attempt_log: Dict[str, List] = defaultdict(list)
_model = None


def get_model():
    global _model
    if _model is None:
        _model = train_lstm()
    return _model


def record_attempt(src_ip: str, success: bool, timestamp: float = None):
    """Call this for every auth attempt to maintain the sliding window."""
    ts = timestamp or time.time()
    _attempt_log[src_ip].append((ts, success))
    # Prune old entries
    cutoff = ts - RULE_WINDOW_SEC
    _attempt_log[src_ip] = [(t, s) for t, s in _attempt_log[src_ip] if t >= cutoff]


def detect(
    src_ip: str,
    recent_packets: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Args:
        src_ip:         source IP to examine
        recent_packets: last N packet dicts from this IP

    Returns:
        detection result dict
    """
    # ── Rule-based ─────────────────────────────────────────────────────────
    attempts = _attempt_log.get(src_ip, [])
    fail_count = sum(1 for _, success in attempts if not success)

    rule_triggered = fail_count >= RULE_FAIL_COUNT
    rule_detail    = f"{fail_count} failed attempts in {RULE_WINDOW_SEC:.0f}s" if rule_triggered else ""

    # ── LSTM inference ─────────────────────────────────────────────────────
    sequence = build_sequence(recent_packets, seq_len=10)
    ml_class, ml_conf = predict_lstm(get_model(), sequence)

    # ── Combined ───────────────────────────────────────────────────────────
    is_attack = rule_triggered or (ml_class == 1 and ml_conf >= 0.65)
    confidence = max(ml_conf, 0.92) if rule_triggered else ml_conf

    return {
        "attack_type": "Brute Force" if is_attack else None,
        "confidence":  round(confidence, 4),
        "method":      "combined" if rule_triggered and ml_class == 1 else
                       "rule"     if rule_triggered else
                       "ml"       if ml_class == 1 else "none",
        "details": rule_detail or f"LSTM conf={ml_conf:.3f}",
        "src_ip":  src_ip,
        "fail_count": fail_count,
    }
