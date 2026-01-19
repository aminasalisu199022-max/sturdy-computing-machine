"""
Nigerian License Plate Validation Module

Validates Nigerian license plates using the simple format:
AAA-123AA (3 letters - 3 digits - 2 letters)

Example: KTS-123AB
Regex: ^[A-Z]{3}-[0-9]{3}[A-Z]{2}$

Author: ALPR System
Date: January 2026
"""

import re


def normalize_plate(text):
    """
    Normalize Nigerian license plate text with OCR error correction.
    
    Pipeline:
    1. Convert text to uppercase
    2. Remove all non-alphanumeric characters
    3. Format to expected 8-character length (3 letters + 3 digits + 2 letters)
    4. Apply context-aware OCR corrections:
       - In letter positions: 5 → S, 8 → B, 1 → I
       - In digit positions: O → 0, I → 1
       - Throughout: 0 → 0 in numbers, O → O in letters
    5. Add hyphen in correct position
    
    Nigerian format: AAA-123AA (3 letters - 3 digits - 2 letters)
    
    Example:
        normalize_plate("kts-123ab") → "KTS-123AB"
        normalize_plate("kts123ab") → "KTS-123AB"
        normalize_plate("k75123ab") → "KIS-123AB" (5→S in letter position)
    
    Args:
        text: Raw OCR text or user input
    
    Returns:
        str: Formatted plate text with hyphen, or original if wrong length
    """
    # Step 1: Convert to uppercase
    text = text.upper()
    
    # Step 2: Remove all non-alphanumeric characters
    text = re.sub(r'[^A-Z0-9]', '', text)
    
    # Step 3: If we don't have enough characters, return as-is
    if len(text) < 8:
        return text
    
    # Step 4: Extract sections (first 8 chars only)
    letters_prefix = text[:3]  # Should be letters
    numbers = text[3:6]         # Should be digits
    letters_suffix = text[6:8]  # Should be letters
    
    # Step 5: Apply context-aware corrections
    
    # Correct letter prefix (positions 0-2)
    # Common OCR errors: 5→S, 8→B, 1→I, 0→O
    letters_prefix = ''.join([
        ('S' if c == '5' else 
         'B' if c == '8' else 
         'I' if c == '1' else 
         'O' if c == '0' else 
         c)
        for c in letters_prefix
    ])
    
    # Correct numbers (positions 3-5)
    # Common OCR errors: O→0, I→1, S→5, B→8
    numbers = ''.join([
        ('0' if c == 'O' else 
         '1' if c == 'I' else 
         '5' if c == 'S' else 
         '8' if c == 'B' else 
         c)
        for c in numbers
    ])
    
    # Correct letter suffix (positions 6-7)
    # Same as prefix: 5→S, 8→B, 1→I, 0→O
    letters_suffix = ''.join([
        ('S' if c == '5' else 
         'B' if c == '8' else 
         'I' if c == '1' else 
         'O' if c == '0' else 
         c)
        for c in letters_suffix
    ])
    
    # Step 6: Format with hyphen
    return f"{letters_prefix}-{numbers}{letters_suffix}"


def is_valid_nigerian_plate(text):
    """
    Check if text matches valid Nigerian license plate format.
    
    Format: AAA-123AA
    - 3 uppercase letters
    - 1 hyphen
    - 3 digits
    - 2 uppercase letters
    
    Example: KTS-123AB
    
    Args:
        text: Text to validate
    
    Returns:
        bool: True if valid Nigerian plate format
    """
    pattern = r'^[A-Z]{3}-[0-9]{3}[A-Z]{2}$'
    return bool(re.match(pattern, text))


def normalize_plate_text(text):
    """
    Normalize plate text for validation.
    
    Args:
        text: Raw OCR text
    
    Returns:
        str: Normalized text (uppercase, cleaned)
    """
    # Convert to uppercase
    text = text.upper().strip()
    
    # Remove spaces
    text = text.replace(' ', '')
    
    # Keep only alphanumeric and hyphen
    text = re.sub(r'[^A-Z0-9\-]', '', text)
    
    return text


def correct_ocr_errors(text):
    """
    Correct common OCR errors in license plate text.
    
    Context-aware corrections:
    - 5 → S (in letter positions)
    - 8 → B (in letter positions)
    - 0 ↔ O (context-based: 0 in digit section, O in letter section)
    - 1 → I (only in letter positions, when surrounded by letters)
    
    Args:
        text: Text potentially containing OCR errors
    
    Returns:
        str: Corrected text
    """
    if not text or len(text) < 3:
        return text
    
    text = text.upper()
    result = list(text)
    
    # For Nigerian plates: AAA-###AA
    # Positions 0-2: letters (A)
    # Positions 4-6: digits (#)
    # Positions 7-8: letters (A)
    # Position 3: hyphen (-)
    
    # First, handle the basic replacements
    # 5 → S (convert digit 5 to letter S)
    # 8 → B (convert digit 8 to letter B)
    for i in range(len(result)):
        if result[i] == '5':
            result[i] = 'S'
        elif result[i] == '8':
            result[i] = 'B'
    
    # Now handle 0/O context-aware correction
    for i in range(len(result)):
        if result[i] in ('0', 'O'):
            # In digit positions (after hyphen): should be 0
            if i >= 4 and i <= 6:
                result[i] = '0'
            # In letter positions: should be O
            elif i in (0, 1, 2, 7, 8):
                result[i] = 'O'
    
    # Handle 1/I in letter positions
    for i in range(len(result)):
        if result[i] == '1' and i in (0, 1, 2, 7, 8):
            # Only correct if surrounded by letters or at word boundary
            result[i] = 'I'
    
    return ''.join(result)


def format_plate_with_hyphen(normalized_text):
    """
    Format normalized plate text with hyphen in correct position.
    
    Takes cleaned text like "KTS123AB" and formats to "KTS-123AB"
    
    Args:
        normalized_text: Cleaned plate text without hyphen
    
    Returns:
        str: Formatted plate with hyphen, or original if wrong length
    """
    # Remove any existing hyphens first
    clean_text = normalized_text.replace('-', '')
    
    # Should be 8 characters: 3 letters + 3 digits + 2 letters
    if len(clean_text) != 8:
        return normalized_text
    
    # Format: AAA-123AA
    formatted = f"{clean_text[:3]}-{clean_text[3:6]}{clean_text[6:8]}"
    
    return formatted


def validate_and_format_plate(text):
    """
    Validate and format a Nigerian license plate.
    
    Complete pipeline:
    1. Normalize using normalize_plate()
    2. Validate format
    
    Args:
        text: Raw plate text
    
    Returns:
        tuple: (is_valid, formatted_plate)
            - is_valid: bool (True if valid format)
            - formatted_plate: str (formatted plate or None)
    """
    # Use the improved normalize_plate function
    normalized = normalize_plate(text)
    
    # Validate the normalized format
    is_valid = is_valid_nigerian_plate(normalized)
    
    return is_valid, normalized if is_valid else None
