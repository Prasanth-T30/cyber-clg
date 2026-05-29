"""
FusionGuardNet – Detections Router
Manually trigger detections (useful for demos / testing).
"""

import uuid, time
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.ml.detection import (
    ddos_detector,
    port_scan_detector,
    brute_force_detector,
    malware_detector,
    sql_injection_detector,
)
from app.ml.feature_extractor import extract_flow_features_from_dict
from app.packet_sniffer.sniffer import RECENT_PACKETS, RECENT_ALERTS
from app.packet_sniffer.packet_processor import simulate_packet

router = APIRouter(prefix="/detect", tags=["detections"])


# ── Request models ────────────────────────────────────────────────────────────

class FlowRequest(BaseModel):
    pkt_count:        int   = 100
    byte_count:       int   = 10000
    pkt_rate:         float = 50.0
    byte_rate:        float = 5000.0
    avg_pkt_len:      float = 100.0
    std_pkt_len:      float = 20.0
    unique_src_ips:   int   = 2
    unique_dst_ports: int   = 5
    syn_ratio:        float = 0.1
    icmp_ratio:       float = 0.0


class PacketRequest(BaseModel):
    dst_port:    int    = 80
    src_ip:      str    = "192.168.1.100"
    dst_ip:      str    = "10.0.0.1"
    payload:     str    = ""
    raw_bytes_b64: Optional[str] = None


class SimulateRequest(BaseModel):
    attack_type: Optional[str] = None   # ddos | port_scan | brute_force | malware | sqli


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/ddos")
async def detect_ddos(flow: FlowRequest):
    result = ddos_detector.detect(flow.model_dump())
    return {"input": flow.model_dump(), "result": result}


@router.post("/sqli")
async def detect_sqli(req: PacketRequest):
    result = sql_injection_detector.detect({
        "payload": req.payload,
        "path":    "",
        "method":  "POST",
    })
    return {"input": req.model_dump(), "result": result}


@router.post("/malware")
async def detect_malware(req: PacketRequest):
    result = malware_detector.detect({
        "dst_port":  req.dst_port,
        "src_ip":    req.src_ip,
        "dst_ip":    req.dst_ip,
        "raw_bytes": req.payload.encode() if req.payload else b"\x00" * 100,
    })
    return {"input": req.model_dump(), "result": result}


@router.post("/simulate")
async def simulate_attack(req: SimulateRequest):
    """Inject a synthetic attack packet into the pipeline and return its detection."""
    pkt = simulate_packet(attack_type=req.attack_type)

    # Run detectors directly without the async sniffer loop
    results: Dict[str, Any] = {}

    if req.attack_type in (None, "malware"):
        results["malware"] = malware_detector.detect(pkt)

    if req.attack_type in (None, "sqli"):
        results["sqli"] = sql_injection_detector.detect({
            "payload": pkt.get("payload", ""),
            "path": "",
        })

    if req.attack_type == "ddos" or req.attack_type is None:
        flow = {
            "pkt_count": 1000, "byte_count": 500000,
            "pkt_rate": 2000, "byte_rate": 200000,
            "avg_pkt_len": 50, "std_pkt_len": 5,
            "unique_src_ips": 200, "unique_dst_ports": 1,
            "syn_ratio": 0.9, "icmp_ratio": 0.0,
        }
        results["ddos"] = ddos_detector.detect(flow)

    alert_id = str(uuid.uuid4())
    detected = [k for k, v in results.items() if v.get("attack_type")]

    alert = {
        "id":          alert_id,
        "timestamp":   time.time(),
        "attack_type": req.attack_type or (detected[0] if detected else "Unknown"),
        "src_ip":      pkt.get("src_ip", "0.0.0.0"),
        "dst_ip":      pkt.get("dst_ip", "10.0.0.1"),
        "confidence":  max((r.get("confidence", 0) for r in results.values()), default=0),
        "method":      "simulation",
        "severity":    "high",
        "status":      "active",
        "details":     f"Simulated {req.attack_type or 'random'} attack",
    }
    RECENT_ALERTS.appendleft(alert)

    return {"packet": pkt, "detections": results, "alert": alert}
