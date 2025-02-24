from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from .face_embeddings import get_embeddings
from .find_embeddings import find_embeddings
from .new_face import save_new_face
from .update_face import update_face

app = FastAPI()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    embedding = get_embeddings(img)
    if embedding is None:
        return JSONResponse({"error": "No faces detected"}, status_code=400)

    req_id = f"rqid-upload-{int(time.time())}"
    results = find_embeddings(req_id, embedding)
    nearest = results[0] if results else None
    threshold = 0.5

    temp_path = f"temp_{file.filename}"
    cv2.imwrite(temp_path, img)

    if nearest is None or nearest['distance'] < threshold:
        identity = save_new_face(req_id, embedding, temp_path)
        confidence = 0.0 if nearest is None else nearest['distance']
    else:
        identity = nearest['identity']
        update_face(req_id, identity, temp_path)
        confidence = nearest['distance']

    return JSONResponse({"identity": identity, "confidence": float(confidence)})

@app.get("/identities/")
def get_identities():
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT identity_name FROM identities")
        identities = [row[0] for row in cur.fetchall()]
    conn.close()
    return {"identities": identities}

@app.get("/images/{identity}")
def get_images(identity: str):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT image_path FROM images WHERE identity_id = (SELECT id FROM identities WHERE identity_name = %s)",
            (identity,)
        )
        images = [row[0] for row in cur.fetchall()]
    conn.close()
    return {"identity": identity, "images": images}