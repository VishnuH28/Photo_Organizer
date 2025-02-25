from flask import Blueprint, request, jsonify
import asyncio
from threading import Thread
from data.err_msgs import ErrorMessages
from face_recognition.start_face_recognition import start_face_recognition
from database.postgres import postgres, check_connection
from data.table_names import TableNames

apiRoutes = Blueprint('apiRoutes', __name__)

@apiRoutes.route('/process/start', methods=['POST'])
def start_process_route():
    success = False
    msg = ""
    req_id = None

    try:
        data = request.get_json()
        r_id = data.get('r_id')
        abs_path = data.get('abs_path')

        if not r_id or not abs_path:
            msg = "r_id and abs_path are required"
            raise ValueError(msg)
        
        if not isinstance(r_id, str) or not isinstance(abs_path, str):
            msg = "r_id and abs_path must be strings"
            raise ValueError(msg)

        # Start process in background
        process_result = start_face_recognition(r_id, abs_path)
        req_id = process_result['req_id']
        thread = Thread(target=lambda: asyncio.run(start_face_recognition(r_id, abs_path)))
        thread.start()

        success = True
        msg = "Process started"
    except Exception as e:
        print(f"start_process_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        return jsonify({"success": success, "msg": msg, "req_id": req_id}), 400
    return jsonify({"success": success, "msg": msg, "req_id": req_id}), 200

@apiRoutes.route('/process/stop', methods=['POST'])
def stop_process_route():
    success = False
    msg = ""

    try:
        data = request.get_json()
        req_id = data.get('req_id')

        if not req_id or not isinstance(req_id, str):
            msg = "req_id is required and must be a string"
            raise ValueError(msg)

        global postgres
        postgres = check_connection(postgres)
        with postgres.cursor() as cur:
            cur.execute(
                f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'stopped' WHERE req_id = %s AND status = 'processing'",
                (req_id,)
            )
            if cur.rowcount > 0:
                success = True
                msg = f"Process {req_id} stopped"
            else:
                msg = f"Process {req_id} not found or not processing"
            postgres.commit()
    except Exception as e:
        print(f"stop_process_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        return jsonify({"success": success, "msg": msg}), 400
    return jsonify({"success": success, "msg": msg}), 200

@apiRoutes.route('/process/stop-all', methods=['POST'])
def stop_all_processes_route():
    success = False
    msg = ""

    try:
        data = request.get_json()
        r_id = data.get('r_id')

        if not r_id or not isinstance(r_id, str):
            msg = "r_id is required and must be a string"
            raise ValueError(msg)

        global postgres
        postgres = check_connection(postgres)
        with postgres.cursor() as cur:
            cur.execute(
                f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'stopped' WHERE r_id = %s AND status = 'processing'",
                (r_id,)
            )
            stopped_count = cur.rowcount
            postgres.commit()
        
        success = True
        msg = f"Stopped {stopped_count} processes for r_id {r_id}" if stopped_count > 0 else f"No processes found for r_id {r_id}"
    except Exception as e:
        print(f"stop_all_processes_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        return jsonify({"success": success, "msg": msg}), 400
    return jsonify({"success": success, "msg": msg}), 200

@apiRoutes.route('/process/status', methods=['POST'])
def status_process_route():
    success = False
    msg = ""
    status = "not found"

    try:
        data = request.get_json()
        req_id = data.get('req_id')

        if not req_id or not isinstance(req_id, str):
            msg = "req_id is required and must be a string"
            raise ValueError(msg)

        global postgres
        postgres = check_connection(postgres)
        with postgres.cursor() as cur:
            cur.execute(
                f"SELECT status FROM {TableNames.FACE_RECOGNITION_REQUEST.value} WHERE req_id = %s",
                (req_id,)
            )
            result = cur.fetchone()
            if result:
                status = result[0]
                success = True
                msg = f"Status for {req_id} retrieved"
            else:
                msg = f"Process {req_id} not found"
    except Exception as e:
        print(f"status_process_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        return jsonify({"success": success, "msg": msg, "status": status}), 400
    return jsonify({"success": success, "msg": msg, "status": status}), 200

@apiRoutes.route('/process/list', methods=['POST'])
def list_processes_route():
    success = False
    msg = ""
    process_list = []

    try:
        data = request.get_json()
        req_id = data.get('req_id')
        all_processes = data.get('all', False)
        limit = data.get('limit')

        if req_id and not isinstance(req_id, str):
            msg = "req_id must be a string"
            raise ValueError(msg)
        if limit is not None and not isinstance(limit, int):
            msg = "limit must be a number"
            raise ValueError(msg)

        global postgres
        postgres = check_connection(postgres)
        with postgres.cursor() as cur:
            if req_id:
                cur.execute(
                    f"SELECT req_id, r_id, status FROM {TableNames.FACE_RECOGNITION_REQUEST.value} WHERE req_id = %s",
                    (req_id,)
                )
                result = cur.fetchone()
                if result:
                    process_list = [{"req_id": result[0], "r_id": result[1], "status": result[2]}]
                else:
                    msg = f"Process {req_id} not found"
                    success = False
                    return jsonify({"success": success, "msg": msg, "list": process_list}), 400
            else:
                query = f"SELECT req_id, r_id, status FROM {TableNames.FACE_RECOGNITION_REQUEST.value}"
                if not all_processes:
                    query += " WHERE status IN ('processing', 'stuck')"
                if limit is not None:
                    query += f" LIMIT {limit}"
                cur.execute(query)
                process_list = [{"req_id": row[0], "r_id": row[1], "status": row[2]} for row in cur.fetchall()]

        success = True
        msg = f"Retrieved {len(process_list)} processes"
    except Exception as e:
        print(f"list_processes_route(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        return jsonify({"success": success, "msg": msg, "list": process_list}), 400
    return jsonify({"success": success, "msg": msg, "list": process_list}), 200