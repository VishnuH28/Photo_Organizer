import cv2

def is_face_engaged(bbox, frame_shape):
    try:
        x, y, w, h = bbox
        height, width = frame_shape[:2]
        
        engaged = (0 <= x <= width - w) and (0 <= y <= height - h) and (w > 0) and (h > 0)
        
        if not engaged:
            print(f"Face bbox {bbox} is outside frame dimensions {frame_shape}")
        return engaged
    
    except Exception as e:
        print(f"Error in is_face_engaged: {e}")
        return False

def draw_roi(frame, bbox, color=(255, 0, 0), thickness=2):
    try:
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame
    
    except Exception as e:
        print(f"Error drawing ROI: {e}")
        return frame