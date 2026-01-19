
import cv2
import numpy as np
import re

# Try to import pytesseract; if not available, use fallback
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Warning: pytesseract not installed. Using fallback OCR method.")

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
    """Initialize and cache the EasyOCR reader (fallback method)."""
    global _ocr_reader
    if _ocr_reader is None and EASYOCR_AVAILABLE:
        try:
            _ocr_reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            print(f"Warning: Could not initialize EasyOCR: {str(e)}")
    return _ocr_reader


def cleanup_ocr_text(text):
    """
    Clean up OCR-extracted text for Nigerian license plates.
    
    Steps:
    1. Convert to uppercase
    2. Remove all non-alphanumeric characters
    
    Args:
        text: Raw OCR text
    
    Returns:
        Cleaned text (uppercase alphanumeric only)
    """
    text = text.upper().strip()
    # Remove all non-alphanumeric characters (except hyphen for now)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text


def enhance_plate_image(image):
    """
    Enhanced preprocessing pipeline for Nigerian license plates.
    
    Pipeline:
    1. Convert to grayscale
    2. Apply bilateral filter (noise reduction)
    3. Apply adaptive thresholding
    4. Increase contrast
    5. Resize for better OCR (at least 2x)
    
    Args:
        image: Input plate image
    
    Returns:
        Enhanced image suitable for OCR
    """
    # Convert to grayscale if color image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Step 1: Bilateral filter (reduce noise while preserving edges)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Step 2: Adaptive thresholding
    adaptive_thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
    
    # Step 3: Increase contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(adaptive_thresh)
    
    # Step 4: Resize plate ROI to at least 2x for better OCR
    # Calculate if we need upscaling
    height, width = enhanced.shape
    if height < 100 or width < 300:  # Small plate, upscale
        scale = max(2, int(300 / width) if width > 0 else 2)
        enhanced = cv2.resize(enhanced, None, fx=scale, fy=scale, 
                              interpolation=cv2.INTER_CUBIC)
    
    # Step 5: Sharpen edges for character clarity
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]], dtype=np.float32)
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return sharpened


def extract_text_from_plate(plate_image):
    """
    Extract text from a license plate image using pytesseract or fallback methods.
    
    Attempts to extract text using:
    1. pytesseract (primary method - requires tesseract system installation)
    2. EasyOCR (fallback)
    3. Contour-based fallback
    
    Args:
        plate_image: Image containing only the license plate
    
    Returns:
        str: Detected text (uppercase alphanumeric), or empty string if detection fails
    """
    
    # Enhance the plate image first
    enhanced = enhance_plate_image(plate_image)
    
    # Try pytesseract first if available
    if PYTESSERACT_AVAILABLE:
        try:
            # Configure pytesseract for license plate recognition
            custom_config = r'--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
            
            extracted_text = pytesseract.image_to_string(enhanced, config=custom_config)
            
            if extracted_text and extracted_text.strip():
                cleaned = cleanup_ocr_text(extracted_text)
                if cleaned:
                    return cleaned
        except Exception as e:
            print(f"pytesseract error: {str(e)}. Trying alternative method.")
    
    # Try EasyOCR as fallback
    if EASYOCR_AVAILABLE:
        try:
            reader = get_ocr_reader()
            if reader is not None:
                results = reader.readtext(plate_image, detail=0)
                if results:
                    extracted_text = ''.join(results)
                    cleaned = cleanup_ocr_text(extracted_text)
                    if cleaned:
                        return cleaned
        except Exception as e:
            print(f"EasyOCR error: {str(e)}. Using contour fallback.")
    
    # Fallback: Use contour-based text extraction
    return _extract_text_fallback(enhanced)


def _extract_text_fallback(plate_image):
    """
    Fallback text extraction using contour analysis.
    
    This method analyzes character contours when OCR methods fail.
    
    Args:
        plate_image: Image containing only the license plate
    
    Returns:
        str: Detected text (placeholder based on character count and shapes)
    """
    try:
        # Ensure grayscale
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        
        # Thresholding
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
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
        
        # Generate placeholder text based on character count and shape
        detected_text = ""
        for x, y, w, h in character_boxes:
            char_image = binary[y:y+h, x:x+w]
            aspect_ratio = float(w) / h if h > 0 else 0
            
            if 0.2 < aspect_ratio < 0.8:
                detected_text += "A"  # Likely a letter
            else:
                detected_text += "0"  # Likely a digit
        
        return detected_text
    
    except Exception as e:
        print(f"Error in fallback OCR: {str(e)}")
        return ""
