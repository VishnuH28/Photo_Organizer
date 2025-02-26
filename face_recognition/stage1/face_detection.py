import cv2
import os
from mtcnn.mtcnn import MTCNN
import numpy as np
from .roi_analysis import is_face_engaged, draw_roi
from PIL import Image
import time

def initialize_detector():
    """Initialize the MTCNN detector."""
    try:
        print("Initializing MTCNN detector...")
        detector = MTCNN()
        print("MTCNN detector initialized successfully!")
        return detector
    except Exception as e:
        print(f"Error initializing MTCNN detector: {e}")
        return None

def open_image(image_path, max_size=(800, 800)):
    """Open and resize an image."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail(max_size)
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return None

def detect_faces(detector, image_path, min_face_size=(50, 50), confidence_threshold=0.98):
    """Detect faces in an image."""
    if detector is None:
        print("Detector not initialized!")
        return []

    frame = open_image(image_path)
    if frame is None:
        return []

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = detector.detect_faces(rgb_frame)
        faces = []

        for detection in detections:
            x, y, width, height = detection['box']
            confidence = detection['confidence']
            if (confidence > confidence_threshold and 
                width >= min_face_size[0] and 
                height >= min_face_size[1]):
                bbox = (x, y, width, height)
                if is_face_engaged(bbox, frame.shape):
                    faces.append((bbox, confidence))
        return faces
    except Exception as e:
        print(f"Error detecting faces in {image_path}: {e}")
        return []

def process_images(input_folder, output_folder=None, min_face_size=(50, 50), confidence_threshold=0.98):
    """Process images in a folder for face detection."""
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found!")
        return [], {'faces_detected': 0, 'processed': 0, 'errors': 0}

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    image_files = [
        os.path.join(input_folder, f) for f in os.listdir(input_folder)
        if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png'}
    ]

    if not image_files:
        print("No valid images found.")
        return [], {'faces_detected': 0, 'processed': 0, 'errors': 0}

    detector = initialize_detector()
    if not detector:
        return [], {'faces_detected': 0, 'processed': 0, 'errors': 0}

    print("\nStarting face detection...")
    start_time = time.time()
    stats = {'faces_detected': 0, 'processed': 0, 'errors': 0}
    images_with_faces = []

    for image_path in image_files:
        try:
            faces = detect_faces(detector, image_path, min_face_size, confidence_threshold)
            stats['processed'] += 1
            if faces:
                images_with_faces.append(image_path)
                stats['faces_detected'] += len(faces)
                print(f"Found {len(faces)} faces in {os.path.basename(image_path)}")

                if output_folder:
                    frame = open_image(image_path)
                    for bbox, _ in faces:
                        frame = draw_roi(frame, bbox)
                    output_path = os.path.join(output_folder, os.path.basename(image_path))
                    cv2.imwrite(output_path, frame)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            stats['errors'] += 1

    print_summary(start_time, stats, images_with_faces)
    return images_with_faces, stats

def print_summary(start_time, stats, images_with_faces):
    """Print summary statistics for face detection."""
    try:
        elapsed_time = time.time() - start_time
        avg_time_per_image = elapsed_time / stats['processed'] if stats['processed'] > 0 else 0
        images_per_second = stats['processed'] / elapsed_time if elapsed_time > 0 else 0
        percentage_faces = (len(images_with_faces) / stats['processed'] * 100) if stats['processed'] > 0 else 0

        print("\nStage 1 Processing Complete!")
        print(f"Total processing time: {elapsed_time:.2f} seconds")
        print(f"Average time per image: {avg_time_per_image:.2f} seconds")
        print(f"Images per second: {images_per_second:.2f}")
        print(f"Total images processed: {stats['processed']}")
        print(f"Total faces detected: {stats['faces_detected']}")
        print(f"Images with faces: {len(images_with_faces)} ({percentage_faces:.1f}%)")
    except Exception as e:
        print(f"Error printing summary: {e}")

if __name__ == "__main__":
    images, stats = process_images("Photos", "People_with_faces")