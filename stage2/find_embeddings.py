import psycopg2
import numpy as np

def connect_db():
    return psycopg2.connect(
        host="194.195.112.175",
        database="face_rec_2",
        user="vishnu",
        password=os.getenv("DB_PASSWORD")
    )

def find_embeddings(req_id, embedding):
    conn = connect_db()
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT identity_name, reference_embedding <-> %s AS distance
                FROM identities
                ORDER BY distance
                LIMIT 1
                """,
                (embedding.tobytes(),)
            )
            row = cur.fetchone()
            if row:
                identity, distance = row
                results.append({"identity": identity, "distance": float(distance)})
    except Exception as e:
        print(f"Error in find_embeddings: {e}")
    finally:
        conn.close()
    return results