# 🚗 Nigerian Automatic License Plate Recognition (ALPR) System

A simple, clean, and functional web-based system for detecting Nigerian license plates, extracting text, and retrieving vehicle information.

## 🎯 Features

### User Interface
- **Simple Web Interface**: Built with Streamlit, no complex setup required
- **File Upload**: Support for images (JPG, PNG) and videos (MP4, AVI)
- **Live Preview**: See your uploaded image or play video before detection
- **Manual Trigger**: Click "Detect Plate" to run analysis (not automatic)
- **Clear Button**: Reset UI and start over with a single click
- **Error Handling**: User-friendly error messages for failed detections

### Detection Capabilities
- **License Plate Detection**: Uses OpenCV edge detection and contour analysis
- **Optical Character Recognition (OCR)**: Extracts text from detected plates
- **Format Validation**: Ensures detected text matches Nigerian plate format
- **Color Classification**: Identifies plate types by color analysis
- **Database Lookup**: Retrieves vehicle owner and registration information
- **Bounding Box Visualization**: Shows detected plates with boxes

### Output Information
When a plate is detected, the system displays:
- **Plate Number**: Recognized text from the license plate
- **Plate Type**: Personal, Commercial, or Government
- **Plate Color**: Identified color of the plate
- **Owner Name**: Retrieved from vehicle database (if registered)
- **Registration State**: State where vehicle is registered
- **Vehicle Type**: Type of vehicle (car, truck, bus, etc.)
- **Vehicle Color**: Color of the registered vehicle
- **Registration Year**: Year of vehicle registration
- **Detection Timestamp**: Date and time of detection
- **Registration Status**: Whether vehicle is in database

## 📋 System Requirements

- Python 3.8 or higher
- 200MB disk space for dependencies
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### Option 1: Using the Quick Start Script

```bash
# Linux/Mac
chmod +x run.sh
./run.sh

# Windows (using Git Bash or WSL)
bash run.sh
```

### Option 2: Manual Installation

```bash
# Clone or download the repository
cd sturdy-computing-machine

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run alpr_system/ui/app.py
```

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│         Nigerian ALPR System                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐    ┌──────────────────────────────┐
│  │   FILE UPLOAD       │    │    CONTROLS                  │
│  │                     │    │                              │
│  │ [Upload Image/Video]│    │ [🔍 Detect Plate]           │
│  │                     │    │ [🗑️  Clear]                │
│  └─────────────────────┘    └──────────────────────────────┘
│
│  ┌─────────────────────┐
│  │    PREVIEW          │
│  │                     │
│  │ [Image/Video]       │
│  │                     │
│  └─────────────────────┘
│
├─────────────────────────────────────────────────────────────┤
│                 DETECTION RESULTS                            │
│                                                               │
│  [Processed Image with Bounding Box]                        │
│                                                               │
│  Plate Number:   LA342BCA                                   │
│  Plate Type:     Personal                                   │
│  Owner:          Aminu Adeyemi                              │
│  State:          Lagos                                      │
│  Vehicle:        Private Car                                │
│  Year:           2022                                       │
│  Timestamp:      2026-01-17 14:30:45                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📝 How to Use

### Step 1: Upload a File
1. Click "Choose an image or video"
2. Select a JPG, PNG (image) or MP4, AVI (video) file
3. The preview appears automatically

### Step 2: Trigger Detection
1. Click the **"🔍 Detect Plate"** button
2. Wait for processing (a few seconds)
3. Results appear below if plate is found

### Step 3: View Results
- See the detected image with green bounding box
- View all plate and vehicle information
- Multiple plates in a video are all displayed

### Step 4: Clear and Retry
- Click **"🗑️ Clear"** to reset the UI
- Upload a new file and start over

## 💾 Project Structure

```
sturdy-computing-machine/
├── alpr_system/                    # Main ALPR package
│   ├── __init__.py                # Package initialization
│   ├── detector.py                # Plate detection module
│   ├── ocr.py                     # Text extraction module
│   ├── plate_color.py             # Color classification
│   ├── vehicle_db.py              # Vehicle database
│   ├── utils.py                   # Utility functions
│   ├── main.py                    # Main ALPR pipeline
│   └── ui/
│       └── app.py                 # Streamlit web interface
├── requirements.txt               # Python dependencies
├── run.sh                         # Quick start script
└── README.md                      # This file
```

## 🔧 Core Modules

### `detector.py` - License Plate Detection
- Uses edge detection (Canny algorithm)
- Finds contours matching plate dimensions
- Returns plate region and bounding box

### `ocr.py` - Text Recognition
- Extracts text from plate image
- Validates Nigerian plate format
- Handles errors and invalid formats

### `plate_color.py` - Color Classification
- Analyzes HSV color space
- Classifies plate type by color:
  - Yellow → Personal/Commercial
  - Red → Government
  - Green → Commercial/Bus
  - White → Personal

### `vehicle_db.py` - Vehicle Database
- Pre-loaded with 5 sample vehicles
- Lookup by plate number
- Extensible for real databases

### `utils.py` - Helper Functions
- Image and video processing
- File type validation
- Temporary file management

### `main.py` - Main Pipeline
- Orchestrates entire workflow
- Returns comprehensive results
- Handles errors gracefully

### `ui/app.py` - Streamlit UI
- Clean, user-friendly interface
- Session state management
- Real-time preview and results

## 📊 Sample Detection Results

When detecting plate **LA342BCA**:

```json
{
  "success": true,
  "message": "Successfully detected plate: LA342BCA",
  "results": [{
    "plate_number": "LA342BCA",
    "plate_color": "Yellow",
    "plate_type": "Personal",
    "confidence": 0.95,
    "owner_name": "Aminu Adeyemi",
    "state": "Lagos",
    "vehicle_type": "Private Car",
    "vehicle_color": "Silver",
    "year": 2022,
    "registered": true,
    "timestamp": "2026-01-17 14:30:45"
  }],
  "timestamp": "2026-01-17 14:30:45"
}
```

## ⚠️ Error Handling

The system provides clear error messages for:
- **No plate detected**: "No license plate detected. Please upload a clearer image."
- **OCR failed**: "OCR failed or detected text does not match Nigerian plate format."
- **Invalid file**: "Invalid file type. Please upload an image (.jpg, .png) or video (.mp4, .avi)"
- **File read error**: "Failed to load image. Please check the file."

## 🎓 Academic Suitability

This system is designed as a final-year Computer Science project with:
- ✅ Clear, readable code
- ✅ Comprehensive comments
- ✅ Modular architecture
- ✅ Simple procedural functions
- ✅ No complex frameworks
- ✅ Professional web UI
- ✅ Complete documentation

## 🚀 Running on localhost

Once started with `run.sh` or `streamlit run alpr_system/ui/app.py`:

- Open browser: **http://localhost:8501**
- UI loads immediately
- Ready for file uploads
- No additional setup needed

## 📦 Dependencies

- **streamlit** (1.20+): Web framework
- **opencv-python** (4.8+): Image processing
- **numpy** (1.24+): Numerical operations
- **pillow** (10.0+): Image library

## 📌 Sample Plates in Database

The system includes 5 pre-registered vehicles for testing:

1. **LA342BCA** - Aminu Adeyemi (Lagos)
2. **KD123ABC** - Fatima Mohammed (Kaduna)
3. **AB567XYZ** - FRSC Official (Abuja)
4. **OG789PQR** - Lagos Transport Co (Ogun)
5. **RI456DEF** - Chinedu Okafor (Rivers)

## 🛠️ Customization

### Add More Vehicles
Edit `vehicle_db.py` and add entries to `VEHICLE_DATABASE`:

```python
VEHICLE_DATABASE = {
    'NG123ABC': {
        'owner_name': 'Your Name',
        'state': 'State Code',
        'vehicle_type': 'Vehicle Type',
        'color': 'Color',
        'year': 2024,
        'plate_type': 'Personal'
    },
    ...
}
```

### Adjust Detection Sensitivity
In `detector.py`, modify Canny edge detection thresholds:

```python
edges = cv2.Canny(blurred, 100, 200)  # Lower values = more sensitive
```

## 🐛 Troubleshooting

**Issue**: Streamlit not found
- **Solution**: `pip install streamlit`

**Issue**: OpenCV errors
- **Solution**: `pip install opencv-python`

**Issue**: Port 8501 already in use
- **Solution**: `streamlit run app.py --server.port 8502`

**Issue**: No plates detected
- **Solution**: Ensure image is clear, well-lit, and plate is visible

## 📞 Support & Documentation

- Check README.md for overview
- See DEVELOPER_GUIDE.md for technical details
- Review code comments for implementation details

## ✨ Key Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Image Upload | ✅ | JPG, PNG supported |
| Video Upload | ✅ | MP4, AVI supported |
| Live Preview | ✅ | Displays before detection |
| Manual Detection | ✅ | User-triggered |
| Clear Button | ✅ | Full UI reset |
| Bounding Boxes | ✅ | Green boxes on detections |
| Database Lookup | ✅ | 5 sample vehicles |
| Error Messages | ✅ | User-friendly |
| Responsive UI | ✅ | Streamlit responsive |
| Session State | ✅ | Maintains state between interactions |

## 📄 License

This project is provided for educational purposes.

## 👨‍💻 Development

Developed as a complete ALPR system showcasing:
- Computer Vision techniques
- Image processing pipelines
- Web UI development
- Database integration
- Error handling

---

**Version**: 1.0.0  
**Last Updated**: January 17, 2026  
**Status**: ✅ Production Ready
