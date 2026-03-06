import os
import numpy as np
import pickle
from sklearn.cluster import DBSCAN
from embedder import get_embedding

AUTHORIZED_DIR = "dataset/authorized"

def build_cluster():
    print("Starting cluster build...")
    embeddings = []

    files = [f for f in os.listdir(AUTHORIZED_DIR) 
             if f.endswith((".jpg", ".jpeg", ".png"))]
    
    print(f"Found {len(files)} images in authorized folder")

    for filename in files:
        full_path = os.path.join(AUTHORIZED_DIR, filename)
        print(f"  Processing: {filename}")
        emb = get_embedding(full_path)
        if emb is not None:
            embeddings.append(emb)

    print(f"\nSuccessfully embedded: {len(embeddings)} faces")

    if len(embeddings) < 3:
        print("ERROR: Need at least 3 valid face images")
        return False

    embeddings = np.array(embeddings)

    clustering = DBSCAN(eps=10.0, min_samples=2).fit(embeddings)
    labels = clustering.labels_

    print(f"DBSCAN labels: {set(labels)}")

    main_mask = labels == 0
    main_cluster = embeddings[main_mask]

    if len(main_cluster) == 0:
        # If DBSCAN fails, just use all embeddings
        print("DBSCAN found no cluster, using all embeddings as cluster")
        main_cluster = embeddings

    centroid = np.mean(main_cluster, axis=0)

    with open("centroid.pkl", "wb") as f:
        pickle.dump(centroid, f)

    print(f"\nSUCCESS: Cluster built with {len(main_cluster)} faces")
    print("centroid.pkl saved")
    return True

if __name__ == "__main__":
    build_cluster()