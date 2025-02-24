import os
import uuid
import asyncio
from stage1.main import process_images  
from stage2.face_recognizer import FaceRecognizerStage2

async def start_face_recognition(r_id, abs_path):
    success = False
    msg = ""
    req_id = "rqid-" + str(uuid.uuid4())

    try:
        if not os.path.exists(abs_path):
            msg = f"The file {abs_path} does not exist."
            raise FileNotFoundError(msg)

        # Run Stage 1 asynchronously (assumes it outputs to stage1/People_with_faces)
        await asyncio.to_thread(stage1_process, abs_path)  # Runs in thread since Stage 1 might not be async

        # Run Stage 2
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
        msg = msg or "An error occurred during processing"
    finally:
        return {
            "success": success,
            "msg": msg,
            "req_id": req_id
        }

if __name__ == "__main__":
    r_id = "test_r_id"
    abs_path = "path/to/your/input/file"  # Replace with actual path
    result = asyncio.run(start_face_recognition(r_id, abs_path))
    print(result)