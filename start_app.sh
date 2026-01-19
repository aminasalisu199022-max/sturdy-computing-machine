#!/bin/bash

# Nigerian ALPR System - Quick Start Script
# This script installs dependencies and runs the application

echo "=================================="
echo "🚗 Nigerian ALPR System"
echo "Quick Start Setup"
echo "=================================="
echo ""

# Check Python version
echo "📌 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -V 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Install dependencies
echo "📌 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Verify installation
echo "📌 Verifying installation..."
python3 -m py_compile alpr_system/plate_validation.py alpr_system/vehicle_db.py alpr_system/main.py

if [ $? -eq 0 ]; then
    echo "✅ All modules verified"
else
    echo "❌ Module verification failed"
    exit 1
fi
echo ""

# Start the application
echo "🚀 Starting Nigerian ALPR System..."
echo ""
echo "   The app will open at: http://localhost:8501"
echo ""
echo "   To stop the server, press: Ctrl+C"
echo ""
echo "=================================="
echo ""

# Run Streamlit
streamlit run alpr_system/ui/app.py
