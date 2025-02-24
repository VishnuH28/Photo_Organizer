import psycopg2

def connect_db():
    return psycopg2.connect(
        host="194.195.112.175",
        database="face_rec_2",
        user="vishnu",
        password=os.getenv("DB_PASSWORD")
    )

def update_face(req_id, identity, image_path):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO images (identity_id, image_path) VALUES ((SELECT id FROM identities WHERE identity_name = %s), %s)",
                (identity, image_path)
            )
            conn.commit()
    except Exception as e:
        print(f"Error updating face: {e}")
    finally:
        conn.close()