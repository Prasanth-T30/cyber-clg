"""
FusionGuardNet – CNN Model
Convolutional Neural Network for detecting spatial patterns in packet byte sequences.
Used primarily for: Malware Traffic detection, SQL Injection detection.

Architecture:
  Input (batch, SEQ_LEN, 1)
  → Conv1D(64, 3, relu) → MaxPool1D(2)
  → Conv1D(128, 3, relu) → MaxPool1D(2)
  → GlobalAveragePooling1D
  → Dense(64, relu) → Dropout(0.3)
  → Dense(num_classes, softmax)
"""

import os
import logging
import numpy as np
from typing import Optional, Tuple

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
SEQ_LEN = 100          # bytes per packet window
NUM_CLASSES = 2        # 0 = benign, 1 = malicious
MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved", "cnn_model.keras")


# ── Model builder ────────────────────────────────────────────────────────────

def build_cnn(seq_len: int = SEQ_LEN, num_classes: int = NUM_CLASSES) -> tf.keras.Model:
    """Build and compile the CNN model."""
    inp = layers.Input(shape=(seq_len, 1), name="byte_sequence")

    x = layers.Conv1D(64, kernel_size=3, activation="relu", padding="same")(inp)
    x = layers.MaxPooling1D(pool_size=2)(x)
    x = layers.BatchNormalization()(x)

    x = layers.Conv1D(128, kernel_size=3, activation="relu", padding="same")(x)
    x = layers.MaxPooling1D(pool_size=2)(x)
    x = layers.BatchNormalization()(x)

    x = layers.Conv1D(64, kernel_size=3, activation="relu", padding="same")(x)
    x = layers.GlobalAveragePooling1D()(x)

    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(num_classes, activation="softmax", name="output")(x)

    model = models.Model(inputs=inp, outputs=out, name="FusionGuardNet_CNN")
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── Synthetic data generator ─────────────────────────────────────────────────

def generate_synthetic_data(
    n_samples: int = 2000,
    seq_len: int = SEQ_LEN,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic packet byte sequences for training.

    Benign packets:  uniform random bytes (0–127), low entropy patterns.
    Malicious packets: repetitive patterns + high-value byte spikes.
    """
    rng = np.random.default_rng(seed)
    X, y = [], []

    half = n_samples // 2

    # Benign samples
    for _ in range(half):
        seq = rng.integers(0, 128, size=seq_len).astype(np.float32) / 255.0
        X.append(seq)
        y.append(0)

    # Malicious samples – inject repetitive / anomalous patterns
    for _ in range(half):
        seq = rng.integers(0, 256, size=seq_len).astype(np.float32) / 255.0
        # inject a high-value spike window (simulates shellcode / payload marker)
        start = rng.integers(0, seq_len - 20)
        seq[start : start + 20] = rng.uniform(0.85, 1.0, size=20)
        X.append(seq)
        y.append(1)

    X = np.array(X)[..., np.newaxis]  # (N, SEQ_LEN, 1)
    y = np.array(y)

    # Shuffle
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


# ── Train / load helpers ─────────────────────────────────────────────────────

def train_cnn(force_retrain: bool = False) -> tf.keras.Model:
    """Train the CNN on synthetic data, or load from disk if already trained."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if not force_retrain and os.path.exists(MODEL_PATH):
        logger.info("Loading pre-trained CNN from %s", MODEL_PATH)
        return tf.keras.models.load_model(MODEL_PATH)

    logger.info("Training CNN model on synthetic data …")
    X, y = generate_synthetic_data(n_samples=3000)
    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    model = build_cnn()
    cb = [
        callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=64,
        callbacks=cb,
        verbose=0,
    )
    logger.info("CNN training complete. Saved to %s", MODEL_PATH)
    return model


def predict_cnn(model: tf.keras.Model, byte_sequence: np.ndarray) -> Tuple[int, float]:
    """
    Run inference on a single packet byte sequence.

    Args:
        model: trained Keras model
        byte_sequence: 1-D numpy array of length SEQ_LEN (raw bytes 0–255)

    Returns:
        (predicted_class, confidence)  where class 1 = malicious
    """
    seq = byte_sequence.astype(np.float32) / 255.0
    # Pad or truncate to SEQ_LEN
    if len(seq) < SEQ_LEN:
        seq = np.pad(seq, (0, SEQ_LEN - len(seq)))
    else:
        seq = seq[:SEQ_LEN]
    inp = seq.reshape(1, SEQ_LEN, 1)
    probs = model.predict(inp, verbose=0)[0]
    pred_class = int(np.argmax(probs))
    confidence = float(probs[pred_class])
    return pred_class, confidence
