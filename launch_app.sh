#!/bin/bash
echo "=== SCALAR ==="
echo ""
echo "Starting SCALAR..."

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

# Make the script executable
chmod +x launch_app.py

# Run the Python script which handles everything else
$PYTHON_CMD launch_app.py

# If the script exits with an error, show the error message
if [ $? -ne 0 ]; then
    echo "Application exited with an error. Check the output above for details."
    read -p "Press Enter to continue..."
fi
