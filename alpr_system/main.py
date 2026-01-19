
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
    
    # Detect license plate region - also get bounding box for drawing
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
    
    # Validate and format using Nigerian plate format (AAA-123AA)
    is_valid, formatted_text = plate_validation.validate_and_format_plate(raw_text)
    
    if not is_valid:
        return {
            'success': False,
            'message': f"Invalid Nigerian license plate format",
            'results': [],
            'timestamp': utils.get_timestamp(),
            'processed_image': detector.draw_bounding_box(display_image, bounding_box)
        }
    
    # Look up vehicle in database
    vehicle_info = vehicle_db.lookup_vehicle(formatted_text)
    
    # Build result with comprehensive information
    result = {
        'plate_number': formatted_text,
        'plate_color': 'Unknown',
        'plate_type': 'Unknown',
        'ocr_confidence': 0.85,
        'owner_name': vehicle_info.get('owner_name') if vehicle_info else 'Unknown',
        'state': vehicle_info.get('state') if vehicle_info else 'Unknown',
        'vehicle_type': vehicle_info.get('vehicle_type') if vehicle_info else 'Unknown',
        'registered': vehicle_info is not None,
        'timestamp': utils.get_timestamp()
    }
    
    # If vehicle is found, get additional details
    if vehicle_info:
        result['plate_color'] = vehicle_info.get('plate_color', 'Unknown')
        result['plate_type'] = vehicle_info.get('plate_type', 'Unknown')
    
    # Draw bounding box on image
    processed_image = detector.draw_bounding_box(display_image, bounding_box, color=(0, 255, 0), thickness=2)
    
    # Add text annotations
    cv2.putText(processed_image, f"Plate: {formatted_text}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    if result['registered']:
        cv2.putText(processed_image, f"Owner: {result['owner_name']}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    return {
        'success': True,
        'message': f'Plate detected: {formatted_text}',
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
        
        # Validate and format using Nigerian plate format
        is_valid, formatted_text = plate_validation.validate_and_format_plate(raw_text)
        
        if not is_valid:
            continue
        
        # Skip if we already have this plate
        if any(r['plate_number'] == formatted_text for r in all_results):
            continue
        
        # Look up vehicle
        vehicle_info = vehicle_db.lookup_vehicle(formatted_text)
        
        # Build result
        result = {
            'plate_number': formatted_text,
            'plate_color': 'Unknown',
            'plate_type': 'Unknown',
            'ocr_confidence': 0.85,
            'owner_name': vehicle_info.get('owner_name') if vehicle_info else 'Unknown',
            'state': vehicle_info.get('state') if vehicle_info else 'Unknown',
            'vehicle_type': vehicle_info.get('vehicle_type') if vehicle_info else 'Unknown',
            'registered': vehicle_info is not None,
            'frame_number': frame_idx,
            'timestamp': utils.get_timestamp()
        }
        
        # Get plate details from vehicle info if available
        if vehicle_info:
            result['plate_color'] = vehicle_info.get('plate_color', 'Unknown')
            result['plate_type'] = vehicle_info.get('plate_type', 'Unknown')
        
        all_results.append(result)
        
        # Draw on frame
        processed_frame = detector.draw_bounding_box(display_frame, bounding_box, color=(0, 255, 0), thickness=2)
        cv2.putText(processed_frame, f"Plate: {formatted_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if result['registered']:
            cv2.putText(processed_frame, f"Owner: {result['owner_name']}", (10, 60),
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
