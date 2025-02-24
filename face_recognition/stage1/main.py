import os
from face_detection import FaceDetector

def process_images(abs_path):
    input_folder = abs_path
    output_folder = os.path.join(os.path.dirname(__file__), "People_with_faces")
    
    detector = FaceDetector()
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        images_with_faces = detector.process_images(input_folder, output_folder)
        
        if images_with_faces:
            print("\nImages with faces detected:")
            for path in images_with_faces:
                print(f"- {path}")
        return images_with_faces
    except Exception as e:
        print(f"Error in process_images: {e}")
        return []

if __name__ == "__main__":
    abs_path = "Photos"
    process_images(abs_path)