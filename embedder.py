from deepface import DeepFace
import numpy as np

def get_embedding(img_path):
    try:
        result = DeepFace.represent(
            img_path=img_path,
            model_name="ArcFace",
            enforce_detection=False
        )
        return np.array(result[0]['embedding'])
    except Exception as e:
        print(f"Embedding error for {img_path}: {e}")
        return None