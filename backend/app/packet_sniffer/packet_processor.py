"""
FusionGuardNet – Packet Processor
Converts raw Scapy packets (or simulated dicts) into normalised feature dicts
that the detectors and feature extractor can consume.
"""

import time
import random
import struct
from typing import Any, Dict, Optional


def process_scapy_packet(pkt: Any) -> Optional[Dict[str, Any]]:
    """
    Extract fields from a live Scapy packet object.
    Returns None if packet cannot be parsed.
    """
    try:
        result: Dict[str, Any] = {
            "timestamp":       time.time(),
            "src_ip":          "",
            "dst_ip":          "",
            "src_port":        0,
            "dst_port":        0,
            "protocol":        "other",
            "payload_len":     0,
            "flag_syn":        False,
            "flag_ack":        False,
            "flag_fin":        False,
            "flag_rst":        False,
            "inter_arrival_ms": 0,
            "raw_bytes":       b"",
        }

        # IP layer
        if pkt.haslayer("IP"):
            result["src_ip"]  = pkt["IP"].src
            result["dst_ip"]  = pkt["IP"].dst
            result["raw_bytes"] = bytes(pkt["IP"].payload)[:200]

        # TCP
        if pkt.haslayer("TCP"):
            result["protocol"]  = "tcp"
            result["src_port"]  = pkt["TCP"].sport
            result["dst_port"]  = pkt["TCP"].dport
            flags               = pkt["TCP"].flags
            result["flag_syn"]  = bool(flags & 0x02)
            result["flag_ack"]  = bool(flags & 0x10)
            result["flag_fin"]  = bool(flags & 0x01)
            result["flag_rst"]  = bool(flags & 0x04)
            if pkt.haslayer("Raw"):
                result["payload_len"] = len(pkt["Raw"].load)

        # UDP
        elif pkt.haslayer("UDP"):
            result["protocol"] = "udp"
            result["src_port"] = pkt["UDP"].sport
            result["dst_port"] = pkt["UDP"].dport
            result["payload_len"] = pkt["UDP"].len

        # ICMP
        elif pkt.haslayer("ICMP"):
            result["protocol"] = "icmp"

        return result

    except Exception:
        return None


def simulate_packet(attack_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a synthetic packet dict for simulation/testing.

    attack_type: "ddos" | "port_scan" | "brute_force" | "malware" | "sqli" | None
    """
    rng = random.Random()
    base: Dict[str, Any] = {
        "timestamp":        time.time(),
        "src_ip":           f"192.168.{rng.randint(0,255)}.{rng.randint(1,254)}",
        "dst_ip":           "10.0.0.1",
        "src_port":         rng.randint(1024, 65535),
        "dst_port":         rng.choice([80, 443, 22, 8080, 3306]),
        "protocol":         rng.choice(["tcp", "udp"]),
        "payload_len":      rng.randint(40, 1400),
        "flag_syn":         False,
        "flag_ack":         True,
        "inter_arrival_ms": rng.uniform(10, 500),
        "raw_bytes":        bytes(rng.randint(0, 255) for _ in range(100)),
    }

    if attack_type == "ddos":
        base["src_ip"]           = f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
        base["flag_syn"]         = True
        base["flag_ack"]         = False
        base["inter_arrival_ms"] = rng.uniform(0.1, 2.0)
        base["payload_len"]      = rng.randint(40, 64)

    elif attack_type == "port_scan":
        base["dst_port"]         = rng.randint(1, 1024)
        base["flag_syn"]         = True
        base["flag_ack"]         = False
        base["inter_arrival_ms"] = rng.uniform(1, 20)

    elif attack_type == "brute_force":
        base["dst_port"]         = 22
        base["flag_syn"]         = True
        base["inter_arrival_ms"] = rng.uniform(200, 800)

    elif attack_type == "malware":
        base["dst_port"]         = rng.choice([4444, 1337, 31337, 6667])
        # high-entropy payload
        base["raw_bytes"]        = bytes(rng.randint(0, 255) for _ in range(100))

    elif attack_type == "sqli":
        payload = b"' OR '1'='1'; DROP TABLE users; --"
        base["dst_port"]   = 80
        base["raw_bytes"]  = payload
        base["payload"]    = payload.decode()

    return base
