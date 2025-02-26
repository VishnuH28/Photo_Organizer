import numpy as np
from database.postgres import postgres, check_connection

def find_embeddings(req_id, embedding):
    global postgres
    postgres = check_connection(postgres)  
    results = []
    try:
        with postgres.cursor() as cur:
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
        # Connection might be closed; let the thread reconnect
    return results