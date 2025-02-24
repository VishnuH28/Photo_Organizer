import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0)  # CPU; use -1 for GPU if available

def get_embeddings(image):
    try:
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = app.get(img_rgb)
        if not faces:
            return None
        best_face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        return best_face.embedding
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return None