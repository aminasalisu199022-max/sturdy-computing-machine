
import cv2
import numpy as np
from datetime import datetime
import os
import tempfile


def load_image(image_path):
    """
    Load an image from file.
    
    Args:
        image_path: Path to image file
    
    Returns:
        np.ndarray: Image in BGR format, or None if loading fails
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def load_image_from_bytes(image_bytes):
    """
    Load an image from bytes (useful for file uploads in Streamlit).
    
    Args:
        image_bytes: Image data as bytes
    
    Returns:
        np.ndarray: Image in BGR format
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def save_image(image, output_path):
    """
    Save an image to file.
    
    Args:
        image: Image array (BGR format)
        output_path: Path where to save
    
    Returns:
        bool: True if saved successfully
    """
    try:
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def resize_image(image, max_width=800, max_height=600):
    """
    Resize image to fit within max dimensions while maintaining aspect ratio.
    
    Args:
        image: Input image
        max_width: Maximum width
        max_height: Maximum height
    
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    # Calculate scaling factor
    scale = min(max_width / w, max_height / h, 1.0)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def convert_bgr_to_rgb(image):
    """
    Convert image from BGR (OpenCV) to RGB (display format).
    
    Args:
        image: Image in BGR format
    
    Returns:
        Image in RGB format
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def get_image_dimensions(image):
    """
    Get image dimensions.
    
    Args:
        image: Input image
    
    Returns:
        tuple: (height, width, channels)
    """
    return image.shape


def crop_image(image, x, y, w, h):
    """
    Crop a region from an image.
    
    Args:
        image: Input image
        x, y: Top-left corner
        w, h: Width and height
    
    Returns:
        Cropped image region
    """
    return image[y:y+h, x:x+w]


def extract_frames_from_video(video_path, frame_interval=30):
    """
    Extract frames from a video file.
    
    Args:
        video_path: Path to video file
        frame_interval: Extract every Nth frame (e.g., 30 = 30 fps = 1 frame per second)
    
    Returns:
        list: List of frames (as numpy arrays)
    """
    frames = []
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
    except Exception as e:
        print(f"Error extracting frames: {e}")
    
    return frames


def get_video_info(video_path):
    """
    Get information about a video file.
    
    Args:
        video_path: Path to video file
    
    Returns:
        dict: Video information (width, height, fps, frame_count, duration)
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None


def get_timestamp():
    """
    Get current timestamp in a readable format.
    
    Returns:
        str: Current date and time
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp_iso():
    """
    Get current timestamp in ISO format.
    
    Returns:
        str: ISO format timestamp
    """
    return datetime.now().isoformat()


def bytes_to_image(image_bytes):
    """
    Convert bytes to OpenCV image.
    
    Args:
        image_bytes: Image as bytes
    
    Returns:
        np.ndarray: Image array or None
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error converting bytes: {e}")
        return None


def image_to_bytes(image):
    """
    Convert OpenCV image to bytes.
    
    Args:
        image: Image array
    
    Returns:
        bytes: Image encoded as JPEG bytes
    """
    try:
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
    except Exception as e:
        print(f"Error converting image to bytes: {e}")
        return None


def save_temp_image(image, suffix='.jpg'):
    """
    Save image to a temporary file.
    
    Args:
        image: Image array
        suffix: File extension
    
    Returns:
        str: Path to temporary file
    """
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        cv2.imwrite(temp_file.name, image)
        return temp_file.name
    except Exception as e:
        print(f"Error saving temp image: {e}")
        return None


def cleanup_temp_file(file_path):
    """
    Delete a temporary file.
    
    Args:
        file_path: Path to file
    
    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting temp file: {e}")
        return False


def is_image_file(filename):
    """
    Check if filename is an image file.
    
    Args:
        filename: Filename or path
    
    Returns:
        bool: True if image file
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    _, ext = os.path.splitext(filename.lower())
    return ext in image_extensions


def is_video_file(filename):
    """
    Check if filename is a video file.
    
    Args:
        filename: Filename or path
    
    Returns:
        bool: True if video file
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
    _, ext = os.path.splitext(filename.lower())
    return ext in video_extensions


def get_file_extension(filename):
    """
    Get file extension.
    
    Args:
        filename: Filename or path
    
    Returns:
        str: File extension (with dot)
    """
    _, ext = os.path.splitext(filename.lower())
    return ext
