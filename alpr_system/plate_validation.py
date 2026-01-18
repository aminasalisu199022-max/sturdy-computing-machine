"""
Nigerian License Plate Validation Module

Validates Nigerian license plates against official formats:
- Personal/Private (BLUE): AAA-123-AA or AAA123AA
- Commercial (RED): AA-123-AAA or AA123AAA
- Government (GREEN): FG-123-AA or AA-456-FG

Author: ALPR System
Date: January 2026
"""

import re


# Nigerian state codes (2-letter abbreviations)
NIGERIAN_STATE_CODES = {
    'LA': 'Lagos',
    'KD': 'Kaduna',
    'AB': 'Abuja',
    'OG': 'Ogun',
    'RI': 'Rivers',
    'KT': 'Katsina',
    'KN': 'Kano',
    'FC': 'Federal',
    'FG': 'Federal',
}


def normalize_plate_text(text):
    """
    Normalize plate text by cleaning and standardizing format.
    
    Args:
        text: Raw OCR text
    
    Returns:
        str: Normalized text (uppercase, spaces removed)
    """
    # Convert to uppercase
    text = text.upper().strip()
    
    # Remove all spaces
    text = text.replace(' ', '')
    
    # Remove hyphens for processing (will add back if needed)
    text = text.replace('-', '')
    
    # Keep only alphanumeric characters
    text = re.sub(r'[^A-Z0-9]', '', text)
    
    return text


def correct_common_ocr_errors(text):
    """
    Correct common OCR errors in license plate text.
    
    Conversions: O→0, I→1, Z→2, S→5, B→8
    
    Args:
        text: Text potentially containing OCR errors
    
    Returns:
        str: Corrected text
    """
    corrections = {
        'O': '0',  # Letter O to digit 0
        'I': '1',  # Letter I to digit 1  
        'Z': '2',  # Letter Z to digit 2
        'S': '5',  # Letter S to digit 5
        'B': '8',  # Letter B to digit 8
    }
    
    # Be very conservative: only correct if BOTH sides are digits
    result = list(text)
    
    # Analyze the text structure
    for i, char in enumerate(result):
        if char in corrections:
            # Get surrounding context
            before = result[i-1] if i > 0 else ''
            after = result[i+1] if i < len(result) - 1 else ''
            
            # Heuristic: only correct if BOTH sides are digits (surrounded by numbers)
            before_is_digit = before.isdigit()
            after_is_digit = after.isdigit()
            
            # Only apply correction if surrounded on BOTH sides by digits
            if before_is_digit and after_is_digit:
                result[i] = corrections[char]
    
    return ''.join(result)


def validate_personal_plate(text):
    """
    Validate Personal/Private license plate format (BLUE).
    
    Format: AAA-123-AA (3 letters, 3 digits, 2 letters)
    Example: KTS-123-AB
    
    Args:
        text: Normalized plate text
    
    Returns:
        tuple: (is_valid, formatted_text, confidence)
    """
    text = correct_common_ocr_errors(text)
    
    # Pattern: 3 letters + 3 digits + 2 letters (8 chars total)
    pattern = r'^([A-Z]{3})(\d{3})([A-Z]{2})$'
    
    match = re.match(pattern, text)
    if match:
        state_code = match.group(1)[:2]  # First 2 letters = state
        numbers = match.group(2)
        letters = match.group(3)
        
        # Format with hyphens
        formatted = f"{state_code}{match.group(1)[2]}-{numbers}-{letters}"
        
        return True, formatted, 0.95
    
    return False, text, 0.0


def validate_commercial_plate(text):
    """
    Validate Commercial license plate format (RED).
    
    Format: AA-123-AAA (2 letters, 3 digits, 3 letters)
    Example: KT-234-KTN
    
    Args:
        text: Normalized plate text
    
    Returns:
        tuple: (is_valid, formatted_text, confidence)
    """
    text = correct_common_ocr_errors(text)
    
    # Pattern: 2 letters + 3 digits + 3 letters (8 chars total)
    pattern = r'^([A-Z]{2})(\d{3})([A-Z]{3})$'
    
    match = re.match(pattern, text)
    if match:
        state_code = match.group(1)
        numbers = match.group(2)
        letters = match.group(3)
        
        # Format with hyphens
        formatted = f"{state_code}-{numbers}-{letters}"
        
        return True, formatted, 0.95
    
    return False, text, 0.0


def validate_government_plate(text):
    """
    Validate Government license plate format (GREEN).
    
    Format: FG-123-AA or AA-456-FG
    
    Args:
        text: Normalized plate text
    
    Returns:
        tuple: (is_valid, formatted_text, confidence)
    """
    text = correct_common_ocr_errors(text)
    
    # Pattern 1: FG-123-AA
    pattern1 = r'^FG(\d{3})([A-Z]{2})$'
    match = re.match(pattern1, text)
    if match:
        formatted = f"FG-{match.group(1)}-{match.group(2)}"
        return True, formatted, 0.95
    
    # Pattern 2: AA-456-FG
    pattern2 = r'^([A-Z]{2})(\d{3})FG$'
    match = re.match(pattern2, text)
    if match:
        formatted = f"{match.group(1)}-{match.group(2)}-FG"
        return True, formatted, 0.95
    
    return False, text, 0.0


def detect_plate_type_from_format(text):
    """
    Detect plate type from text format.
    
    Args:
        text: Normalized plate text
    
    Returns:
        str: Plate type (Personal, Commercial, Government, Unknown)
    """
    text = correct_common_ocr_errors(text)
    
    # Check Personal format: 3 letters + 3 digits + 2 letters
    if re.match(r'^[A-Z]{3}\d{3}[A-Z]{2}$', text):
        return 'Personal'
    
    # Check Commercial format: 2 letters + 3 digits + 3 letters
    if re.match(r'^[A-Z]{2}\d{3}[A-Z]{3}$', text):
        return 'Commercial'
    
    # Check Government format: FG + 3 digits + 2 letters
    if re.match(r'^FG\d{3}[A-Z]{2}$', text):
        return 'Government'
    
    # Check Government format: 2 letters + 3 digits + FG
    if re.match(r'^[A-Z]{2}\d{3}FG$', text):
        return 'Government'
    
    return 'Unknown'


def validate_nigerian_plate(text):
    """
    Validate Nigerian license plate and return comprehensive validation result.
    
    Args:
        text: OCR-extracted plate text
    
    Returns:
        dict: {
            'is_valid': bool,
            'plate_number': str (formatted),
            'plate_type': str (Personal/Commercial/Government),
            'confidence': float (0.0-1.0),
            'state_code': str,
            'message': str
        }
    """
    # Normalize input
    normalized = normalize_plate_text(text)
    
    if not normalized or len(normalized) < 7:
        return {
            'is_valid': False,
            'plate_number': text,
            'plate_type': 'Unknown',
            'confidence': 0.0,
            'state_code': '',
            'message': 'Plate text too short'
        }
    
    # Try Personal format first (3 letters, 3 digits, 2 letters - 8 chars)
    is_valid, formatted, confidence = validate_personal_plate(normalized)
    if is_valid:
        state_code = formatted[:2]
        state_name = NIGERIAN_STATE_CODES.get(state_code, 'Unknown')
        return {
            'is_valid': True,
            'plate_number': formatted,
            'plate_type': 'Personal',
            'confidence': confidence,
            'state_code': state_code,
            'state_name': state_name,
            'message': 'Valid Nigerian personal license plate'
        }
    
    # Try Commercial format (2 letters, 3 digits, 3 letters - 8 chars)
    is_valid, formatted, confidence = validate_commercial_plate(normalized)
    if is_valid:
        state_code = formatted[:2]
        state_name = NIGERIAN_STATE_CODES.get(state_code, 'Unknown')
        return {
            'is_valid': True,
            'plate_number': formatted,
            'plate_type': 'Commercial',
            'confidence': confidence,
            'state_code': state_code,
            'state_name': state_name,
            'message': 'Valid Nigerian commercial license plate'
        }
    
    # Try Government format (FG-123-AA or AA-456-FG)
    is_valid, formatted, confidence = validate_government_plate(normalized)
    if is_valid:
        state_code = 'FG'
        state_name = 'Federal'
        return {
            'is_valid': True,
            'plate_number': formatted,
            'plate_type': 'Government',
            'confidence': confidence,
            'state_code': state_code,
            'state_name': state_name,
            'message': 'Valid Nigerian government license plate'
        }
    
    # If no format matches, return invalid
    detected_type = detect_plate_type_from_format(normalized)
    
    return {
        'is_valid': False,
        'plate_number': normalized,
        'plate_type': detected_type,
        'confidence': 0.3,
        'state_code': '',
        'message': f'Invalid Nigerian license plate format (detected as {detected_type})'
    }


def format_plate_with_hyphens(plate_number):
    """
    Format a plate number with hyphens according to its type.
    
    Args:
        plate_number: Plate number without formatting
    
    Returns:
        str: Formatted plate number
    """
    normalized = normalize_plate_text(plate_number)
    
    validation = validate_nigerian_plate(normalized)
    if validation['is_valid']:
        return validation['plate_number']
    
    return normalized
