
import cv2
from datetime import datetime
from . import detector
from . import ocr
from . import plate_color
from . import vehicle_db
from . import plate_validation
from . import utils


def run_alpr(image_or_video_path):
    """
    Main ALPR function - runs the complete license plate recognition pipeline.
    
    This function:
    1. Loads the image or video
    2. Detects the license plate region
    3. Performs OCR to extract text
    4. Classifies plate type by color
    5. Looks up vehicle information in database
    6. Returns comprehensive results
    
    Args:
        image_or_video_path: Path to image (.jpg, .png) or video (.mp4, .avi) file
    
    Returns:
        dict: Detection results with keys:
            - success: bool (True if plate detected)
            - message: str (status message)
            - results: list (list of detected plates if successful)
            - timestamp: str
            - processed_image: np.ndarray (image with bounding boxes)
    """
    
    # Determine file type
    is_video = utils.is_video_file(image_or_video_path)
    is_image = utils.is_image_file(image_or_video_path)
    
    if not is_image and not is_video:
        return {
            'success': False,
            'message': 'Invalid file type. Please upload an image (.jpg, .png) or video (.mp4, .avi)',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }
    
    try:
        if is_image:
            return _process_image(image_or_video_path)
        else:
            return _process_video(image_or_video_path)
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing file: {str(e)}',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }


def _process_image(image_path):
    """
    Process a single image for ALPR.
    
    Args:
        image_path: Path to image file
    
    Returns:
        dict: Detection results
    """
    # Load image
    image = utils.load_image(image_path)
    if image is None:
        return {
            'success': False,
            'message': 'Failed to load image. Please check the file.',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }
    
    # Resize for processing if too large
    display_image = utils.resize_image(image, max_width=800, max_height=600)
    
    # Detect plate region
    plate_region, bounding_box = detector.detect_plate_region(display_image)
    
    if plate_region is None:
        return {
            'success': False,
            'message': 'No license plate detected. Please upload a clearer image.',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': display_image
        }
    
    # Extract text from plate
    raw_text = ocr.extract_text_from_plate(plate_region)
    
    # Validate using Nigerian plate format
    validation_result = plate_validation.validate_nigerian_plate(raw_text)
    
    if not validation_result['is_valid']:
        return {
            'success': False,
            'message': f"Invalid Nigerian license plate format: {validation_result['message']}",
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': detector.draw_bounding_box(display_image, bounding_box)
        }
    
    formatted_text = validation_result['plate_number']
    plate_type_from_validation = validation_result['plate_type']
    
    # Classify plate by color (for additional confirmation)
    plate_color_name = plate_color.get_plate_color(plate_region)
    plate_type_from_color = plate_color.classify_plate_type(plate_color_name)
    
    # Prefer the type from validation, but note the color
    plate_type = plate_type_from_validation
    
    # Look up vehicle in database
    vehicle_info = vehicle_db.lookup_vehicle(formatted_text)
    
    # Build result with comprehensive information
    result = {
        'plate_number': formatted_text,
        'plate_color': plate_color_name,
        'plate_type': plate_type,
        'plate_type_color_based': plate_type_from_color,
        'ocr_confidence': validation_result.get('confidence', 0.9),
        'owner_name': vehicle_info.get('owner_name', 'Vehicle details not found') if vehicle_info else 'Vehicle details not found',
        'state': vehicle_info.get('state', 'Unknown') if vehicle_info else 'Unknown',
        'vehicle_type': vehicle_info.get('vehicle_type', 'Unknown') if vehicle_info else 'Unknown',
        'vehicle_color': vehicle_info.get('color', 'Unknown') if vehicle_info else 'Unknown',
        'year': vehicle_info.get('year', None) if vehicle_info else None,
        'registered': vehicle_info is not None,
        'state_code': validation_result.get('state_code', ''),
        'timestamp': utils.get_timestamp()
    }
    
    # Draw bounding box on image with colored outline based on type
    color_map = {
        'Personal': (0, 0, 255),      # Blue for personal
        'Commercial': (0, 165, 255),  # Orange for commercial
        'Government': (0, 255, 0)     # Green for government
    }
    box_color = color_map.get(plate_type, (0, 255, 255))
    
    processed_image = detector.draw_bounding_box(display_image, bounding_box, color=box_color, thickness=3)
    
    # Add comprehensive text annotations
    y_offset = 30
    cv2.putText(processed_image, f"Plate: {formatted_text}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)
    y_offset += 30
    cv2.putText(processed_image, f"Type: {plate_type}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
    y_offset += 30
    cv2.putText(processed_image, f"Owner: {result['owner_name']}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    y_offset += 25
    cv2.putText(processed_image, f"Vehicle: {result['vehicle_type']}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    return {
        'success': True,
        'message': f'Successfully detected plate: {formatted_text}',
        'results': [result],
        'timestamp': utils.get_timestamp(),
        'processed_image': processed_image
    }


def _process_video(video_path):
    """
    Process a video for ALPR by extracting frames.
    
    Args:
        video_path: Path to video file
    
    Returns:
        dict: Detection results from all frames
    """
    # Get video info
    video_info = utils.get_video_info(video_path)
    if not video_info:
        return {
            'success': False,
            'message': 'Failed to read video file.',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }
    
    # Extract frames (one frame per second)
    frames = utils.extract_frames_from_video(video_path, frame_interval=int(video_info['fps']))
    
    if not frames:
        return {
            'success': False,
            'message': 'Failed to extract frames from video.',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }
    
    # Process each frame
    all_results = []
    processed_frames = []
    
    for frame_idx, frame in enumerate(frames):
        # Resize frame for processing
        display_frame = utils.resize_image(frame, max_width=800, max_height=600)
        
        # Detect plate
        plate_region, bounding_box = detector.detect_plate_region(display_frame)
        
        if plate_region is None:
            continue
        
        # Extract text
        raw_text = ocr.extract_text_from_plate(plate_region)
        
        # Validate using Nigerian plate format
        validation_result = plate_validation.validate_nigerian_plate(raw_text)
        
        if not validation_result['is_valid']:
            continue
        
        formatted_text = validation_result['plate_number']
        
        # Skip if we already have this plate
        if any(r['plate_number'] == formatted_text for r in all_results):
            continue
        
        # Classify plate by color
        plate_color_name = plate_color.get_plate_color(plate_region)
        plate_type_from_color = plate_color.classify_plate_type(plate_color_name)
        plate_type_str = validation_result['plate_type']
        
        # Look up vehicle
        vehicle_info = vehicle_db.lookup_vehicle(formatted_text)
        
        # Build result
        result = {
            'plate_number': formatted_text,
            'plate_color': plate_color_name,
            'plate_type': plate_type_str,
            'ocr_confidence': validation_result.get('confidence', 0.9),
            'owner_name': vehicle_info.get('owner_name', 'Vehicle details not found') if vehicle_info else 'Vehicle details not found',
            'state': vehicle_info.get('state', 'Unknown') if vehicle_info else 'Unknown',
            'vehicle_type': vehicle_info.get('vehicle_type', 'Unknown') if vehicle_info else 'Unknown',
            'vehicle_color': vehicle_info.get('color', 'Unknown') if vehicle_info else 'Unknown',
            'year': vehicle_info.get('year', None) if vehicle_info else None,
            'registered': vehicle_info is not None,
            'frame_number': frame_idx,
            'state_code': validation_result.get('state_code', ''),
            'timestamp': utils.get_timestamp()
        }
        
        all_results.append(result)
        
        # Draw on frame with color based on plate type
        color_map = {
            'Personal': (0, 0, 255),      # Blue for personal
            'Commercial': (0, 165, 255),  # Orange for commercial
            'Government': (0, 255, 0)     # Green for government
        }
        box_color = color_map.get(plate_type_str, (0, 255, 255))
        
        processed_frame = detector.draw_bounding_box(display_frame, bounding_box, color=box_color, thickness=3)
        cv2.putText(processed_frame, f"Plate: {formatted_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
        cv2.putText(processed_frame, f"Type: {plate_type_str}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 1)
        cv2.putText(processed_frame, f"Owner: {result['owner_name']}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        processed_frames.append(processed_frame)
    
    if not all_results:
        return {
            'success': False,
            'message': 'No license plates detected in video. Please use a clearer video.',
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': None
        }
    
    # Return first processed frame and all results
    return {
        'success': True,
        'message': f'Successfully detected {len(all_results)} unique plate(s) in video',
        'results': all_results,
        'timestamp': utils.get_timestamp(),
        'processed_image': processed_frames[0] if processed_frames else frames[0]
    }


def get_result_summary(result):
    """
    Create a human-readable summary of detection results.
    
    Args:
        result: Detection result from run_alpr()
    
    Returns:
        str: Formatted summary text
    """
    if not result['success']:
        return f"❌ {result['message']}"
    
    summary = f"✅ Detection Successful\n\n"
    summary += f"Timestamp: {result['timestamp']}\n"
    summary += f"Plates Found: {len(result['results'])}\n\n"
    
    for i, plate_result in enumerate(result['results'], 1):
        summary += f"--- Plate {i} ---\n"
        summary += f"Plate Number: {plate_result['plate_number']}\n"
        summary += f"Plate Type: {plate_result['plate_type']}\n"
        summary += f"Plate Color: {plate_result['plate_color']}\n"
        summary += f"Owner: {plate_result['owner_name']}\n"
        summary += f"State: {plate_result['state']}\n"
        summary += f"Registered: {'Yes' if plate_result['registered'] else 'No'}\n"
        summary += f"Vehicle: {plate_result['vehicle_type']}\n"
        summary += f"Year: {plate_result.get('year', 'N/A')}\n\n"
    
    return summary
