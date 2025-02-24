from enum import Enum

class TableNames(Enum):
    KNOWN_FACES = "known_faces"
    KNOWN_FACE_EMBEDDINGS = "known_face_embeddings"
    FACES_IN_ASSETS = "faces_in_assets"
    TEMP_FACE_EMBEDDINGS = "temp_face_embeddings"
    FACE_RECOGNITION_REQUEST = "face_recognition_request"