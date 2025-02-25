import time
from database.postgres import postgres, check_connection

def save_new_face(req_id, embedding, image_path):
    global postgres
    postgres = check_connection(postgres)
    identity = f"Person_{req_id}_{int(time.time())}"
    try:
        with postgres.cursor() as cur:
            cur.execute(
                "INSERT INTO identities (identity_name, reference_embedding) VALUES (%s, %s) RETURNING id",
                (identity, embedding.tobytes())
            )
            identity_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO images (identity_id, image_path) VALUES (%s, %s)",
                (identity_id, image_path)
            )
            postgres.commit()
    except Exception as e:
        print(f"Error saving new face: {e}")
    return identity