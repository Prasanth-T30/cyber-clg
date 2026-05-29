"""
FusionGuardNet – SQL Injection Detector
Hybrid: regex rule-matching on HTTP payloads + CNN on character-level encoding.
Detects: classic SQLi, blind SQLi, UNION-based, error-based, time-based patterns.
"""

import re
import logging
import numpy as np
from typing import Any, Dict

from app.ml.models.cnn_model import train_cnn, predict_cnn

logger = logging.getLogger(__name__)

# ── SQLi regex signatures ────────────────────────────────────────────────────
SQLI_PATTERNS = [
    re.compile(r"(\s|'|\"|;|--|#)(OR|AND)\s+['\"0-9]",        re.IGNORECASE),
    re.compile(r"UNION\s+(ALL\s+)?SELECT",                      re.IGNORECASE),
    re.compile(r"(DROP|DELETE|INSERT|UPDATE|ALTER)\s+TABLE",    re.IGNORECASE),
    re.compile(r"EXEC(\s|\()+(S|X)P\w+",                        re.IGNORECASE),
    re.compile(r"(SLEEP|BENCHMARK|WAITFOR)\s*\(",               re.IGNORECASE),
    re.compile(r"(INFORMATION_SCHEMA|SYS\.TABLES|ALL_TABLES)",  re.IGNORECASE),
    re.compile(r"CHAR\(\d+\)",                                   re.IGNORECASE),
    re.compile(r"0x[0-9a-fA-F]{4,}"),
    re.compile(r"'(\s*)\bOR\b(\s*)'"),
    re.compile(r"--\s*$", re.MULTILINE),
]

SEQ_LEN   = 100   # characters encoded as bytes
_model    = None


def get_model():
    global _model
    if _model is None:
        _model = train_cnn()
    return _model


def _encode_payload(payload: str, seq_len: int = SEQ_LEN) -> np.ndarray:
    """Encode a string payload as a byte-value array for CNN input."""
    encoded = [min(ord(c), 255) for c in payload[:seq_len]]
    if len(encoded) < seq_len:
        encoded += [0] * (seq_len - len(encoded))
    return np.array(encoded, dtype=np.float32)


def detect(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Args:
        request: dict with keys:
                   payload  (str)  – URL-decoded query string / POST body
                   path     (str)  – request path
                   method   (str)

    Returns:
        detection result dict
    """
    payload = str(request.get("payload", "")) + " " + str(request.get("path", ""))
    payload = payload.strip()

    # ── Regex rule-based ───────────────────────────────────────────────────
    matched_patterns = []
    for pat in SQLI_PATTERNS:
        if pat.search(payload):
            matched_patterns.append(pat.pattern[:40])

    rule_triggered = len(matched_patterns) > 0

    # ── CNN inference on character encoding ───────────────────────────────
    byte_seq = _encode_payload(payload)
    ml_class, ml_conf = predict_cnn(get_model(), byte_seq)

    # ── Combined ───────────────────────────────────────────────────────────
    is_attack = rule_triggered or (ml_class == 1 and ml_conf >= 0.70)
    confidence = max(ml_conf, 0.95) if rule_triggered else ml_conf

    return {
        "attack_type": "SQL Injection" if is_attack else None,
        "confidence":  round(confidence, 4),
        "method":      "combined" if rule_triggered and ml_class == 1 else
                       "rule"     if rule_triggered else
                       "ml"       if ml_class == 1 else "none",
        "details": f"matched {len(matched_patterns)} pattern(s)" if matched_patterns
                   else f"CNN conf={ml_conf:.3f}",
        "patterns_matched": matched_patterns[:5],
    }
