from flask import Flask
from routes.api_routes import apiRoutes
from data.env import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
import database.postgres
from init.initialize import initialize
import sys
import os

# Add face_recognition/stage1 to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'face_recognition', 'stage1'))

app = Flask(__name__)
app.register_blueprint(apiRoutes, url_prefix="/api/v1")

@app.route('/')
def home():
    return "Server is running!"

initialize()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

    # Optional: Test the pipeline directly (uncomment to use)
    """
    import os
    import asyncio
    from start_face_recognition import start_face_recognition

    test_r_id = "test_r_id"
    test_abs_path = "Photos"
    
    if not os.path.exists(test_abs_path):
        os.makedirs(test_abs_path, exist_ok=True)
        print(f"Created test input folder: {test_abs_path}")

    print("Starting test run...")
    result = asyncio.run(start_face_recognition(test_r_id, test_abs_path))
    print(result)
    """