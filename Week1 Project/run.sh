#!/bin/bash
# Setup and run script for Body Composition Dashboard

echo "🚀 Body Composition Dashboard Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check if Uv is installed, if not install it
if ! command -v uv &> /dev/null; then
    echo "📦 Installing Uv package manager..."
    python3 -m pip install --quiet uv
    if [ $? -eq 0 ]; then
        echo "✓ Uv installed successfully"
    else
        echo "❌ Failed to install Uv. Falling back to pip."
        use_pip=true
    fi
else
    echo "✓ Uv is already installed"
fi

echo ""
echo "📥 Installing dependencies..."

if [ "$use_pip" = true ]; then
    echo "Using pip..."
    python3 -m pip install -r requirements.txt
else
    echo "Using Uv..."
    uv sync
fi

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎬 Starting Streamlit app..."
echo "The app will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

if [ "$use_pip" = true ]; then
    python3 -m streamlit run app.py
else
    uv run streamlit run app.py
fi
