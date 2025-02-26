import os
from .face_detection import process_images as detect_faces_in_folder

def process_images(abs_path):
    """Process images in a folder for face detection (Stage 1 entry point)."""
    input_folder = abs_path
    output_folder = os.path.join(os.path.dirname(__file__), "People_with_faces")
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        images_with_faces, _ = detect_faces_in_folder(input_folder, output_folder)
        
        if images_with_faces:
            print("\nImages with faces detected:")
            for path in images_with_faces:
                print(f"- {path}")
        return images_with_faces
    except Exception as e:
        print(f"Error in process_images: {e}")
        return []

if __name__ == "__main__":
    process_images("Photos")