import psycopg2
from psycopg2 import OperationalError
import data.env as env
import time
import threading

def create_connection():
    """Create a database connection to the PostgreSQL database."""
    connection = None
    try:
        connection = psycopg2.connect(
            database=env.POSTGRES_DB,
            user=env.POSTGRES_USER,
            password=env.POSTGRES_PASSWORD,
            host=env.POSTGRES_HOST,
            port=env.POSTGRES_PORT,
        )
        print("Postgres DB connected")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def check_connection(connection):
    """Check if the connection is alive, if not, reconnect."""
    try:
        if connection is None or connection.closed != 0:
            print("Postgres DB connection lost. Reconnecting...")
            connection = create_connection()
    except Exception as e:
        print(f"An error occurred while checking the connection: {e}")
    return connection

# Establish initial connection
postgres = create_connection()  # GLOBAL VARIABLE

# Event listener to check connection status and reconnect if necessary
def check_connection_periodically():
    global postgres
    while True:
        postgres = check_connection(postgres)
        time.sleep(60)  # Check every 60 seconds

# Run the connection check in a separate thread
thread = threading.Thread(target=check_connection_periodically, daemon=True)
thread.start()