import os
import shutil
import time
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from tqdm import tqdm

class FoodDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")  # Load YOLOv8n model
        self.food_categories = {
            'apple', 'banana', 'orange', 'pizza', 'donut', 'cake', 'sandwich', 
            'hot dog', 'carrot', 'broccoli', 'bowl', 'bottle', 'wine glass', 'cup', 
            'fork', 'knife', 'spoon', 'dining table'
        }

    def detect_food(self, image_path):
        """Run food detection on a single image."""
        results = self.model(image_path)
        detected_items = {self.model.names[int(box.cls)] for box in results[0].boxes}
        return any(item in self.food_categories for item in detected_items)

    def process_images(self, input_folder="Photos", output_folder="Photos_with_Food"):
        """Process images and move food-related ones to output folder."""
        os.makedirs(output_folder, exist_ok=True)
        images = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not images:
            print("No images found in input folder.")
            return
        
        print(f"Processing {len(images)} images...")
        start_time = time.time()

        for img in tqdm(images, desc="Detecting food"):
            img_path = os.path.join(input_folder, img)
            if self.detect_food(img_path):
                shutil.copy2(img_path, os.path.join(output_folder, img))

        print(f"Processing complete in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    detector = FoodDetector()
    detector.process_images()
