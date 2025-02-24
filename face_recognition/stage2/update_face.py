from database.postgres import postgres, check_connection

def update_face(req_id, identity, image_path):
    global postgres
    postgres = check_connection(postgres)
    try:
        with postgres.cursor() as cur:
            cur.execute(
                "INSERT INTO images (identity_id, image_path) VALUES ((SELECT id FROM identities WHERE identity_name = %s), %s)",
                (identity, image_path)
            )
            postgres.commit()
    except Exception as e:
        print(f"Error updating face: {e}")