import os
import uuid
import asyncio
from stage1.main import process_images as stage1_process
from stage2.face_recognizer import FaceRecognizerStage2
from data.err_msgs import ErrorMessages

async def start_face_recognition(r_id, abs_path):
    success = False
    msg = ""
    req_id = "rqid-" + str(uuid.uuid4())

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
    except Exception as e:
        print(f"start_face_recognition(): {e}")
        msg = msg or ErrorMessages.GENERIC_ERROR.value
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