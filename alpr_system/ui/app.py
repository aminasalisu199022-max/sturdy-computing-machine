"""
Nigerian Automatic License Plate Recognition System - Streamlit UI

Simple, clean web interface for ALPR detection using Streamlit.
Users can upload images or videos, trigger detection manually, and view results.

Run with: streamlit run app.py
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

from alpr_system.main import run_alpr, get_result_summary
from alpr_system.detector import draw_bounding_box
from alpr_system.utils import convert_bgr_to_rgb, load_image_from_bytes, is_image_file, is_video_file


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Nigerian ALPR System",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
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


def display_results(results):
    """Display detection results in a formatted way."""
    if not results['success']:
        # Display error message with warning box
        st.warning(f"⚠️ {results['message']}")
        
        # Show processed image anyway if available
        if results['processed_image'] is not None:
            st.subheader("📸 Processed Image")
            processed_rgb = convert_bgr_to_rgb(results['processed_image'])
            st.image(processed_rgb, use_column_width=True)
        return
    
    # Display success message
    st.success(f"✅ {results['message']}")
    
    # Display processed image with bounding boxes
    if results['processed_image'] is not None:
        st.subheader("📸 Detected Image")
        processed_rgb = convert_bgr_to_rgb(results['processed_image'])
        st.image(processed_rgb, use_column_width=True)
    
    # Display detection details for each plate
    if results['results']:
        st.subheader("📋 Detection Results")
        
        for i, plate_info in enumerate(results['results'], 1):
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Plate #{i}**")
                    st.metric("Plate Number", plate_info['plate_number'])
                    st.metric("Plate Type", plate_info['plate_type'])
                    st.metric("Plate Color", plate_info['plate_color'])
                
                with col2:
                    st.write(f"**Vehicle Information**")
                    st.metric("Owner", plate_info.get('owner_name', 'N/A'))
                    st.metric("Registration State", plate_info.get('state', 'N/A'))
                    st.metric("Registered", "✓ Yes" if plate_info.get('registered') else "✗ No")
                
                # Additional details
                st.write("**Additional Details**")
                details_cols = st.columns(3)
                with details_cols[0]:
                    st.write(f"**Vehicle Type:** {plate_info.get('vehicle_type', 'N/A')}")
                with details_cols[1]:
                    st.write(f"**Vehicle Color:** {plate_info.get('vehicle_color', 'N/A')}")
                with details_cols[2]:
                    st.write(f"**Year:** {plate_info.get('year', 'N/A')}")
                
                st.write(f"**Detection Time:** {plate_info['timestamp']}")
                st.divider()


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

# Title and Header
st.title("🚗 Nigerian Automatic License Plate Recognition System")
st.markdown("---")
st.write("Upload an image or video to detect license plates and retrieve vehicle information.")

# Create two-column layout for better organization
left_column, right_column = st.columns([1, 1])

# ============================================================================
# LEFT COLUMN: FILE UPLOAD AND PREVIEW
# ============================================================================

with left_column:
    st.subheader("📁 File Upload")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "Choose an image or video",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov', 'mkv'],
        help="Supported formats: JPG, PNG for images; MP4, AVI for videos"
    )
    
    # Handle file upload
    if uploaded_file is not None:
        # Get file extension to preserve it in temp file
        _, file_ext = os.path.splitext(uploaded_file.name)
        
        # Save file temporarily with proper extension and update session state
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = tmp_file.name
        
        st.session_state.uploaded_file = temp_path
        st.session_state.uploaded_file_name = uploaded_file.name
        
        # Determine file type with better detection
        file_name_lower = uploaded_file.name.lower()
        
        # Check image extensions
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm')
        
        if any(file_name_lower.endswith(ext) for ext in image_extensions):
            st.session_state.file_type = 'image'
        elif any(file_name_lower.endswith(ext) for ext in video_extensions):
            st.session_state.file_type = 'video'
        else:
            # Fallback: try using the is_image_file and is_video_file functions
            if is_image_file(uploaded_file.name):
                st.session_state.file_type = 'image'
            elif is_video_file(uploaded_file.name):
                st.session_state.file_type = 'video'
            else:
                st.error(f"❌ Unsupported file type: {uploaded_file.name}. Please upload a JPG, PNG image or MP4, AVI video.")
    
    # Display preview if file is uploaded
    if st.session_state.uploaded_file and st.session_state.file_type:
        st.subheader("👁️ Preview")
        
        if st.session_state.file_type == 'image':
            # Display image preview
            image = Image.open(st.session_state.uploaded_file)
            st.image(image, use_column_width=True, caption="Uploaded Image")
        
        elif st.session_state.file_type == 'video':
            # Display video player
            video_file = open(st.session_state.uploaded_file, 'rb')
            st.video(video_file)
            video_file.close()


# ============================================================================
# RIGHT COLUMN: CONTROL BUTTONS AND RESULTS
# ============================================================================

with right_column:
    st.subheader("⚙️ Controls")
    
    # Create button columns
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        detect_button = st.button(
            "🔍 Detect Plate",
            help="Click to run license plate detection",
            use_container_width=True
        )
    
    with button_col2:
        clear_button = st.button(
            "🗑️ Clear",
            help="Clear uploaded file and results",
            use_container_width=True
        )
    
    # Handle detect button
    if detect_button:
        if st.session_state.uploaded_file is None:
            st.error("⚠️ Please upload an image or video first!")
        else:
            with st.spinner("🔄 Processing... This may take a moment..."):
                try:
                    # Run ALPR detection
                    results = run_alpr(st.session_state.uploaded_file)
                    st.session_state.detection_results = results
                    st.session_state.processed_image = results.get('processed_image')
                except Exception as e:
                    st.error(f"❌ Error during detection: {str(e)}")
    
    # Handle clear button
    if clear_button:
        # Clean up temporary file
        if st.session_state.uploaded_file and os.path.exists(st.session_state.uploaded_file):
            try:
                os.remove(st.session_state.uploaded_file)
            except:
                pass
        
        clear_session()
        st.success("✅ Cleared! Ready for new upload.")
        st.rerun()


# ============================================================================
# RESULTS SECTION
# ============================================================================

st.markdown("---")

if st.session_state.detection_results:
    st.subheader("📊 Detection Results")
    display_results(st.session_state.detection_results)
elif st.session_state.uploaded_file and st.session_state.file_type:
    st.info("ℹ️ Click 'Detect Plate' to start detection")
else:
    st.info("ℹ️ Upload an image or video to begin")


# ============================================================================
# FOOTER AND INFORMATION
# ============================================================================

st.markdown("---")

# Information section
with st.expander("ℹ️ System Information"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Supported Formats**")
        st.write("• Images: JPG, PNG")
        st.write("• Videos: MP4, AVI")
    
    with col2:
        st.write("**How It Works**")
        st.write("1. Upload image/video")
        st.write("2. Click 'Detect Plate'")
        st.write("3. View results")
    
    with col3:
        st.write("**Features**")
        st.write("• License plate detection")
        st.write("• OCR text extraction")
        st.write("• Database lookup")
        st.write("• Vehicle info retrieval")

st.caption("🚗 Nigerian ALPR System | Powered by OpenCV & Streamlit | v1.0")
