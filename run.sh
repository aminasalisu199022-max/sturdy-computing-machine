#!/bin/bash
# Quick Start Script for Nigerian ALPR System

echo "🚗 Nigerian Automatic License Plate Recognition System"
echo "======================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please run manually:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""

# Launch Streamlit app
echo "🚀 Starting Nigerian ALPR System..."
echo ""
echo "The application will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run alpr_system/ui/app.py
