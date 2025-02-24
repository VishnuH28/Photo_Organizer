import os
import cv2
from .face_embeddings import get_embeddings
from .find_embeddings import find_embeddings
from .new_face import save_new_face
from .update_face import update_face
import time
import gc

class FaceRecognizerStage2:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.stats = {
            'faces_recognized': 0,
            'unique_people': 0,
            'processed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    def process_images(self, input_folder, req_id):
        self.stats['start_time'] = time.time()
        image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not image_files:
            print("No images found to process")
            return

        print(f"Found {len(image_files)} images to process")
        
        for image_path in image_files:
            img = cv2.imread(image_path)
            if img is None:
                self.stats['errors'] += 1
                continue

            embedding = get_embeddings(img)
            if embedding is None:
                self.stats['errors'] += 1
                continue

            results = find_embeddings(req_id, embedding)
            nearest = results[0] if results else None

            if nearest is None or nearest['distance'] < self.threshold:
                identity = save_new_face(req_id, embedding, image_path)
                self.stats['unique_people'] += 1
            else:
                identity = nearest['identity']
                update_face(req_id, identity, image_path)

            self.stats['faces_recognized'] += 1
            self.stats['processed'] += 1
            gc.collect()

        self.stats['end_time'] = time.time()
        self.print_summary()

    def print_summary(self):
        processing_time = self.stats['end_time'] - self.stats['start_time']
        total_images = self.stats['processed']
        avg_time = processing_time / total_images if total_images > 0 else 0
        print("\nStage 2 Processing Complete!")
        print(f"Total processing time: {processing_time:.2f} seconds")
        print(f"Average time per image: {avg_time:.2f} seconds")
        print(f"Total images processed: {total_images}")
        print(f"Faces recognized: {self.stats['faces_recognized']}")
        print(f"Unique people identified: {self.stats['unique_people']}")
        if self.stats['errors'] > 0:
            print(f"Errors encountered: {self.stats['errors']}")