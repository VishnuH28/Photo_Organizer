import torch
import cv2
import time
import os
import gc
import shutil
from ultralytics import YOLO

# Load YOLOv8 model (choose a better accuracy model like YOLOv8m)
model_path = "yolov8s.pt"  # Change to 'yolov8s.pt' if you need faster speed
model = YOLO(model_path)

# Input and output directories
input_folder = "Photos"
output_folder = "Animals"
os.makedirs(output_folder, exist_ok=True)

# Get all image files
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

total_images = len(image_files)
print(f"Found {total_images} images to process")

# Start processing
start_time = time.time()

def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error reading {image_path}")
        return None
    
    # Resize image for efficiency
    image = cv2.resize(image, (640, 640))
    
    # Run YOLOv8 inference
    results = model(image)
    
    # Check if an animal is detected
    detected = False
    for result in results:
        for box in result.boxes:
            cls = int(box.cls.item())
            label = model.names[cls]
            if label in ["dog", "cat", "bird", "horse", "cow", "elephant", "zebra", "giraffe"]:  # Add more if needed
                detected = True
                break
        if detected:
            break
    
    return detected

processed_images = 0

time_per_image = []
for image_file in image_files:
    image_path = os.path.join(input_folder, image_file)
    output_path = os.path.join(output_folder, image_file)
    
    image_start_time = time.time()
    if process_image(image_path):
        shutil.copy(image_path, output_path)  # Copy instead of move
    image_end_time = time.time()
    
    time_taken = image_end_time - image_start_time
    time_per_image.append(time_taken)
    processed_images += 1
    print(f"Processed {processed_images}/{total_images} - Time taken: {time_taken:.2f}s")
    
    # Cleanup memory
    torch.cuda.empty_cache()
    gc.collect()

# Summary
end_time = time.time()
total_time = end_time - start_time
average_time = sum(time_per_image) / len(time_per_image) if time_per_image else 0

print("\nProcessing Summary:")
print(f"Total processing time: {total_time:.2f}s")
print(f"Average time per image: {average_time:.2f}s")
