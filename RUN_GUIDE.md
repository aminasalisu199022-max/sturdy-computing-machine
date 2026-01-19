# Nigerian ALPR System - Run Guide

## Overview
A clean, professional YOLO-based Automatic License Plate Recognition (ALPR) system designed for recognizing Nigerian license plates.

**System Features:**
- ✅ Streamlit web interface
- ✅ Image and video support
- ✅ Real-time license plate detection
- ✅ Nigerian plate format validation (AAA-123AA)
- ✅ Mock Nigerian vehicle database
- ✅ Clean, undergraduate-level code

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- `streamlit` - Web UI framework
- `opencv-python` - Image/video processing
- `ultralytics` - YOLO detection
- `pytesseract` - OCR text extraction
- `pillow` - Image handling

---

### 2. Run the Application

```bash
streamlit run alpr_system/ui/app.py
```

The app will start at: **http://localhost:8501**

---

## How to Use

### User Interface

1. **Upload File Section (Left)**
   - Click "Select an image or video"
   - Supported formats:
     - Images: JPG, PNG
     - Videos: MP4, AVI, MOV, MKV

2. **Preview Section**
   - Image preview displays immediately after upload
   - Video preview with embedded player

3. **Controls Section (Right)**
   - **🔍 Detect Plate** - Starts the license plate detection
   - **🗑️ Clear** - Resets the UI and clears all results

4. **Results Section**
   - Displays detected image with bounding boxes
   - Shows plate information and vehicle details

---

## Example Test Images

### Plate Found in Database
Upload an image with plate: **KTS-123AB**
- Owner: Lawal Nasiru
- Vehicle: Toyota Corolla
- State: Katsina
- Color: Blue (Private)

### Plate Not in Database
Upload an image with any other Nigerian plate format like **LAG-456CD**
- Shows: "Plate detected but not found in database"

### Invalid Format
Upload an image with incorrect format (not AAA-123AA)
- Shows: "Invalid Nigerian license plate format"

---

## Nigerian License Plate Format

**Valid Format: AAA-123AA**
- 3 uppercase letters (state code)
- 1 hyphen
- 3 digits
- 2 uppercase letters

**Examples:**
- KTS-123AB ✅
- LAG-456CD ✅
- LAG456CD ❌ (missing hyphen)
- lts-123ab ❌ (lowercase)

---

## System Architecture

### File Structure
```
alpr_system/
├── ui/
│   └── app.py                 # Streamlit UI
├── main.py                    # Core ALPR pipeline
├── detector.py                # YOLO plate detection
├── ocr.py                     # Text extraction
├── plate_validation.py        # Format validation
├── vehicle_db.py              # Mock vehicle database
├── plate_color.py             # Plate color classification
├── utils.py                   # Helper functions
└── __init__.py

models/
├── license_plate_detector.pt  # YOLO weights
└── yolov8n.pt                 # YOLOv8 nano model
```

### Core Modules

#### **plate_validation.py**
Validates Nigerian license plate format
```python
is_valid_nigerian_plate("KTS-123AB")  # True
normalize_plate_text("kts 123ab")     # Cleans text
correct_ocr_errors("K75-123AB")       # Fixes OCR mistakes
```

#### **vehicle_db.py**
Mock Nigerian vehicle registry
```python
lookup_vehicle("KTS-123AB")
# Returns: {
#   'owner_name': 'Lawal Nasiru',
#   'vehicle_type': 'Toyota Corolla',
#   'state': 'Katsina',
#   'plate_color': 'Blue',
#   'plate_type': 'Private'
# }
```

#### **main.py**
Main detection pipeline
```python
results = run_alpr("path/to/image.jpg")
# Returns: {
#   'success': True,
#   'message': 'Plate detected: KTS-123AB',
#   'results': [plate_data],
#   'processed_image': image_with_boxes
# }
```

---

## Database Records

The system includes 15+ test vehicle records with Nigerian states:

| Plate | Owner | State | Type | Color |
|-------|-------|-------|------|-------|
| KTS-123AB | Lawal Nasiru | Katsina | Private | Blue |
| LAG-456CD | Adewale Johnson | Lagos | Private | Blue |
| KDU-789EF | Aminu Haruna | Kaduna | Commercial | Red |
| OGU-234GH | Chioma Okonkwo | Ogun | Private | Blue |
| ABA-567IJ | FRSC | Federal | Government | Green |

All records are in [alpr_system/vehicle_db.py](alpr_system/vehicle_db.py)

---

## Output Display Logic

### ✅ Plate Found in Database
```
✅ Plate detected and found in database!

Plate Number: KTS-123AB
Registration Status: Found
Color: Blue
Type: Private

Vehicle Information:
Owner: Lawal Nasiru
State: Katsina
Vehicle: Toyota Corolla
Year: 2021
```

### ⚠️ Plate Detected but Not Found
```
⚠️ Plate detected but not found in database

Plate Number: XXX-000XX
Status: Not registered
Vehicle Type: Unknown
Plate Color: Unknown
```

### ❌ Invalid Format
```
❌ Invalid Nigerian license plate format

Expected format: AAA-123AA (e.g., KTS-123AB)
3 letters - 1 hyphen - 3 digits - 2 letters
```

### ❌ No Plate Detected
```
❌ No license plate detected in the image

Tips: Try uploading a clearer image with a visible license plate
```

---

## Code Quality

The system is designed for **final-year undergraduate projects** with:
- ✅ Simple, readable code
- ✅ Clear function names and documentation
- ✅ Modular architecture
- ✅ No over-engineering
- ✅ Comprehensive comments
- ✅ Error handling

---

## Troubleshooting

### Streamlit not starting
```bash
# Kill any existing streamlit processes
pkill -f streamlit

# Try again
streamlit run alpr_system/ui/app.py
```

### Module import errors
```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Verify Python path is correct
python3 -c "import alpr_system; print('OK')"
```

### No plate detected
- Try uploading a clearer image
- Ensure the license plate is visible and well-lit
- For videos, make sure plates are visible in at least one frame

### OCR errors (wrong text)
- The system automatically corrects common OCR errors (O→0, I→1, etc.)
- If still incorrect, ensure the image is well-lit and high quality

---

## Testing

### Test with Sample Plates
1. **Known Plate (KTS-123AB)**
   - Create a test image with this text
   - System will show registered vehicle info

2. **Unknown Plate (NEW-999XX)**
   - System will show "not found in database" message

3. **Invalid Format (ABC-12345)**
   - System will show "invalid format" error

---

## Performance Notes

- **Image processing**: ~1-2 seconds
- **Video processing**: ~5-10 seconds (depending on duration)
- **GPU support**: Uses CPU by default, GPU acceleration available

---

## System Requirements

- Python 3.8+
- 2GB RAM minimum
- Webcam or image/video files
- Modern browser (Chrome, Firefox, Safari, Edge)

---

## API Reference

### run_alpr(file_path)
Main detection function

**Parameters:**
- `file_path` (str): Path to image or video

**Returns:**
```python
{
    'success': bool,           # Detection succeeded
    'message': str,            # Status message
    'results': list,           # Plate data
    'timestamp': str,          # Detection time
    'processed_image': ndarray # Image with boxes
}
```

### lookup_vehicle(plate_number)
Look up vehicle by plate

**Parameters:**
- `plate_number` (str): License plate (e.g., "KTS-123AB")

**Returns:**
```python
{
    'owner_name': str,
    'vehicle_type': str,
    'state': str,
    'plate_color': str,
    'plate_type': str,
    'year': int
}
# Returns None if not found
```

### validate_and_format_plate(text)
Validate and format plate text

**Parameters:**
- `text` (str): Raw OCR text

**Returns:**
```python
(is_valid: bool, formatted_plate: str or None)
```

---

## License
Educational use only for final-year undergraduate projects.

---

## Support

For issues or questions:
1. Check this guide
2. Review [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
3. Check code comments in relevant modules

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** ✅ Production Ready
