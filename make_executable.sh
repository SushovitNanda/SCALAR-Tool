#!/bin/bash
echo "=== SCALAR ==="
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Make the app.py file executable
chmod +x app.py

echo "The application is now executable."
echo "You can start it with:"
echo "./app.py"
echo ""
echo "Or with Python directly:"
echo "python3 app.py"
echo ""
echo "Once running, open your browser to: http://localhost:5000"
