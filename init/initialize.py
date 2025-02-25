from database.postgres import postgres, check_connection
from data.table_names import TableNames

def create_tables():
    """Creates necessary database tables if they do not exist."""
    queries = {
        "identities": """
        CREATE TABLE IF NOT EXISTS identities (
            id SERIAL PRIMARY KEY,
            identity_name VARCHAR(50) UNIQUE,
            reference_embedding BYTEA
        );
        """,
        "images": """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            identity_id INTEGER REFERENCES identities(id),
            image_path TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        TableNames.FACE_RECOGNITION_REQUEST.value: """
        CREATE TABLE IF NOT EXISTS face_recognition_request (
            req_id VARCHAR(50) PRIMARY KEY,
            r_id VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    """Runs all initialization functions."""
    print("Initializing database and system setup...")
    create_tables()
    print("Initialization complete.")

if __name__ == "__main__":
    initialize()