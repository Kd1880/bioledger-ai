import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from flask import Flask, request, jsonify
from ai_module import analyze_image
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def hash_image(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Get AI result
    result = analyze_image(filepath)

    # Get image hash (for blockchain)
    image_hash = hash_image(filepath)

    return jsonify({
        "trust_score": result["trust_score"],
        "anomaly": result["anomaly"],
        "cosine_distance": result["cosine_distance"],
        "status": result["status"],
        "image_hash": image_hash,        # Backend sends this to blockchain
        "filename": file.filename
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "AI server running"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)