import os
import uuid
import asyncio
from face_recognition.stage1.main import process_images as stage1_process
from face_recognition.stage2.face_recognizer import FaceRecognizerStage2
from data.err_msgs import ErrorMessages
from database.postgres import postgres, check_connection
from data.table_names import TableNames

async def start_face_recognition(r_id, abs_path):
    success = False
    msg = ""
    req_id = "rqid-" + str(uuid.uuid4())

    # Save request to database
    global postgres
    postgres = check_connection(postgres)
    try:
        with postgres.cursor() as cur:
            cur.execute(
                f"INSERT INTO {TableNames.FACE_RECOGNITION_REQUEST.value} (req_id, r_id, status) VALUES (%s, %s, %s)",
                (req_id, r_id, 'processing')
            )
            postgres.commit()
    except Exception as e:
        print(f"Failed to start process in DB: {e}")
        msg = "Failed to initiate process"
        return {"success": False, "msg": msg, "req_id": req_id}

    try:
        if not os.path.exists(abs_path):
            msg = f"The file {abs_path} does not exist."
            raise FileNotFoundError(msg)

        await asyncio.to_thread(stage1_process, abs_path)

        input_folder = os.path.join(os.path.dirname(__file__), "stage1", "People_with_faces")
        if not os.path.exists(input_folder):
            msg = "Stage 1 output folder not found."
            raise FileNotFoundError(msg)

        recognizer = FaceRecognizerStage2(threshold=0.5)
        recognizer.process_images(input_folder, req_id)
        success = True
        msg = "Face recognition process completed successfully"

        # Update status to completed
        with postgres.cursor() as cur:
            cur.execute(
                f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'completed' WHERE req_id = %s",
                (req_id,)
            )
            postgres.commit()
    except Exception as e:
        print(f"start_face_recognition(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
        with postgres.cursor() as cur:
            cur.execute(
                f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'stuck' WHERE req_id = %s",
                (req_id,)
            )
            postgres.commit()
    finally:
        return {
            "success": success,
            "msg": msg,
            "req_id": req_id
        }

if __name__ == "__main__":
    r_id = "test_r_id"
    abs_path = "path/to/your/input/folder"
    result = asyncio.run(start_face_recognition(r_id, abs_path))
    print(result)