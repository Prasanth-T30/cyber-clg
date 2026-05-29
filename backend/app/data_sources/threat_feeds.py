"""
FusionGuardNet – Threat Feeds Data Source
Maintains in-memory blocklists and provides a ThreatFeedSignal for the Fusion Layer.
In production, these would be refreshed from real threat intelligence sources
(e.g., AbuseIPDB, VirusTotal, Emerging Threats).
"""

import logging
from typing import Optional, Set

from app.ml.fusion_layer import ThreatFeedSignal

logger = logging.getLogger(__name__)

# ── Simulated blocklists ─────────────────────────────────────────────────────

BLOCKED_IPS: Set[str] = {
    "185.220.101.0",
    "45.33.32.156",
    "198.199.94.50",
    "192.241.214.62",
    "104.236.246.117",
}

BLOCKED_DOMAINS: Set[str] = {
    "malware-c2.example.com",
    "phishing-site.xyz",
    "botnet-ctrl.net",
    "exploit-kit.ru",
}

KNOWN_MALWARE_HASHES: Set[str] = {
    "d41d8cd98f00b204e9800998ecf8427e",  # example MD5
    "aabbccddeeff00112233445566778899",
}


# ── Lookup helpers ────────────────────────────────────────────────────────────

def check_ip(ip: str) -> bool:
    return ip in BLOCKED_IPS


def check_domain(domain: str) -> bool:
    return any(domain.endswith(d) for d in BLOCKED_DOMAINS)


def check_hash(file_hash: str) -> bool:
    return file_hash.lower() in KNOWN_MALWARE_HASHES


def get_signal(
    src_ip:      Optional[str] = None,
    domain:      Optional[str] = None,
    file_hash:   Optional[str] = None,
) -> ThreatFeedSignal:
    """Build a ThreatFeedSignal from IP / domain / hash lookups."""
    ip_hit   = check_ip(src_ip)   if src_ip   else False
    dom_hit  = check_domain(domain) if domain else False
    hash_hit = check_hash(file_hash) if file_hash else False

    score = 0.0
    if ip_hit:   score = min(score + 0.50, 1.0)
    if dom_hit:  score = min(score + 0.40, 1.0)
    if hash_hit: score = min(score + 0.60, 1.0)

    return ThreatFeedSignal(
        ip_in_blocklist     = ip_hit,
        domain_in_blocklist = dom_hit,
        known_malware_hash  = hash_hit,
        threat_score        = score,
    )


def add_blocked_ip(ip: str):
    BLOCKED_IPS.add(ip)
    logger.info("Added %s to IP blocklist", ip)


def add_blocked_domain(domain: str):
    BLOCKED_DOMAINS.add(domain)
    logger.info("Added %s to domain blocklist", domain)
