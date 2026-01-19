
import cv2
import numpy as np
from ultralytics import YOLO
import os
import torch

# Global variable to cache the model
_yolo_model = None


def get_yolo_model():
    """
    Load or return cached license plate YOLO model.
    
    Returns:
        YOLO: YOLOv8 model instance for license plate detection
    """
    global _yolo_model
    
    if _yolo_model is not None:
        return _yolo_model
    
    try:
        # Use license plate-specific YOLOv8 model
        # Located in models/ directory at project root
        import os
        
        # Determine the path to the license plate model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        model_path = os.path.join(project_root, "models", "license_plate_detector.pt")
        
        # Fallback to relative path if absolute path doesn't work
        if not os.path.exists(model_path):
            model_path = "models/license_plate_detector.pt"
        
        # If still not found, check for yolov8n.pt in models directory
        if not os.path.exists(model_path):
            alt_path = os.path.join(project_root, "models", "yolov8n.pt")
            if os.path.exists(alt_path):
                model_path = alt_path
                print("License plate model not found, using YOLOv8n as fallback")
        
        print(f"Loading license plate detector model: {model_path}")
        _yolo_model = YOLO(model_path)
        
        # Set to evaluation mode
        _yolo_model.eval()
        
        print("License plate detector model loaded successfully")
        return _yolo_model
    
    except Exception as e:
        print(f"Error loading license plate model: {str(e)}")
        raise


def detect_plate_region(image):
    """
    Detect license plate region using YOLOv8.
    
    Args:
        image: Input image (BGR format from OpenCV)
    
    Returns:
        tuple: (plate_region, bounding_box) where:
            - plate_region: cropped image containing the plate
            - bounding_box: (x, y, w, h) coordinates
            Returns (None, None) if no plate detected
    """
    try:
        model = get_yolo_model()
        
        # Run inference with confidence threshold
        results = model(image, conf=0.3, verbose=False)
        
        if not results or len(results) == 0:
            return None, None
        
        detections = results[0]
        
        # Find the largest detection (most likely to be a license plate)
        if detections.boxes is None or len(detections.boxes) == 0:
            return None, None
        
        # Get bounding boxes
        boxes = detections.boxes.xyxy.cpu().numpy()
        confidences = detections.boxes.conf.cpu().numpy()
        
        if len(boxes) == 0:
            return None, None
        
        # Filter by confidence and take the detection with highest confidence
        best_detection = None
        best_score = 0
        
        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            
            # Basic plate-like shape filtering
            aspect_ratio = w / h if h > 0 else 0
            
            # License plates are typically between 1.5-8 times wider than tall
            if 1.5 < aspect_ratio < 8.0:
                score = conf * (1 + abs(aspect_ratio - 3.5) / 10)
                if score > best_score:
                    best_score = score
                    best_detection = (x1, y1, x2, y2)
        
        # If no detection with good aspect ratio, just take the highest confidence one
        if best_detection is None:
            x1, y1, x2, y2 = boxes[0]
            best_detection = (x1, y1, x2, y2)
        
        x1, y1, x2, y2 = best_detection
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Ensure coordinates are within bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.shape[1], x2)
        y2 = min(image.shape[0], y2)
        
        w = x2 - x1
        h = y2 - y1
        
        # Add small padding
        padding = 5
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(image.shape[1], x2 + padding)
        y2 = min(image.shape[0], y2 + padding)
        
        # Extract plate region
        plate_region = image[y1:y2, x1:x2]
        
        # Return region and bounding box in (x, y, w, h) format
        return plate_region, (x1, y1, x2 - x1, y2 - y1)
    
    except Exception as e:
        print(f"Error in YOLO detection: {str(e)}")
        return None, None


def detect_plate_region_with_debug(image, debug=True):
    """
    Detect license plate region using YOLOv8 with debug visualization.
    
    Args:
        image: Input image (BGR format from OpenCV)
        debug: If True, print debug information and draw all detections
    
    Returns:
        tuple: (plate_region, bounding_box, debug_image) where:
            - plate_region: cropped image containing the plate
            - bounding_box: (x, y, w, h) coordinates
            - debug_image: image with all detections drawn
            Returns (None, None, None) if no plate detected
    """
    try:
        model = get_yolo_model()
        
        # Run inference with confidence threshold
        results = model(image, conf=0.3, verbose=False)
        
        debug_image = image.copy()
        
        if not results or len(results) == 0:
            if debug:
                print("[DEBUG] No detections found")
            return None, None, debug_image
        
        detections = results[0]
        
        # Find all detections
        if detections.boxes is None or len(detections.boxes) == 0:
            if debug:
                print("[DEBUG] No boxes detected")
            return None, None, debug_image
        
        # Get bounding boxes
        boxes = detections.boxes.xyxy.cpu().numpy()
        confidences = detections.boxes.conf.cpu().numpy()
        class_ids = detections.boxes.cls.cpu().numpy() if detections.boxes.cls is not None else [0] * len(boxes)
        
        if debug:
            print(f"[DEBUG] Total detections: {len(boxes)}")
            print(f"[DEBUG] Class IDs: {class_ids}")
            print(f"[DEBUG] Confidences: {confidences}")
        
        if len(boxes) == 0:
            return None, None, debug_image
        
        # Draw all detections on debug image
        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Draw bounding box
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
            
            # Draw confidence and class
            label = f"Class {int(class_id)}: {conf:.2f}"
            cv2.putText(debug_image, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            if debug:
                print(f"  Detection {i+1}: Class={int(class_id)}, Conf={conf:.3f}, "
                      f"Box=[{x1},{y1},{x2},{y2}]")
        
        # Filter by confidence and take the detection with highest confidence
        best_detection = None
        best_score = 0
        
        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            
            # Basic plate-like shape filtering
            aspect_ratio = w / h if h > 0 else 0
            
            # License plates are typically between 1.5-8 times wider than tall
            if 1.5 < aspect_ratio < 8.0:
                score = conf * (1 + abs(aspect_ratio - 3.5) / 10)
                if score > best_score:
                    best_score = score
                    best_detection = (x1, y1, x2, y2)
        
        # If no detection with good aspect ratio, just take the highest confidence one
        if best_detection is None:
            x1, y1, x2, y2 = boxes[0]
            best_detection = (x1, y1, x2, y2)
        
        if debug:
            print(f"[DEBUG] Selected detection with score: {best_score:.3f}")
        
        x1, y1, x2, y2 = best_detection
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Ensure coordinates are within bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image.shape[1], x2)
        y2 = min(image.shape[0], y2)
        
        w = x2 - x1
        h = y2 - y1
        
        # Add small padding
        padding = 5
        x1_padded = max(0, x1 - padding)
        y1_padded = max(0, y1 - padding)
        x2_padded = min(image.shape[1], x2 + padding)
        y2_padded = min(image.shape[0], y2 + padding)
        
        # Extract plate region
        plate_region = image[y1_padded:y2_padded, x1_padded:x2_padded]
        
        # Draw selected detection in green
        cv2.rectangle(debug_image, (x1_padded, y1_padded), (x2_padded, y2_padded), (0, 255, 0), 3)
        cv2.putText(debug_image, "SELECTED", (x1_padded, y1_padded - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Return region, bounding box in (x, y, w, h) format, and debug image
        return plate_region, (x1_padded, y1_padded, x2_padded - x1_padded, y2_padded - y1_padded), debug_image
    
    except Exception as e:
        print(f"Error in YOLO detection: {str(e)}")
        return None, None, image.copy()


def draw_bounding_box(image, bounding_box, color=(0, 255, 0), thickness=2):
    """
    Draw bounding box on an image.
    
    Args:
        image: Input image
        bounding_box: (x, y, w, h) coordinates
        color: BGR color tuple
        thickness: Line thickness
    
    Returns:
        Image with drawn bounding box
    """
    if bounding_box is None:
        return image
    
    image_copy = image.copy()
    x, y, w, h = bounding_box
    
    # Draw rectangle
    cv2.rectangle(image_copy, (x, y), (x + w, y + h), color, thickness)
    
    return image_copy


def get_all_plate_regions(image, max_plates=5):
    """
    Get multiple potential plate regions from an image using YOLO.
    
    Args:
        image: Input image
        max_plates: Maximum number of plates to return
    
    Returns:
        list: List of (plate_region, bounding_box) tuples
    """
    try:
        model = get_yolo_model()
        
        # Run inference
        results = model(image, conf=0.25, verbose=False)
        
        if not results or len(results) == 0:
            return []
        
        detections = results[0]
        
        if detections.boxes is None or len(detections.boxes) == 0:
            return []
        
        # Get bounding boxes and confidences
        boxes = detections.boxes.xyxy.cpu().numpy()
        confidences = detections.boxes.conf.cpu().numpy()
        
        plate_list = []
        
        for box, conf in zip(boxes, confidences):
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Ensure coordinates are within bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image.shape[1], x2)
            y2 = min(image.shape[0], y2)
            
            # Add padding
            padding = 5
            x1_padded = max(0, x1 - padding)
            y1_padded = max(0, y1 - padding)
            x2_padded = min(image.shape[1], x2 + padding)
            y2_padded = min(image.shape[0], y2 + padding)
            
            # Extract plate region
            plate_region = image[y1_padded:y2_padded, x1_padded:x2_padded]
            
            if plate_region.size > 0:  # Only add non-empty regions
                plate_list.append((
                    plate_region,
                    (x1_padded, y1_padded, x2_padded - x1_padded, y2_padded - y1_padded),
                    float(conf)
                ))
        
        # Sort by confidence and take top max_plates
        plate_list.sort(key=lambda x: x[2], reverse=True)
        
        # Return only the regions and bounding boxes (without confidence)
        return [(region, bbox) for region, bbox, _ in plate_list[:max_plates]]
    
    except Exception as e:
        print(f"Error in multi-plate YOLO detection: {str(e)}")
        return []


def detect_license_plate(image):
    """
    Detect a license plate in an image using the license plate detector model.
    
    This function runs YOLO inference on the input image and returns the
    cropped license plate region if detected, or None if no plate is found.
    
    Args:
        image: Input image in BGR format (OpenCV format)
    
    Returns:
        np.ndarray: Cropped license plate image if detected
        None: If no license plate is detected
    """
    try:
        # Run detection using the standard detection function
        plate_region, bounding_box = detect_plate_region(image)
        
        if plate_region is None:
            return None
        
        return plate_region
    
    except Exception as e:
        print(f"Error in detect_license_plate: {str(e)}")
        return None
