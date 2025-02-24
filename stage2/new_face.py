import psycopg2
import time

def connect_db():
    return psycopg2.connect(
        host="194.195.112.175",
        database="face_rec_2",
        user="vishnu",
        password=os.getenv("DB_PASSWORD")
    )

def save_new_face(req_id, embedding, image_path):
    conn = connect_db()
    identity = f"Person_{req_id}_{int(time.time())}"
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO identities (identity_name, reference_embedding) VALUES (%s, %s) RETURNING id",
                (identity, embedding.tobytes())
            )
            identity_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO images (identity_id, image_path) VALUES (%s, %s)",
                (identity_id, image_path)
            )
            conn.commit()
    except Exception as e:
        print(f"Error saving new face: {e}")
    finally:
        conn.close()
    return identity