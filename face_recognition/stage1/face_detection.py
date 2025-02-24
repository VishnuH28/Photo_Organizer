import cv2
import os
from mtcnn.mtcnn import MTCNN
import numpy as np
from roi_analysis import is_face_engaged, draw_roi
from PIL import Image
import time

class FaceDetector:
    def __init__(self, min_face_size=(50, 50), confidence_threshold=0.98, max_size=(800, 800)):
        self.min_face_size = min_face_size
        self.confidence_threshold = confidence_threshold
        self.max_size = max_size
        self.detector = None
        self.stats = {'faces_detected': 0, 'processed': 0, 'errors': 0}
        self.images_with_faces = []

    def initialize_detector(self):
        try:
            print("Initializing MTCNN detector...")
            self.detector = MTCNN()
            print("MTCNN detector initialized successfully!")
            return True
        except Exception as e:
            print(f"Error initializing MTCNN detector: {e}")
            self.detector = None
            return False

    def _open_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img.thumbnail(self.max_size)
                return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            return None

    def detect_faces(self, image_path):
        if self.detector is None:
            print("Detector not initialized!")
            return []

        frame = self._open_image(image_path)
        if frame is None:
            self.stats['errors'] += 1
            return []

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = self.detector.detect_faces(rgb_frame)
            faces = []

            for detection in detections:
                x, y, width, height = detection['box']
                confidence = detection['confidence']
                if (confidence > self.confidence_threshold and 
                    width >= self.min_face_size[0] and 
                    height >= self.min_face_size[1]):
                    bbox = (x, y, width, height)
                    if is_face_engaged(bbox, frame.shape):
                        faces.append((bbox, confidence))
                        self.stats['faces_detected'] += 1

            self.stats['processed'] += 1
            return faces

        except Exception as e:
            print(f"Error detecting faces in {image_path}: {e}")
            self.stats['errors'] += 1
            return []

    def process_images(self, input_folder, output_folder=None):
        if not os.path.exists(input_folder):
            print(f"Error: Input folder '{input_folder}' not found!")
            return []

        if output_folder:
            os.makedirs(output_folder, exist_ok=True)

        image_files = [
            os.path.join(input_folder, f) for f in os.listdir(input_folder)
            if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png'}
        ]

        if not image_files:
            print("No valid images found.")
            return []

        if not self.initialize_detector():
            return []

        print("\nStarting face detection...")
        start_time = time.time()

        for image_path in image_files:
            try:
                faces = self.detect_faces(image_path)
                if faces:
                    self.images_with_faces.append(image_path)
                    print(f"Found {len(faces)} faces in {os.path.basename(image_path)}")

                    if output_folder:
                        frame = self._open_image(image_path)
                        for bbox, _ in faces:
                            frame = draw_roi(frame, bbox)
                        output_path = os.path.join(output_folder, os.path.basename(image_path))
                        cv2.imwrite(output_path, frame)

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                self.stats['errors'] += 1

        self.print_summary(start_time)
        return self.images_with_faces

    def print_summary(self, start_time):
        try:
            elapsed_time = time.time() - start_time
            avg_time_per_image = elapsed_time / self.stats['processed'] if self.stats['processed'] > 0 else 0
            images_per_second = self.stats['processed'] / elapsed_time if elapsed_time > 0 else 0
            percentage_faces = (len(self.images_with_faces) / self.stats['processed'] * 100) if self.stats['processed'] > 0 else 0

            print("\nStage 1 Processing Complete!")
            print(f"Total processing time: {elapsed_time:.2f} seconds")
            print(f"Average time per image: {avg_time_per_image:.2f} seconds")
            print(f"Images per second: {images_per_second:.2f}")
            print(f"Total images processed: {self.stats['processed']}")
            print(f"Total faces detected: {self.stats['faces_detected']}")
            print(f"Images with faces: {len(self.images_with_faces)} ({percentage_faces:.1f}%)")
            
        except Exception as e:
            print(f"Error printing summary: {e}")

    def get_stats(self):
        return self.stats