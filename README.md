# BioLedger — AI Biometric Verification Pipeline

> **AI Engineer Module** | Phantasia 3.0 Hackathon — 2nd Place, AI + Blockchain Track

This repository contains the complete **AI pipeline** I built as the AI Engineer for BioLedger — a decentralized biometric verification system. The pipeline takes a face image, generates a 512-dimensional embedding using ArcFace, computes a trust score via cosine similarity, and exposes everything through a Flask REST API with Keccak-256 image hashing for blockchain integration.

> 🔗 Full project (blockchain + backend + frontend): [phantasia-bioledger](https://github.com/Kd1880/phantasia-bioledger)

---

## What This Repo Contains

This is **only the AI layer** of BioLedger:

```
✅ Face embedding extraction     (ArcFace via DeepFace)
✅ Authorized cluster building   (DBSCAN)
✅ Trust score computation       (Cosine similarity)
✅ Anomaly/poison detection      (Threshold-based flagging)
✅ Flask REST API                (with Keccak-256 hashing)
✅ End-to-end pipeline test
```

The blockchain smart contracts, Web3 integration, and frontend live in the main repo linked above.

---

##  Problem This Solves

Biometric systems suffer from **data poisoning** — where malicious face images are injected into training/inference pipelines to corrupt model behavior. BioLedger's AI layer detects these poisoned inputs in real time by:

1. Modeling what "authorized" faces look like in embedding space
2. Flagging any input that deviates significantly from that cluster
3. Returning a trust score that the blockchain layer logs immutably on-chain

---

##  How the AI Pipeline Works

```
Input Image
     │
     ▼
┌──────────────────────────────┐
│  ArcFace Pretrained Model    │
│  512-dim facial embedding    │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  Cosine Similarity           │
│  vs. Authorized Centroid     │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  Trust Score (0–100)         │
│  Anomaly Flag (True/False)   │
│  Status (AUTHORIZED /        │
│          SUSPICIOUS)         │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  Flask REST API              │
│  + Keccak-256 image hash     │
│  → returned to blockchain    │
└──────────────────────────────┘
```

---

## Project Structure

```
bioledger-ai/
│
├── dataset/
│   ├── authorized/        ← 15–20 images of authorized person
│   ├── unknown/           ← Unknown faces for testing
│   └── poison/            ← Adversarial faces for demo
│
├── embedder.py            ← ArcFace embedding extractor
├── build_cluster.py       ← Builds DBSCAN cluster + saves centroid
├── trust.py               ← Cosine similarity trust scoring
├── ai_module.py           ← Clean interface for inference
├── app.py                 ← Flask REST API
├── test_pipeline.py       ← Tests all 3 scenarios
├── centroid.pkl           ← Auto-generated after build_cluster.py
└── requirements.txt

>  `dataset/` and `centroid.pkl` are excluded from this repo via `.gitignore`. Download the dataset from the Kaggle link in Step 1 below.
```

---

## Setup

### Requirements
- Python 3.8 – 3.10
- pip

### Install

```bash
git clone https://github.com/Kd1880/bioledger-ai.git
cd bioledger-ai

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### `requirements.txt`

```
deepface
scikit-learn
scipy
numpy
flask
tensorflow
opencv-python
tf-keras
```

---

##  Running the Pipeline

### Step 1 — Download Dataset

This project uses the **LFW (Labeled Faces in the Wild)** dataset from Kaggle.

 **Dataset Link:** [https://www.kaggle.com/datasets/jessicali9530/lfw-dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset)

> The dataset is not included in this repo due to size. Download it from Kaggle (free account required) and follow the steps below.

**After downloading and extracting:**

The dataset contains folders named by person — e.g. `George_W_Bush/`, `Colin_Powell/`, `Tony_Blair/` etc.

Copy images into the project folders like this:

```
dataset/authorized/   ← 15–20 images of ONE person (e.g. George_W_Bush)
dataset/unknown/      ← 5 images of different people (e.g. Colin_Powell)
dataset/poison/       ← 5 images for adversarial demo (e.g. Tony_Blair)
```

**Folder structure after setup:**

```
dataset/
├── authorized/
│   ├── George_W_Bush_0001.jpg
│   ├── George_W_Bush_0002.jpg
│   └── ...
├── unknown/
│   ├── Colin_Powell_0001.jpg
│   └── ...
└── poison/
    ├── Tony_Blair_0001.jpg
    └── ...
```

### Step 2 — Build Authorized Cluster

```bash
python build_cluster.py
```

This extracts ArcFace embeddings from all authorized images, runs DBSCAN clustering, computes the centroid, and saves it as `centroid.pkl`.

```
Building cluster from authorized faces...
Found 19 images in authorized folder
  Processing: face_0001.jpg ✓
  Processing: face_0002.jpg ✓
  ...
SUCCESS: Cluster built with 18 faces. centroid.pkl saved.
```

### Step 3 — Test the Pipeline

```bash
python test_pipeline.py
```

Expected output:

```
TESTING AUTHORIZED FACES
face_0001.jpg → trust_score: 85.41  anomaly: False  AUTHORIZED ✅
face_0002.jpg → trust_score: 83.80  anomaly: False  AUTHORIZED ✅

TESTING UNKNOWN FACES
unknown_0001.jpg → trust_score: 8.34   anomaly: True   SUSPICIOUS 🔴
unknown_0002.jpg → trust_score: 9.25   anomaly: True   SUSPICIOUS 🔴

TESTING POISON FACES
poison_0001.jpg → trust_score: 15.47  anomaly: True   SUSPICIOUS 🔴
poison_0002.jpg → trust_score: 6.99   anomaly: True   SUSPICIOUS 🔴
```

### Step 4 — Start the API

```bash
python app.py
```

Running at `http://127.0.0.1:5000`

---

## API Reference

### `POST /analyze`

**Request** — `multipart/form-data`:

| Field | Type | Description |
|---|---|---|
| `image` | File | Face image (.jpg / .png) |

**Response**:

```json
{
  "trust_score": 85.41,
  "anomaly": false,
  "cosine_distance": 0.1459,
  "status": "AUTHORIZED",
  "image_hash": "4f19991979a6138e73fa0a75a34bcab30eaea46d3670a7047a1451c1b178e91f",
  "filename": "face.jpg"
}
```

| Field | Type | Description |
|---|---|---|
| `trust_score` | float 0–100 | Higher = more trustworthy |
| `anomaly` | bool | True if input is suspicious |
| `cosine_distance` | float | Raw distance from authorized centroid |
| `status` | string | `AUTHORIZED` or `SUSPICIOUS` |
| `image_hash` | string | Keccak-256 hash sent to blockchain |

### `GET /health`

```json
{ "status": "AI server running" }
```

---

## Postman Testing

Import into Postman:

1. Method: `POST`
2. URL: `http://127.0.0.1:5000/analyze`
3. Body → `form-data`
4. Key: `image` (type: **File**)
5. Value: select any face image

---

## Results

Tested on LFW dataset — 30 facial images across 3 identity classes:

| Category | Cosine Distance | Trust Score | Detection |
|---|---|---|---|
| Authorized faces | 0.14 – 0.18 | 83 – 85 | ✅ AUTHORIZED |
| Unknown faces | 0.75 – 0.98 | 2 – 25 | 🔴 SUSPICIOUS |
| Poison faces | 0.84 – 0.93 | 6 – 15 | 🔴 SUSPICIOUS |

**Detection accuracy: 100% on test set**

---

##  Blockchain Integration

The API response is designed to feed directly into the blockchain layer:

```
image_hash   →  passed to logInference() in smart contract
trust_score  →  stored on-chain per inference
anomaly      →  if True, triggers updateReputation() penalty
```

**Why Keccak-256?**
Keccak-256 is Ethereum's native hashing algorithm — the same one used by `keccak256()` in Solidity. Using it in Python ensures the image fingerprint computed off-chain is directly verifiable on-chain without any conversion.

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|---|---|---|
| Face Embeddings | ArcFace (DeepFace) | State-of-the-art face recognition, 512-dim vectors |
| Clustering | DBSCAN (scikit-learn) | No predefined clusters, natural outlier detection |
| Similarity | Cosine Distance (scipy) | Better than Euclidean for high-dim embedding space |
| API | Flask | Lightweight, easy blockchain team integration |
| Hashing | Keccak-256 | Ethereum-native, on-chain compatible |

---

##  Key Technical Decisions

**Why ArcFace over FaceNet?**
ArcFace uses additive angular margin loss producing better-separated embeddings — authorized vs unknown faces show clearer cosine distance separation (0.15 vs 0.85+).

**Why DBSCAN over K-Means?**
DBSCAN doesn't require specifying the number of clusters and naturally identifies outliers as noise (label -1) — exactly what poisoned inputs are.

**Why Cosine Similarity over Euclidean Distance?**
In high-dimensional spaces (512-dim), Euclidean distance becomes unreliable. Cosine similarity measures the angle between vectors regardless of magnitude — more meaningful for comparing identity embeddings.


##  License

MIT License
