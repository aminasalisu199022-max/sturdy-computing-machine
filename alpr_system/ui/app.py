"""
Nigerian Automatic License Plate Recognition System - Streamlit UI

Clean, professional web interface for ALPR detection.
Users can upload images or videos, detect plates, and retrieve vehicle information.

Run with: streamlit run alpr_system/ui/app.py
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alpr_system.main import run_alpr
from alpr_system.utils import convert_bgr_to_rgb, is_image_file, is_video_file


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Nigerian ALPR System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 12px;
        font-size: 16px;
        border-radius: 6px;
    }
    .plate-number {
        font-family: monospace;
        font-size: 24px;
        font-weight: bold;
        padding: 12px;
        background-color: #f0f0f0;
        border-radius: 4px;
        text-align: center;
    }
    .success-box {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 2px solid #28a745;
        color: #155724;
    }
    .error-box {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        color: #721c24;
    }
    .warning-box {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        color: #856404;
    }
    .info-box {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
        color: #0c5460;
    }
    .vehicle-info {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None

if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

if 'file_type' not in st.session_state:
    st.session_state.file_type = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clear_session():
    """Clear all session state variables to reset the UI."""
    st.session_state.uploaded_file = None
    st.session_state.uploaded_file_name = None
    st.session_state.detection_results = None
    st.session_state.processed_image = None
    st.session_state.file_type = None


def display_plate_found(plate_data):
    """
    Display results when plate is found in database.
    
    Args:
        plate_data: Dictionary containing plate and vehicle information
    """
    st.success("✅ Plate detected and found in database!")
    
    # Create a clean vehicle info display
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Plate Number**")
            st.markdown(f'<div class="plate-number">{plate_data["plate_number"]}</div>', 
                       unsafe_allow_html=True)
            
            st.markdown("**Plate Status**")
            st.info(f"✅ Found in database")
        
        with col2:
            st.markdown("**Plate Details**")
            st.write(f"🎨 **Color:** {plate_data.get('plate_color', 'Unknown')}")
            st.write(f"🏷️ **Type:** {plate_data.get('plate_type', 'Unknown')}")
    
    st.divider()
    
    # Vehicle Information
    st.subheader("🚗 Vehicle Information")
    vehicle_col1, vehicle_col2 = st.columns(2)
    
    with vehicle_col1:
        st.write(f"👤 **Owner:** {plate_data.get('owner_name', 'N/A')}")
        st.write(f"📍 **State:** {plate_data.get('state', 'N/A')}")
    
    with vehicle_col2:
        st.write(f"🚙 **Vehicle:** {plate_data.get('vehicle_type', 'N/A')}")
        st.write(f"🏘️ **Type:** {plate_data.get('plate_type', 'N/A')}")


def display_plate_not_found(plate_number):
    """
    Display results when plate is detected but not found in database.
    
    Args:
        plate_number: The detected plate number
    """
    st.warning("⚠️ Plate detected but not found in database")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Plate Number**")
            st.markdown(f'<div class="plate-number">{plate_number}</div>', 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Status**")
            st.write("🔍 Plate detected but not registered")
            st.write("🏷️ **Vehicle Type:** Unknown")
            st.write("🎨 **Plate Color:** Unknown")


def display_no_plate_detected():
    """Display message when no plate is detected."""
    st.error("❌ No license plate detected in the image")
    st.info("💡 Try uploading a clearer image with a visible license plate")


def display_invalid_plate():
    """Display message for invalid plate format."""
    st.error("❌ Invalid Nigerian license plate format")
    st.info("📋 Valid format: AAA-123AA (e.g., KTS-123AB)")


def display_detection_image(processed_image):
    """Display the processed image with bounding boxes."""
    if processed_image is not None:
        st.subheader("📸 Detected Image")
        processed_rgb = convert_bgr_to_rgb(processed_image)
        st.image(processed_rgb, use_container_width=True)


def display_results(results):
    """Display detection results in a formatted way."""
    if not results['success']:
        # Display error message
        st.warning(f"⚠️ {results['message']}")
        
        # Show processed image if available
        if results['processed_image'] is not None:
            display_detection_image(results['processed_image'])
        return
    
    # Display processed image
    display_detection_image(results.get('processed_image'))


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

# Title and Header
st.title("🚗 Nigerian ALPR System")
st.markdown("Automatic License Plate Recognition")
st.markdown("---")

# Two-column layout
left_col, right_col = st.columns([1, 1], gap="large")

# ============================================================================
# LEFT COLUMN: FILE UPLOAD AND PREVIEW
# ============================================================================

with left_col:
    st.subheader("📁 Upload File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Select an image or video",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov', 'mkv'],
        help="Supported: JPG, PNG images or MP4, AVI videos"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        _, file_ext = os.path.splitext(uploaded_file.name)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name
        
        st.session_state.uploaded_file = temp_path
        st.session_state.uploaded_file_name = uploaded_file.name
        
        # Determine file type
        file_lower = uploaded_file.name.lower()
        if any(file_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            st.session_state.file_type = 'image'
        elif any(file_lower.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            st.session_state.file_type = 'video'
    
    # Display preview
    if st.session_state.uploaded_file and st.session_state.file_type:
        st.subheader("👁️ Preview")
        
        if st.session_state.file_type == 'image':
            image = Image.open(st.session_state.uploaded_file)
            st.image(image, use_container_width=True)
        else:
            video_file = open(st.session_state.uploaded_file, 'rb')
            st.video(video_file)
            video_file.close()


# ============================================================================
# RIGHT COLUMN: CONTROLS AND RESULTS
# ============================================================================

with right_col:
    st.subheader("⚙️ Controls")
    
    # Buttons
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        detect_btn = st.button(
            "🔍 Detect Plate",
            use_container_width=True,
            type="primary"
        )
    
    with button_col2:
        clear_btn = st.button(
            "🗑️ Clear",
            use_container_width=True
        )
    
    # Handle detect button
    if detect_btn:
        if st.session_state.uploaded_file is None:
            st.error("Please upload an image or video first")
        else:
            with st.spinner("🔄 Processing... Please wait..."):
                try:
                    results = run_alpr(st.session_state.uploaded_file)
                    st.session_state.detection_results = results
                    st.session_state.processed_image = results.get('processed_image')
                except Exception as e:
                    st.error(f"Error during detection: {str(e)}")
    
    # Handle clear button
    if clear_btn:
        if st.session_state.uploaded_file and os.path.exists(st.session_state.uploaded_file):
            try:
                os.remove(st.session_state.uploaded_file)
            except:
                pass
        clear_session()
        st.success("✅ Cleared! Ready for new upload")
        st.rerun()


# ============================================================================
# RESULTS SECTION
# ============================================================================

st.markdown("---")

if st.session_state.detection_results:
    st.subheader("📊 Results")
    results = st.session_state.detection_results
    
    # Display processed image
    display_detection_image(results.get('processed_image'))
    
    st.divider()
    
    # Handle different result scenarios
    if results['success'] and results.get('results'):
        # Plate was detected and found
        plate_data = results['results'][0]
        
        if plate_data.get('registered'):
            # Plate found in database
            display_plate_found(plate_data)
        else:
            # Plate detected but not in database
            display_plate_not_found(plate_data.get('plate_number', 'Unknown'))
    
    elif results['success']:
        # Plate detected but no valid results
        display_no_plate_detected()
    
    elif not results['success']:
        # Error cases
        message = results.get('message', 'Unknown error')
        if 'no plate' in message.lower() or 'not detected' in message.lower():
            display_no_plate_detected()
        elif 'invalid' in message.lower():
            display_invalid_plate()
        else:
            st.error(f"❌ {message}")

elif st.session_state.uploaded_file:
    st.info("👆 Click 'Detect Plate' to start recognition")
else:
    st.info("👈 Upload an image or video to begin")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

with st.expander("ℹ️ System Information"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Supported Formats**")
        st.write("📷 Images: JPG, PNG")
        st.write("🎥 Videos: MP4, AVI, MOV")
    
    with col2:
        st.write("**Plate Format**")
        st.write("Example: **KTS-123AB**")
        st.write("3 letters - 3 digits - 2 letters")
    
    with col3:
        st.write("**How It Works**")
        st.write("1️⃣ Upload file")
        st.write("2️⃣ Click Detect")
        st.write("3️⃣ View results")

st.caption("🚗 Nigerian ALPR System | Powered by YOLOv8 & Streamlit | v1.0")
