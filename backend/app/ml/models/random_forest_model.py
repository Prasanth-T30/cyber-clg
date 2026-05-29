"""
FusionGuardNet – Random Forest Model
Ensemble classifier on flow-level statistical features.
Used primarily for: DDoS detection, general anomaly scoring.

Flow features (10 total):
  0  pkt_count        – packets in the flow window
  1  byte_count       – total bytes
  2  pkt_rate         – packets per second
  3  byte_rate        – bytes per second
  4  avg_pkt_len      – mean packet size
  5  std_pkt_len      – std-dev of packet sizes
  6  unique_src_ips   – distinct source IPs
  7  unique_dst_ports – distinct destination ports
  8  syn_ratio        – SYN packets / total packets
  9  icmp_ratio       – ICMP packets / total packets
"""

import os
import logging
import pickle
import numpy as np
from typing import Tuple

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)

MODEL_PATH  = os.path.join(os.path.dirname(__file__), "saved", "rf_pipeline.pkl")
N_FEATURES  = 10
NUM_CLASSES = 2   # 0 = benign, 1 = attack


# ── Synthetic data generator ─────────────────────────────────────────────────

def generate_flow_data(
    n_samples: int = 2000, seed: int = 99
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic flow-level feature vectors.

    Benign flows:  low rates, few source IPs, varied ports.
    DDoS flows:    very high pkt_rate / byte_rate, many unique src IPs,
                   high SYN ratio, concentrated dst port.
    """
    rng = np.random.default_rng(seed)
    half = n_samples // 2

    # Benign
    benign = np.column_stack([
        rng.integers(10, 200, half),          # pkt_count
        rng.integers(1000, 50000, half),       # byte_count
        rng.uniform(1, 50, half),              # pkt_rate
        rng.uniform(100, 5000, half),          # byte_rate
        rng.uniform(64, 1500, half),           # avg_pkt_len
        rng.uniform(0, 200, half),             # std_pkt_len
        rng.integers(1, 5, half),              # unique_src_ips
        rng.integers(1, 20, half),             # unique_dst_ports
        rng.uniform(0, 0.3, half),             # syn_ratio
        rng.uniform(0, 0.1, half),             # icmp_ratio
    ]).astype(np.float32)

    # DDoS / Attack
    attack = np.column_stack([
        rng.integers(500, 5000, half),         # pkt_count – very high
        rng.integers(100000, 1000000, half),   # byte_count
        rng.uniform(500, 10000, half),         # pkt_rate – very high
        rng.uniform(50000, 500000, half),      # byte_rate
        rng.uniform(40, 80, half),             # avg_pkt_len – small (flood)
        rng.uniform(0, 20, half),              # std_pkt_len – uniform
        rng.integers(50, 500, half),           # unique_src_ips – many
        rng.integers(1, 3, half),              # unique_dst_ports – few
        rng.uniform(0.7, 1.0, half),           # syn_ratio – high
        rng.uniform(0, 0.05, half),            # icmp_ratio
    ]).astype(np.float32)

    X = np.vstack([benign, attack])
    y = np.array([0] * half + [1] * half)

    idx = rng.permutation(len(X))
    return X[idx], y[idx]


# ── Train / load helpers ─────────────────────────────────────────────────────

def build_rf_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])


def train_rf(force_retrain: bool = False) -> Pipeline:
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if not force_retrain and os.path.exists(MODEL_PATH):
        logger.info("Loading pre-trained RF pipeline from %s", MODEL_PATH)
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    logger.info("Training Random Forest on synthetic flow data …")
    X, y = generate_flow_data(n_samples=4000)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    pipe = build_rf_pipeline()
    pipe.fit(X_train, y_train)

    report = classification_report(y_val, pipe.predict(X_val), target_names=["benign", "attack"])
    logger.info("RF validation report:\n%s", report)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipe, f)
    logger.info("RF pipeline saved to %s", MODEL_PATH)
    return pipe


def predict_rf(pipeline: Pipeline, flow_features: np.ndarray) -> Tuple[int, float]:
    """
    Args:
        pipeline: trained sklearn Pipeline
        flow_features: 1-D array of length N_FEATURES

    Returns:
        (predicted_class, confidence)
    """
    x = flow_features.astype(np.float32).reshape(1, -1)
    pred_class = int(pipeline.predict(x)[0])
    proba = pipeline.predict_proba(x)[0]
    confidence = float(proba[pred_class])
    return pred_class, confidence
