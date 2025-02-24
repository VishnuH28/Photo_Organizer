from database.postgres import postgres, check_connection
from data.table_names import TableNames

def create_tables():
    queries = {
        TableNames.KNOWN_FACE_EMBEDDINGS.value: """
        CREATE TABLE IF NOT EXISTS known_face_embeddings (
            f_id VARCHAR(50) PRIMARY KEY,
            embeddings BYTEA
        );
        """,
        TableNames.FACES_IN_ASSETS.value: """
        CREATE TABLE IF NOT EXISTS faces_in_assets (
            f_id VARCHAR(50) REFERENCES known_face_embeddings(f_id),
            v_id VARCHAR(50),
            PRIMARY KEY (f_id, v_id)
        );
        """,
        TableNames.TEMP_FACE_EMBEDDINGS.value: """
        CREATE TABLE IF NOT EXISTS temp_face_embeddings (
            req_id VARCHAR(50),
            f_id VARCHAR(50),
            embeddings BYTEA,
            screen_time_ms INTEGER,
            found_count INTEGER,
            PRIMARY KEY (req_id, f_id)
        );
        """,
        TableNames.FACE_RECOGNITION_REQUEST.value: """
        CREATE TABLE IF NOT EXISTS face_recognition_request (
            req_id VARCHAR(50) PRIMARY KEY,
            v_id VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pending'
        );
        """
    }

    global postgres
    postgres = check_connection(postgres)
    try:
        with postgres.cursor() as cur:
            for table, query in queries.items():
                print(f"Creating table {table}...")
                cur.execute(query)
            postgres.commit()
        print("All tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

def initialize():
    print("Initializing database and system setup...")
    create_tables()
    print("Initialization complete.")

if __name__ == "__main__":
    initialize()