"""
FusionGuardNet - Feature Extractor
Converts raw packet dictionaries into normalised feature vectors
suitable for the CNN, LSTM, and Random Forest models.
"""

import numpy as np
from typing import Any, Dict, List


# -- Normalisation constants --
MAX_PORT      = 65535.0
MAX_PKT_LEN   = 1500.0
MAX_INTER_MS  = 5000.0
MAX_PKT_COUNT = 10000.0
MAX_BYTE_COUNT = 1_000_000.0
MAX_RATE      = 10000.0


def extract_packet_features(pkt: Dict[str, Any]) -> np.ndarray:
    """
    Return a 6-element float32 feature vector for a single packet dict.
    Expected keys (all optional - defaults to 0):
        dst_port, inter_arrival_ms, payload_len,
        protocol (tcp/udp/icmp/other), flag_syn, flag_ack
    """
    proto_map = {"tcp": 0.5, "udp": 0.25, "icmp": 0.1, "other": 0.05}
    proto = proto_map.get(str(pkt.get("protocol", "tcp")).lower(), 0.05)
    features = np.array([
        pkt.get("dst_port", 0)         / MAX_PORT,
        pkt.get("inter_arrival_ms", 0) / MAX_INTER_MS,
        pkt.get("payload_len", 0)      / MAX_PKT_LEN,
        proto,
        float(bool(pkt.get("flag_syn", False))),
        float(bool(pkt.get("flag_ack", False))),
    ], dtype=np.float32)
    return np.clip(features, 0.0, 1.0)


def build_sequence(packets: List[Dict[str, Any]], seq_len: int = 10) -> np.ndarray:
    """
    Build an (seq_len, 6) LSTM input array from a list of packet dicts.
    Pads with zeros if fewer than seq_len packets are provided.
    """
    vecs = [extract_packet_features(p) for p in packets[:seq_len]]
    if len(vecs) < seq_len:
        pad = [np.zeros(6, dtype=np.float32)] * (seq_len - len(vecs))
        vecs = vecs + pad
    return np.stack(vecs, axis=0)


def extract_byte_sequence(raw_bytes: bytes, seq_len: int = 100) -> np.ndarray:
    """
    Convert raw packet bytes to a normalised (seq_len,) float32 array.
    Used as input to the CNN.
    """
    arr = np.frombuffer(raw_bytes[:seq_len], dtype=np.uint8).astype(np.float32) / 255.0
    if len(arr) < seq_len:
        arr = np.pad(arr, (0, seq_len - len(arr)))
    return arr


def extract_flow_features(flow: Dict[str, Any]) -> np.ndarray:
    """
    Return a 10-element float32 feature vector for a flow summary dict.
    Expected keys: pkt_count, byte_count, pkt_rate, byte_rate,
        avg_pkt_len, std_pkt_len, unique_src_ips,
        unique_dst_ports, syn_ratio, icmp_ratio
    """
    features = np.array([
        flow.get("pkt_count",        0) / MAX_PKT_COUNT,
        flow.get("byte_count",       0) / MAX_BYTE_COUNT,
        flow.get("pkt_rate",         0) / MAX_RATE,
        flow.get("byte_rate",        0) / MAX_BYTE_COUNT,
        flow.get("avg_pkt_len",      0) / MAX_PKT_LEN,
        flow.get("std_pkt_len",      0) / MAX_PKT_LEN,
        flow.get("unique_src_ips",   0) / 1000.0,
        flow.get("unique_dst_ports", 0) / MAX_PORT,
        float(flow.get("syn_ratio",  0.0)),
        float(flow.get("icmp_ratio", 0.0)),
    ], dtype=np.float32)
    return np.clip(features, 0.0, 1.0)


def extract_flow_features_from_dict(flow: Dict[str, Any]) -> np.ndarray:
    """Alias that correctly reads from the 'flow' dict."""
    features = np.array([
        flow.get("pkt_count",        0) / MAX_PKT_COUNT,
        flow.get("byte_count",       0) / MAX_BYTE_COUNT,
        flow.get("pkt_rate",         0) / MAX_RATE,
        flow.get("byte_rate",        0) / MAX_BYTE_COUNT,
        flow.get("avg_pkt_len",      0) / MAX_PKT_LEN,
        flow.get("std_pkt_len",      0) / MAX_PKT_LEN,
        flow.get("unique_src_ips",   0) / 1000.0,
        flow.get("unique_dst_ports", 0) / MAX_PORT,
        float(flow.get("syn_ratio",  0.0)),
        float(flow.get("icmp_ratio", 0.0)),
    ], dtype=np.float32)
    return np.clip(features, 0.0, 1.0)
