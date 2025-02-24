from flask import Blueprint, request, jsonify
apiRoutes = Blueprint('apiRoutes', __name__)

from data.err_msgs import ErrorMessages
from start_face_recognition import start_face_recognition  # Adjusted import path

# Route to start a new process
@apiRoutes.route('/process/start', methods=['POST'])
def start_process_route():
    success = False
    msg = ""
    req_id = None

    try:
        data = request.get_json()
        r_id = data.get('r_id')  # Get the r_id from the request
        abs_path = data.get('abs_path')  # Get the abs_path from the request

        if not r_id or not abs_path:
            msg = "r_id and abs_path are required"
            raise ValueError(msg)
        
        if not isinstance(r_id, str) or not isinstance(abs_path, str):
            msg = "r_id and abs_path must be strings"
            raise ValueError(msg)

        # Start the process (synchronous call; async handled internally)
        process_result = start_face_recognition(r_id, abs_path)

        success = process_result.get('success')
        msg = process_result.get('msg')
        req_id = process_result.get('req_id')
    except Exception as e:
        print(f"start_process_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
    finally:
        return jsonify({"success": success, "msg": msg, "req_id": req_id}), 200