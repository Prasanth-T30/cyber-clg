"""
FusionGuardNet – LSTM Model
Long Short-Term Memory network for detecting temporal/sequential attack patterns.
Used for: Port Scanning (sequential port access), Brute-Force (login sequences).

Architecture:
  Input  (batch, SEQ_LEN, FEATURES)
  → LSTM(128, return_sequences=True)
  → Dropout(0.3)
  → LSTM(64)
  → Dense(32, relu)
  → Dense(num_classes, softmax)
"""

import os
import logging
import numpy as np
from typing import Tuple

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
SEQ_LEN   = 10    # number of packets / events in one window
N_FEATURES = 6    # per-event feature count (see feature_extractor.py)
NUM_CLASSES = 2   # 0 = benign, 1 = attack
MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved", "lstm_model.keras")


# ── Model builder ────────────────────────────────────────────────────────────

def build_lstm(
    seq_len: int = SEQ_LEN,
    n_features: int = N_FEATURES,
    num_classes: int = NUM_CLASSES,
) -> tf.keras.Model:
    inp = layers.Input(shape=(seq_len, n_features), name="event_sequence")

    x = layers.LSTM(128, return_sequences=True)(inp)
    x = layers.Dropout(0.3)(x)
    x = layers.LSTM(64)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(32, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(num_classes, activation="softmax", name="output")(x)

    model = models.Model(inputs=inp, outputs=out, name="FusionGuardNet_LSTM")
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── Synthetic data generator ─────────────────────────────────────────────────

def generate_synthetic_sequences(
    n_samples: int = 2000,
    seq_len: int = SEQ_LEN,
    n_features: int = N_FEATURES,
    seed: int = 7,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Feature columns (per event):
      0: dst_port (normalised 0-1)
      1: inter_arrival_ms (normalised)
      2: payload_len (normalised)
      3: protocol_id (tcp=0.5, udp=0.25, icmp=0.1 …)
      4: flag_syn (0/1)
      5: flag_ack (0/1)

    Benign:  random ports, varied arrival times, mixed protocols.
    Attack:  port-scan pattern — monotonically increasing ports, short gaps;
             brute-force pattern — same port (22/23/80), very short gaps, SYN=1.
    """
    rng = np.random.default_rng(seed)
    X, y = [], []

    half = n_samples // 2

    # Benign sequences
    for _ in range(half):
        seq = rng.random((seq_len, n_features)).astype(np.float32)
        X.append(seq)
        y.append(0)

    # Attack sequences  (alternating port-scan / brute-force style)
    for i in range(half):
        seq = np.zeros((seq_len, n_features), dtype=np.float32)
        if i % 2 == 0:
            # Port scan: rising ports, short inter-arrival
            ports = np.linspace(0.0, 1.0, seq_len)
            seq[:, 0] = ports
            seq[:, 1] = rng.uniform(0.0, 0.05, seq_len)  # very short gaps
            seq[:, 4] = 1.0                               # SYN flag set
        else:
            # Brute-force: same port repeatedly, very short gaps
            seq[:, 0] = 0.022                             # port 22 normalised
            seq[:, 1] = rng.uniform(0.0, 0.02, seq_len)
            seq[:, 4] = 1.0
            seq[:, 5] = 0.0
        X.append(seq)
        y.append(1)

    X = np.array(X)
    y = np.array(y)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


# ── Train / load helpers ─────────────────────────────────────────────────────

def train_lstm(force_retrain: bool = False) -> tf.keras.Model:
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if not force_retrain and os.path.exists(MODEL_PATH):
        logger.info("Loading pre-trained LSTM from %s", MODEL_PATH)
        return tf.keras.models.load_model(MODEL_PATH)

    logger.info("Training LSTM model on synthetic data …")
    X, y = generate_synthetic_sequences(n_samples=3000)
    split = int(0.8 * len(X))

    model = build_lstm()
    cb = [
        callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]
    model.fit(
        X[:split], y[:split],
        validation_data=(X[split:], y[split:]),
        epochs=30,
        batch_size=64,
        callbacks=cb,
        verbose=0,
    )
    logger.info("LSTM training complete. Saved to %s", MODEL_PATH)
    return model


def predict_lstm(
    model: tf.keras.Model, sequence: np.ndarray
) -> Tuple[int, float]:
    """
    Run inference on a single event sequence.

    Args:
        model: trained Keras model
        sequence: numpy array of shape (SEQ_LEN, N_FEATURES)

    Returns:
        (predicted_class, confidence)  class 1 = attack
    """
    inp = sequence.astype(np.float32).reshape(1, SEQ_LEN, N_FEATURES)
    probs = model.predict(inp, verbose=0)[0]
    pred_class = int(np.argmax(probs))
    return pred_class, float(probs[pred_class])
