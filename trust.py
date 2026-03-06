from scipy.spatial.distance import cosine
import pickle
import numpy as np
from embedder import get_embedding

ANOMALY_THRESHOLD = 0.4  # cosine distance above this = anomaly

def compute_trust_score(img_path):
    # Load centroid
    try:
        with open("centroid.pkl", "rb") as f:
            centroid = pickle.load(f)
    except FileNotFoundError:
        return {
            "trust_score": 0,
            "anomaly": True,
            "error": "Run build_cluster.py first"
        }

    # Get embedding
    embedding = get_embedding(img_path)

    if embedding is None:
        return {
            "trust_score": 0,
            "anomaly": True,
            "reason": "No face detected in image"
        }

    # Cosine distance 0.0 = identical, 1.0 = completely different
    cos_dist = float(cosine(embedding, centroid))

    # Fix: scale within 0-1 range properly
    # Authorized faces: 0.15-0.20 → should give 80-85
    # Unknown faces:    0.70-0.99 → should give 0-30
    trust_score = round(max(0, min(100, (1 - cos_dist) * 100)), 2)

    anomaly = cos_dist > ANOMALY_THRESHOLD

    return {
        "trust_score": trust_score,
        "anomaly": bool(anomaly),
        "cosine_distance": round(cos_dist, 4),
        "status": "SUSPICIOUS" if anomaly else "AUTHORIZED"
    }