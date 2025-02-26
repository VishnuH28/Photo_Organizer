import os
import cv2
from .face_embeddings import get_embeddings
from .find_embeddings import find_embeddings
from .new_face import save_new_face
from .update_face import update_face
import time
import gc

def process_images(input_folder, req_id, threshold=0.5):
    """Process images for face recognition (Stage 2 entry point)."""
    start_time = time.time()
    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print("No images found to process")
        return {'faces_recognized': 0, 'unique_people': 0, 'processed': 0, 'errors': 0}

    print(f"Found {len(image_files)} images to process")
    stats = {'faces_recognized': 0, 'unique_people': 0, 'processed': 0, 'errors': 0}

    for image_path in image_files:
        img = cv2.imread(image_path)
        if img is None:
            stats['errors'] += 1
            continue

        embedding = get_embeddings(img)
        if embedding is None:
            stats['errors'] += 1
            continue

        results = find_embeddings(req_id, embedding)
        nearest = results[0] if results else None

        if nearest is None or nearest['distance'] < threshold:
            identity = save_new_face(req_id, embedding, image_path)
            stats['unique_people'] += 1
        else:
            identity = nearest['identity']
            update_face(req_id, identity, image_path)

        stats['faces_recognized'] += 1
        stats['processed'] += 1
        gc.collect()

    end_time = time.time()
    print_summary(start_time, end_time, stats)
    return stats

def print_summary(start_time, end_time, stats):
    """Print summary statistics for face recognition."""
    processing_time = end_time - start_time
    total_images = stats['processed']
    avg_time = processing_time / total_images if total_images > 0 else 0
    print("\nStage 2 Processing Complete!")
    print(f"Total processing time: {processing_time:.2f} seconds")
    print(f"Average time per image: {avg_time:.2f} seconds")
    print(f"Total images processed: {total_images}")
    print(f"Faces recognized: {stats['faces_recognized']}")
    print(f"Unique people identified: {stats['unique_people']}")
    if stats['errors'] > 0:
        print(f"Errors encountered: {stats['errors']}")

if __name__ == "__main__":
    process_images("People_with_faces", "test_req_id")