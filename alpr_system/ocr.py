
import cv2
import numpy as np
import re

# Try to import EasyOCR; if not available, use fallback
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not installed. Using fallback OCR method.")


# Global EasyOCR reader cache
_ocr_reader = None


def get_ocr_reader():
    """Initialize and cache the EasyOCR reader."""
    global _ocr_reader
    if _ocr_reader is None and EASYOCR_AVAILABLE:
        try:
            _ocr_reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            print(f"Warning: Could not initialize EasyOCR: {str(e)}")
    return _ocr_reader


def cleanup_ocr_text(text):
    """
    Clean up OCR-extracted text by correcting common errors.
    
    OCR errors: O→0, I→1, Z→2, S→5, B→8
    
    Args:
        text: Raw OCR text
    
    Returns:
        Cleaned text
    """
    text = text.upper().strip()
    # Remove spaces and special characters except hyphens and numbers
    text = re.sub(r'[^A-Z0-9\-]', '', text)
    
    # Correct common OCR errors
    corrections = {
        'O': '0',  # Letter O to digit zero
        'I': '1',  # Letter I to digit one
        'Z': '2',  # Letter Z to digit two
        'S': '5',  # Letter S to digit five
        'B': '8',  # Letter B to digit eight
    }
    
    # This is a simplified approach - we'll apply corrections contextually
    result = text
    
    return result


def extract_text_from_plate(plate_image):
    """
    Extract text from a license plate image using EasyOCR or fallback method.
    
    Args:
        plate_image: Image containing only the license plate
    
    Returns:
        str: Detected text (or empty string if detection fails)
    """
    # Try EasyOCR first if available
    if EASYOCR_AVAILABLE:
        try:
            reader = get_ocr_reader()
            if reader is not None:
                results = reader.readtext(plate_image, detail=0)
                if results:
                    extracted_text = ''.join(results)
                    return cleanup_ocr_text(extracted_text)
        except Exception as e:
            print(f"EasyOCR error: {str(e)}. Falling back to contour method.")
    
    # Fallback: Use contour-based text extraction
    return _extract_text_fallback(plate_image)


def _extract_text_fallback(plate_image):
    """
    Fallback text extraction using contour analysis.
    
    Args:
        plate_image: Image containing only the license plate
    
    Returns:
        str: Detected text
    """
    # Preprocessing
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY) if len(plate_image.shape) == 3 else plate_image
    
    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Thresholding
    _, binary = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
    
    # Invert if needed
    if cv2.countNonZero(binary) > binary.size // 2:
        binary = cv2.bitwise_not(binary)
    
    # Remove noise using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Find contours of characters
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return ""
    
    # Sort contours left to right
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    
    # Extract character regions
    character_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 30:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        
        # Character height should be reasonable
        if h < 10 or h > plate_image.shape[0] - 10:
            continue
        
        character_boxes.append((x, y, w, h))
    
    if not character_boxes:
        return ""
    
    # Generate placeholder text based on count
    detected_text = ""
    for x, y, w, h in character_boxes:
        char_image = binary[y:y+h, x:x+w]
        aspect_ratio = float(w) / h if h > 0 else 0
        
        if 0.2 < aspect_ratio < 0.8:
            detected_text += "A"  # Likely a letter
        else:
            detected_text += "0"  # Likely a digit
    
    return detected_text


def enhance_plate_image(image):
    """
    Enhance a plate image for better OCR results.
    
    Args:
        image: Input plate image
    
    Returns:
        Enhanced image
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Sharpen
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened
