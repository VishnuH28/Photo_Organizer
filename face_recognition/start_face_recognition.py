import os
import uuid
import asyncio
from face_recognition.stage1.stage1_process import process_images as stage1_process
from face_recognition.stage2.face_recognizer import process_images as stage2_process
from data.err_msgs import ErrorMessages
from database.postgres import postgres, check_connection
from data.table_names import TableNames

async def start_face_recognition(r_id, abs_path, stop_flag=None):
    """Main entry point to start face recognition process."""
    success = False
    msg = ""
    req_id = "rqid-" + str(uuid.uuid4())

    if stop_flag and stop_flag.value:
        return {"success": False, "msg": "Process stopped before starting", "req_id": req_id}

    global postgres
    postgres = check_connection(postgres)

    try:
        # Insert initial request into database
        with postgres.cursor() as cur:
            cur.execute(
                f"INSERT INTO {TableNames.FACE_RECOGNITION_REQUEST.value} (req_id, r_id, status) VALUES (%s, %s, %s)",
                (req_id, r_id, 'processing')
            )
            postgres.commit()

        # Check input path
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"The file {abs_path} does not exist.")

        if stop_flag and stop_flag.value:
            raise Exception("Process stopped")

        # Stage 1: Face detection
        await asyncio.to_thread(stage1_process, abs_path)

        if stop_flag and stop_flag.value:
            raise Exception("Process stopped")

        # Stage 2: Face recognition
        input_folder = os.path.join(os.path.dirname(__file__), "stage1", "People_with_faces")
        if not os.path.exists(input_folder):
            raise FileNotFoundError("Stage 1 output folder not found.")

        stage2_process(input_folder, req_id)

        # Update status to completed
        with postgres.cursor() as cur:
            cur.execute(
                f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'completed' WHERE req_id = %s",
                (req_id,)
            )
            postgres.commit()

        success = True
        msg = "Face recognition process completed successfully"
    except Exception as e:
        print(f"start_face_recognition(): {e}")
        msg = str(e) or ErrorMessages.GENERIC_ERROR.value
        # Update status to stuck if processing started
        try:
            with postgres.cursor() as cur:
                cur.execute(
                    f"UPDATE {TableNames.FACE_RECOGNITION_REQUEST.value} SET status = 'stuck' WHERE req_id = %s",
                    (req_id,)
                )
                postgres.commit()
        except Exception as db_e:
            print(f"Failed to update status to stuck: {db_e}")
    finally:
        return {"success": success, "msg": msg, "req_id": req_id}

if __name__ == "__main__":
    result = asyncio.run(start_face_recognition("test_r_id", "Photos"))
    print(result)