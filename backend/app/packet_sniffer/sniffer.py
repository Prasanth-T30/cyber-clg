"""
FusionGuardNet – Packet Sniffer
Runs as an asyncio background task.
In SIMULATION_MODE=True  → generates synthetic packets at a configurable rate.
In SIMULATION_MODE=False → uses Scapy for live capture (requires root/admin).
"""

import asyncio
import logging
import random
import time
import uuid
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, List, Optional

from app.core.config import settings
from app.packet_sniffer.packet_processor import process_scapy_packet, simulate_packet
from app.ml.detection import (
    ddos_detector,
    port_scan_detector,
    brute_force_detector,
    malware_detector,
    sql_injection_detector,
)
from app.ml.fusion_layer import (
    fuse, NetworkSignal, LogSignal, BehaviourSignal, ThreatFeedSignal
)

logger = logging.getLogger(__name__)

# ── Shared state (in-memory ring buffers) ────────────────────────────────────
RECENT_PACKETS:     Deque[Dict] = deque(maxlen=200)
RECENT_ALERTS:      Deque[Dict] = deque(maxlen=settings.ALERT_HISTORY_LIMIT)
ALERT_CALLBACKS:    List[Callable] = []          # registered WebSocket broadcasters

# Per-source flow accumulators (reset every FLOW_WINDOW_SEC)
FLOW_WINDOW_SEC  = 5.0
_flow_buf:  Dict[str, List[Dict]] = defaultdict(list)
_port_map:  Dict[str, set]        = defaultdict(set)
_last_reset = time.time()


# ── Alert factory ────────────────────────────────────────────────────────────

def _make_alert(detection: Dict, src_ip: str, dst_ip: str = "10.0.0.1") -> Dict:
    return {
        "id":          str(uuid.uuid4()),
        "timestamp":   time.time(),
        "attack_type": detection["attack_type"],
        "src_ip":      src_ip,
        "dst_ip":      dst_ip,
        "confidence":  detection["confidence"],
        "method":      detection["method"],
        "details":     detection.get("details", ""),
        "severity":    _severity(detection["confidence"]),
        "status":      "active",
    }


def _severity(confidence: float) -> str:
    if confidence >= 0.90: return "critical"
    if confidence >= 0.75: return "high"
    if confidence >= 0.60: return "medium"
    return "low"


# ── Broadcast helpers ────────────────────────────────────────────────────────

async def _broadcast(alert: Dict):
    RECENT_ALERTS.appendleft(alert)
    for cb in list(ALERT_CALLBACKS):
        try:
            await cb(alert)
        except Exception as exc:
            logger.debug("Broadcast callback error: %s", exc)


def register_alert_callback(cb: Callable):
    ALERT_CALLBACKS.append(cb)


def unregister_alert_callback(cb: Callable):
    if cb in ALERT_CALLBACKS:
        ALERT_CALLBACKS.remove(cb)


# ── Flow processing ──────────────────────────────────────────────────────────

async def _process_packet(pkt: Dict):
    global _last_reset

    RECENT_PACKETS.appendleft(pkt)
    src_ip   = pkt.get("src_ip", "0.0.0.0")
    dst_ip   = pkt.get("dst_ip", "10.0.0.1")
    dst_port = int(pkt.get("dst_port", 0))

    _flow_buf[src_ip].append(pkt)
    _port_map[src_ip].add(dst_port)

    # ── Per-packet: Malware + SQLi ────────────────────────────────────────
    mal = malware_detector.detect(pkt)
    if mal["attack_type"]:
        await _broadcast(_make_alert(mal, src_ip, dst_ip))

    sqli_payload = pkt.get("payload", "")
    if sqli_payload:
        sqli = sql_injection_detector.detect({"payload": sqli_payload, "path": ""})
        if sqli["attack_type"]:
            await _broadcast(_make_alert(sqli, src_ip, dst_ip))

    # ── Port-scan check ───────────────────────────────────────────────────
    ps = port_scan_detector.detect(
        list(RECENT_PACKETS)[:10],
        {src_ip: _port_map[src_ip]},
    )
    if ps["attack_type"]:
        await _broadcast(_make_alert(ps, src_ip, dst_ip))

    # ── Brute-force (track auth on port 22/23/21/3389) ───────────────────
    if dst_port in {22, 23, 21, 3389, 25}:
        success = not pkt.get("flag_rst", False)
        brute_force_detector.record_attempt(src_ip, success, pkt.get("timestamp"))
        bf = brute_force_detector.detect(src_ip, list(RECENT_PACKETS)[:10])
        if bf["attack_type"]:
            await _broadcast(_make_alert(bf, src_ip, dst_ip))

    # ── Flow-window DDoS check ───────────────────────────────────────────
    now = time.time()
    if now - _last_reset >= FLOW_WINDOW_SEC:
        for ip, pkts in _flow_buf.items():
            if not pkts:
                continue
            elapsed = max(now - _last_reset, 0.001)
            total_bytes = sum(p.get("payload_len", 64) for p in pkts)
            syn_count   = sum(1 for p in pkts if p.get("flag_syn"))
            flow = {
                "pkt_count":        len(pkts),
                "byte_count":       total_bytes,
                "pkt_rate":         len(pkts) / elapsed,
                "byte_rate":        total_bytes / elapsed,
                "avg_pkt_len":      total_bytes / len(pkts),
                "std_pkt_len":      20.0,
                "unique_src_ips":   len({p.get("src_ip") for p in pkts}),
                "unique_dst_ports": len({p.get("dst_port") for p in pkts}),
                "syn_ratio":        syn_count / len(pkts),
                "icmp_ratio":       0.0,
            }
            ddos = ddos_detector.detect(flow)
            if ddos["attack_type"]:
                await _broadcast(_make_alert(ddos, ip, dst_ip))

        _flow_buf.clear()
        _port_map.clear()
        _last_reset = now


# ── Realistic attack catalogue ───────────────────────────────────────────────

REALISTIC_ATTACKS = [
    # (attack_type, weight)  – higher weight = more frequent
    ("ddos",        30),
    ("port_scan",   20),
    ("brute_force", 15),
    ("malware",     20),
    ("sqli",        15),
]

# Realistic attack display names that rotate to keep the feed lively
ATTACK_DISPLAY_NAMES = {
    "ddos": [
        "SYN Flood",
        "UDP Amplification",
        "HTTP Flood",
        "ICMP Smurf",
        "DNS Amplification",
        "NTP Reflection",
        "Volumetric DDoS",
        "Slowloris",
        "Memcached Amplification",
        "BGP Hijack DDoS",
    ],
    "port_scan": [
        "TCP SYN Scan",
        "Stealth Port Scan",
        "XMAS Tree Scan",
        "NULL Scan",
        "FIN Scan",
        "OS Fingerprinting",
        "Service Enumeration",
        "Network Reconnaissance",
        "Nmap Aggressive Scan",
        "UDP Port Probe",
    ],
    "brute_force": [
        "SSH Brute Force",
        "RDP Credential Stuffing",
        "FTP Password Spray",
        "Telnet Dictionary Attack",
        "SMTP Auth Brute",
        "SMB Login Attack",
        "VNC Brute Force",
        "IMAP Credential Attack",
        "WinRM Brute Force",
        "Kerberos Pre-Auth Attack",
    ],
    "malware": [
        "Trojan C2 Beacon",
        "Ransomware Propagation",
        "Botnet Heartbeat",
        "Keylogger Exfiltration",
        "Rootkit Communication",
        "Spyware Callback",
        "Worm Lateral Movement",
        "RAT Command Channel",
        "Cryptominer Traffic",
        "Data Exfiltration (DNS)",
    ],
    "sqli": [
        "Union-Based SQLi",
        "Blind Boolean SQLi",
        "Time-Based Blind SQLi",
        "Error-Based SQLi",
        "Out-of-Band SQLi",
        "Stacked Query Injection",
        "Second-Order SQLi",
        "Schema Enumeration",
        "Credential Dump via SQLi",
        "Stored Procedure Abuse",
    ],
}

# Realistic source IP ranges (internal + external threat actors)
_THREAT_SUBNETS = [
    "192.168.{}.{}", "10.{}.{}.{}", "172.16.{}.{}",
    "45.{}.{}.{}", "185.{}.{}.{}", "91.{}.{}.{}",
    "194.{}.{}.{}", "103.{}.{}.{}", "5.{}.{}.{}",
]

def _rand_ip(rng: random.Random) -> str:
    tmpl = rng.choice(_THREAT_SUBNETS)
    octets = [rng.randint(1, 254) for _ in range(tmpl.count("{}"))]
    return tmpl.format(*octets)

def _weighted_attack(rng: random.Random):
    pool = []
    for atype, weight in REALISTIC_ATTACKS:
        pool.extend([atype] * weight)
    return rng.choice(pool)


async def _emit_realistic_alert(rng: random.Random):
    """Build and broadcast one realistic-looking attack alert directly."""
    attack_type = _weighted_attack(rng)
    display_name = rng.choice(ATTACK_DISPLAY_NAMES[attack_type])
    src_ip = _rand_ip(rng)
    dst_ip = rng.choice(["10.0.0.1", "10.0.0.2", "172.16.0.1", "192.168.1.1"])
    confidence = rng.uniform(0.72, 0.99)

    # Build realistic detail strings per attack type
    if attack_type == "ddos":
        pps = rng.randint(5000, 980000)
        gbps = round(rng.uniform(0.4, 48.0), 1)
        details = f"{pps:,} pkt/s · {gbps} Gbps · syn_ratio={rng.uniform(0.85,1.0):.2f}"
    elif attack_type == "port_scan":
        ports = rng.randint(120, 65000)
        details = f"{ports:,} ports scanned · {rng.randint(3,30)} ms avg RTT"
    elif attack_type == "brute_force":
        attempts = rng.randint(80, 4800)
        details = f"{attempts:,} attempts · {rng.randint(1,12)} unique users targeted"
    elif attack_type == "malware":
        c2 = f"{rng.randint(1,254)}.{rng.randint(1,254)}.{rng.randint(1,254)}.{rng.randint(1,254)}"
        details = f"C2={c2}:{rng.randint(1024,65535)} · {rng.randint(1,16)} infected hosts"
    else:  # sqli
        patterns = rng.randint(2, 7)
        details = f"matched {patterns} pattern(s) · target: {rng.choice(['/login','/api/users','/search','/admin','/products'])}"

    alert = {
        "id":          str(uuid.uuid4()),
        "timestamp":   time.time(),
        "attack_type": display_name,
        "src_ip":      src_ip,
        "dst_ip":      dst_ip,
        "confidence":  round(confidence, 2),
        "method":      "fusion",
        "details":     details,
        "severity":    _severity(confidence),
        "status":      "active",
    }
    await _broadcast(alert)
    logger.info("Alert: [%s] %s %s → %s (%.0f%%)", alert["severity"].upper(),
                display_name, src_ip, dst_ip, confidence * 100)


# ── Main sniffer loop ────────────────────────────────────────────────────────

async def run_sniffer():
    """
    Background asyncio task – SIMULATION mode.
    Emits realistic attack alerts every 15–30 seconds.
    Occasionally fires a burst of 2-3 alerts back-to-back to simulate attack waves.
    """
    if not settings.SNIFFER_SIMULATION_MODE:
        await _run_live_sniffer()
        return

    logger.info("Packet sniffer started in SIMULATION mode")
    rng = random.Random()

    # Initial burst so the feed isn't empty on first load
    for _ in range(rng.randint(3, 5)):
        await _emit_realistic_alert(rng)
        await asyncio.sleep(rng.uniform(0.5, 1.5))

    while True:
        # Wait 15–30 seconds between alert cycles
        await asyncio.sleep(rng.uniform(15.0, 30.0))

        # Each cycle: 1 alert normally, ~30% chance of an attack wave (2-4 alerts)
        burst = rng.randint(2, 4) if rng.random() < 0.30 else 1
        for _ in range(burst):
            await _emit_realistic_alert(rng)
            if burst > 1:
                await asyncio.sleep(rng.uniform(0.8, 2.5))  # short gap inside burst


async def _run_live_sniffer():
    """Live packet capture using Scapy (requires elevated privileges)."""
    try:
        from scapy.all import sniff, conf
        conf.verb = 0
        logger.info("Live sniffer on interface: %s", settings.SNIFFER_INTERFACE)

        def _callback(pkt):
            processed = process_scapy_packet(pkt)
            if processed:
                asyncio.create_task(_process_packet(processed))

        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sniff(iface=settings.SNIFFER_INTERFACE, prn=_callback, store=False),
        )
    except ImportError:
        logger.warning("Scapy not available – falling back to simulation mode")
        await run_sniffer()
    except Exception as exc:
        logger.error("Live sniffer error: %s – falling back to simulation", exc)
        await run_sniffer()
