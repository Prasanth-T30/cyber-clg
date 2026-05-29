"""
FusionGuardNet – Fusion Layer
Aggregates signals from three data modalities:
  1. Network packets  (packet sniffer)
  2. System logs      (log ingestion)
  3. User behaviour   (behavioural analytics)
  4. Threat feeds     (external threat intelligence)

The fusion layer computes a combined threat score and decides whether
to escalate to the AI Detection Core.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Data models ──────────────────────────────────────────────────────────────

@dataclass
class NetworkSignal:
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    pkt_rate: float
    byte_rate: float
    syn_ratio: float
    unique_src_ips: int
    payload_sample: bytes = b""
    raw_packets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LogSignal:
    failed_logins: int = 0
    successful_logins: int = 0
    privilege_escalations: int = 0
    unusual_process_count: int = 0
    error_rate: float = 0.0


@dataclass
class BehaviourSignal:
    off_hours_access: bool = False
    unusual_volume: bool = False
    new_device: bool = False
    geo_anomaly: bool = False
    rapid_data_access: bool = False


@dataclass
class ThreatFeedSignal:
    ip_in_blocklist: bool = False
    domain_in_blocklist: bool = False
    known_malware_hash: bool = False
    threat_score: float = 0.0   # 0.0–1.0 from threat intelligence


@dataclass
class FusionResult:
    combined_score: float           # 0.0–1.0
    network_score: float
    log_score: float
    behaviour_score: float
    threat_feed_score: float
    escalate: bool                  # True → send to AI Detection Core
    explanation: str


# ── Scorer helpers ────────────────────────────────────────────────────────────

def _score_network(sig: NetworkSignal) -> float:
    score = 0.0
    if sig.pkt_rate > 500:    score += 0.35
    elif sig.pkt_rate > 100:  score += 0.15
    if sig.syn_ratio > 0.8:   score += 0.25
    if sig.unique_src_ips > 50: score += 0.20
    if sig.byte_rate > 100_000: score += 0.10
    if sig.dst_port in {22, 23, 3389, 445, 135}: score += 0.10
    return min(score, 1.0)


def _score_logs(sig: LogSignal) -> float:
    score = 0.0
    if sig.failed_logins > 10:          score += 0.40
    elif sig.failed_logins > 5:         score += 0.20
    if sig.privilege_escalations > 0:   score += 0.30
    if sig.unusual_process_count > 5:   score += 0.20
    if sig.error_rate > 0.5:            score += 0.10
    return min(score, 1.0)


def _score_behaviour(sig: BehaviourSignal) -> float:
    flags = [
        sig.off_hours_access,
        sig.unusual_volume,
        sig.new_device,
        sig.geo_anomaly,
        sig.rapid_data_access,
    ]
    return round(sum(flags) / len(flags), 4)


def _score_threat_feed(sig: ThreatFeedSignal) -> float:
    score = sig.threat_score
    if sig.ip_in_blocklist:     score = min(score + 0.40, 1.0)
    if sig.domain_in_blocklist: score = min(score + 0.30, 1.0)
    if sig.known_malware_hash:  score = min(score + 0.50, 1.0)
    return score


# ── Main fusion function ─────────────────────────────────────────────────────

WEIGHTS = {
    "network":     0.40,
    "log":         0.25,
    "behaviour":   0.15,
    "threat_feed": 0.20,
}

ESCALATION_THRESHOLD = 0.45   # combined score above this → send to AI core


def fuse(
    network:     Optional[NetworkSignal]    = None,
    logs:        Optional[LogSignal]        = None,
    behaviour:   Optional[BehaviourSignal]  = None,
    threat_feed: Optional[ThreatFeedSignal] = None,
) -> FusionResult:
    """
    Combine signals from all modalities into a single FusionResult.
    Missing modalities contribute a score of 0.
    """
    net_score  = _score_network(network)      if network      else 0.0
    log_score  = _score_logs(logs)            if logs         else 0.0
    beh_score  = _score_behaviour(behaviour)  if behaviour    else 0.0
    tf_score   = _score_threat_feed(threat_feed) if threat_feed else 0.0

    combined = (
        WEIGHTS["network"]     * net_score +
        WEIGHTS["log"]         * log_score +
        WEIGHTS["behaviour"]   * beh_score +
        WEIGHTS["threat_feed"] * tf_score
    )
    combined = round(combined, 4)
    escalate  = combined >= ESCALATION_THRESHOLD

    explanation = (
        f"Network:{net_score:.2f} Logs:{log_score:.2f} "
        f"Behaviour:{beh_score:.2f} ThreatFeed:{tf_score:.2f} "
        f"→ Combined:{combined:.2f} {'[ESCALATE]' if escalate else '[OK]'}"
    )
    logger.debug("Fusion: %s", explanation)

    return FusionResult(
        combined_score=combined,
        network_score=net_score,
        log_score=log_score,
        behaviour_score=beh_score,
        threat_feed_score=tf_score,
        escalate=escalate,
        explanation=explanation,
    )
