#!/bin/bash
echo "=== SCALAR Dependency Installer ==="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.8 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Check Python version
echo "Checking Python version..."
$PYTHON_CMD --version

# Check if pip is available
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "ERROR: pip is not available. Please install pip."
    exit 1
fi

echo "Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
    echo ""
    echo "You can now run the application using:"
    echo "./launch_app.sh"
    echo "or"
    echo "$PYTHON_CMD launch_app.py"
else
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again."
    exit 1
fi
