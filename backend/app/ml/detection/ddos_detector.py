"""
FusionGuardNet – DDoS Detector
Uses Random Forest on flow-level features + rule-based thresholds.
Detects: SYN floods, UDP floods, ICMP floods, HTTP floods.
"""

import logging
import numpy as np
from typing import Any, Dict, Optional, Tuple

from app.ml.models.random_forest_model import train_rf, predict_rf
from app.ml.feature_extractor import extract_flow_features_from_dict

logger = logging.getLogger(__name__)

# Thresholds for instant rule-based detection (before ML)
RULE_PKT_RATE   = 1000.0   # packets/sec
RULE_SYN_RATIO  = 0.85
RULE_UNIQUE_SRC = 100

_model = None


def get_model():
    global _model
    if _model is None:
        _model = train_rf()
    return _model


def detect(flow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyse a flow summary dict and return a detection result.

    Args:
        flow: dict with keys matching extract_flow_features_from_dict

    Returns:
        {
          "attack_type": "DDoS" | None,
          "confidence": float,
          "method": "rule" | "ml" | "combined",
          "details": str
        }
    """
    # ── Rule-based fast-path ───────────────────────────────────────────────
    rule_triggered = False
    rule_details   = []

    if flow.get("pkt_rate", 0) > RULE_PKT_RATE:
        rule_triggered = True
        rule_details.append(f"pkt_rate={flow['pkt_rate']:.0f} (>{RULE_PKT_RATE})")

    if flow.get("syn_ratio", 0) > RULE_SYN_RATIO:
        rule_triggered = True
        rule_details.append(f"syn_ratio={flow['syn_ratio']:.2f} (>{RULE_SYN_RATIO})")

    if flow.get("unique_src_ips", 0) > RULE_UNIQUE_SRC:
        rule_triggered = True
        rule_details.append(f"unique_src_ips={flow['unique_src_ips']} (>{RULE_UNIQUE_SRC})")

    # ── ML classification ──────────────────────────────────────────────────
    features = extract_flow_features_from_dict(flow)
    ml_class, ml_conf = predict_rf(get_model(), features)

    # ── Combined decision ──────────────────────────────────────────────────
    is_attack = rule_triggered or (ml_class == 1 and ml_conf >= 0.65)

    method = "combined" if (rule_triggered and ml_class == 1) else \
             "rule" if rule_triggered else \
             "ml" if ml_class == 1 else "none"

    confidence = ml_conf if not rule_triggered else max(ml_conf, 0.90)

    return {
        "attack_type": "DDoS" if is_attack else None,
        "confidence":  round(confidence, 4),
        "method":      method,
        "details":     "; ".join(rule_details) if rule_details else f"ML conf={ml_conf:.3f}",
    }
