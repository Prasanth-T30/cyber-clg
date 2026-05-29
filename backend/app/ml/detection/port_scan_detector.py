"""
FusionGuardNet – Port Scan Detector
Uses LSTM on packet event sequences to detect systematic port enumeration.
Also applies a fast heuristic: many distinct dst_ports from one src in a short window.
"""

import logging
import numpy as np
from collections import defaultdict
from typing import Any, Dict, List

from app.ml.models.lstm_model import train_lstm, predict_lstm
from app.ml.feature_extractor import build_sequence

logger = logging.getLogger(__name__)

# Rule thresholds
RULE_UNIQUE_PORTS  = 15    # distinct dst_ports per source in one window
RULE_WINDOW_SEC    = 5.0   # seconds

_model = None


def get_model():
    global _model
    if _model is None:
        _model = train_lstm()
    return _model


def detect(packets: List[Dict[str, Any]], window_src_port_map: Dict[str, set]) -> Dict[str, Any]:
    """
    Args:
        packets: recent packet dicts (up to last 10) for LSTM input
        window_src_port_map: {src_ip: set(dst_ports)} accumulated in current window

    Returns:
        detection result dict
    """
    # ── Rule-based ─────────────────────────────────────────────────────────
    rule_triggered = False
    rule_details   = []

    for src_ip, ports in window_src_port_map.items():
        if len(ports) >= RULE_UNIQUE_PORTS:
            rule_triggered = True
            rule_details.append(f"{src_ip} scanned {len(ports)} ports")

    # ── LSTM inference ─────────────────────────────────────────────────────
    sequence = build_sequence(packets, seq_len=10)
    ml_class, ml_conf = predict_lstm(get_model(), sequence)

    # ── Combined ───────────────────────────────────────────────────────────
    is_attack = rule_triggered or (ml_class == 1 and ml_conf >= 0.65)
    confidence = max(ml_conf, 0.90) if rule_triggered else ml_conf

    return {
        "attack_type": "Port Scanning" if is_attack else None,
        "confidence":  round(confidence, 4),
        "method":      "combined" if rule_triggered and ml_class == 1 else
                       "rule"     if rule_triggered else
                       "ml"       if ml_class == 1 else "none",
        "details": "; ".join(rule_details) or f"LSTM conf={ml_conf:.3f}",
    }
