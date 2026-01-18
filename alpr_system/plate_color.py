"""
License Plate Color Classification Module

This module analyzes the color of detected license plates to classify them
into types (Personal, Commercial, or Government) based on Nigerian standards.
"""

import cv2
import numpy as np


def get_plate_color(plate_image):
    """
    Determine the dominant color of a license plate using HSV color space.
    
    Args:
        plate_image: Image of the license plate
    
    Returns:
        str: Color name (Yellow, White, Red, Green, Blue, etc.)
    """
    # Convert BGR to HSV
    hsv = cv2.cvtColor(plate_image, cv2.COLOR_BGR2HSV)
    
    # Calculate histogram for all 3 channels
    h, s, v = cv2.split(hsv)
    
    # Get dominant values
    h_mode = np.argmax(np.bincount(h.flatten()))
    s_mode = np.argmax(np.bincount(s.flatten()))
    v_mode = np.argmax(np.bincount(v.flatten()))
    
    # Classify color based on HSV values
    # H: 0-180 (hue), S: 0-255 (saturation), V: 0-255 (value)
    
    # Yellow: H 15-35, high S, high V
    if 15 <= h_mode <= 35 and s_mode > 100 and v_mode > 100:
        return "Yellow"
    
    # White/Light: Low saturation, very high value
    if s_mode < 50 and v_mode > 150:
        return "White"
    
    # Red: H 0-10 or 170-180, high S, high V
    if (0 <= h_mode <= 10 or 170 <= h_mode <= 180) and s_mode > 100 and v_mode > 100:
        return "Red"
    
    # Green: H 35-85, high S, high V
    if 35 <= h_mode <= 85 and s_mode > 100 and v_mode > 100:
        return "Green"
    
    # Blue: H 100-130, high S, high V
    if 100 <= h_mode <= 130 and s_mode > 100 and v_mode > 100:
        return "Blue"
    
    # Black: Low V
    if v_mode < 50:
        return "Black"
    
    return "Unknown"


def classify_plate_type(color):
    """
    Classify license plate type based on color using Nigerian standards.
    
    Nigerian Standards:
    - Private/Personal: Yellow background with black text
    - Commercial: Yellow background with black text (similar to private)
    - Government: Red background with white text
    - Bus/Commercial: Green background with white text
    
    Args:
        color: Plate color string
    
    Returns:
        str: Plate type (Personal, Commercial, Government, or Unknown)
    """
    color_to_type = {
        'Yellow': 'Personal/Commercial',
        'Red': 'Government',
        'Green': 'Commercial/Bus',
        'White': 'Personal',
        'Blue': 'Government',
        'Black': 'Unknown'
    }
    
    return color_to_type.get(color, 'Unknown')


def analyze_plate_background(plate_image):
    """
    Analyze the plate background in more detail.
    
    Args:
        plate_image: Image of the license plate
    
    Returns:
        dict: Background analysis results
    """
    hsv = cv2.cvtColor(plate_image, cv2.COLOR_BGR2HSV)
    
    # Create masks for different colors
    masks = {
        'yellow': cv2.inRange(hsv, np.array([15, 100, 100]), np.array([35, 255, 255])),
        'white': cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 50, 255])),
        'red': cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255])),
        'green': cv2.inRange(hsv, np.array([35, 100, 100]), np.array([85, 255, 255])),
        'blue': cv2.inRange(hsv, np.array([100, 100, 100]), np.array([130, 255, 255])),
    }
    
    # Count pixels in each color range
    pixel_counts = {color: np.sum(mask) // 255 for color, mask in masks.items()}
    
    # Find dominant color
    dominant_color = max(pixel_counts, key=pixel_counts.get)
    
    # Calculate percentages
    total_pixels = plate_image.shape[0] * plate_image.shape[1]
    percentages = {color: (count / total_pixels * 100) for color, count in pixel_counts.items()}
    
    return {
        'dominant_color': dominant_color,
        'percentages': percentages,
        'pixel_counts': pixel_counts
    }


def get_plate_confidence(color):
    """
    Get confidence score for plate type classification.
    
    Args:
        color: Plate color string
    
    Returns:
        float: Confidence score (0.0 - 1.0)
    """
    # High confidence colors for Nigerian plates
    high_confidence = {'Yellow': 0.95, 'Red': 0.90, 'Green': 0.85}
    
    return high_confidence.get(color, 0.5)


def detect_multiple_colors(plate_image):
    """
    Detect multiple colors present in the plate image.
    Useful for multi-color plates or plates with text.
    
    Args:
        plate_image: Image of the license plate
    
    Returns:
        dict: Color distribution information
    """
    hsv = cv2.cvtColor(plate_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Create histograms
    h_hist = cv2.calcHist([h], [0], None, [180], [0, 180])
    s_hist = cv2.calcHist([s], [0], None, [256], [0, 256])
    v_hist = cv2.calcHist([v], [0], None, [256], [0, 256])
    
    # Find peaks (dominant values)
    h_peaks = np.argsort(h_hist.flatten())[-3:][::-1]
    s_peaks = np.argsort(s_hist.flatten())[-3:][::-1]
    v_peaks = np.argsort(v_hist.flatten())[-3:][::-1]
    
    return {
        'hue_peaks': h_peaks.tolist(),
        'saturation_peaks': s_peaks.tolist(),
        'value_peaks': v_peaks.tolist(),
        'hue_histogram': h_hist.flatten().tolist(),
        'saturation_histogram': s_hist.flatten().tolist(),
        'value_histogram': v_hist.flatten().tolist()
    }
