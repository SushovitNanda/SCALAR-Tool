#!/bin/bash
echo "=== SCALAR Linux Setup ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is not recommended for security reasons."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        echo "Please install Python 3.8 or higher:"
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "  Fedora: sudo dnf install python3 python3-pip"
        exit 1
    else
        PYTHON_CMD="python"
        print_warning "Using 'python' command (ensure it's Python 3.8+)"
    fi
else
    PYTHON_CMD="python3"
    print_status "Python 3 found"
fi

# Check Python version
echo "Checking Python version..."
$PYTHON_CMD --version

# Check if pip is available
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip is not available"
    echo "Please install pip:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

print_status "pip is available"

# Make scripts executable
echo "Making scripts executable..."
chmod +x launch_app.py
chmod +x launch_app.sh
chmod +x install_dependencies.sh
chmod +x make_executable.sh
print_status "Scripts are now executable"

# Install dependencies
echo "Installing Python dependencies..."
if $PYTHON_CMD -m pip install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    echo "You can try installing manually with: $PYTHON_CMD -m pip install -r requirements.txt"
    exit 1
fi

# Create desktop shortcut (optional)
echo ""
read -p "Create desktop shortcut? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_DIR="$HOME/Desktop"
    if [ ! -d "$DESKTOP_DIR" ]; then
        DESKTOP_DIR="$HOME/桌面"  # Chinese
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$HOME/Escritorio"  # Spanish
            if [ ! -d "$DESKTOP_DIR" ]; then
                print_warning "Could not find desktop directory"
            fi
        fi
    fi
    
    if [ -d "$DESKTOP_DIR" ]; then
        SCRIPT_PATH="$(pwd)/launch_app.sh"
        cat > "$DESKTOP_DIR/SCALAR.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SCALAR
Comment=Semantic Clustering and Labeling Based Toolkit
Exec=$SCRIPT_PATH
Icon=terminal
Terminal=true
Categories=Development;Science;
EOF
        chmod +x "$DESKTOP_DIR/SCALAR.desktop"
        print_status "Desktop shortcut created"
    fi
fi

echo ""
print_status "Setup completed successfully!"
echo ""
echo "You can now run SCALAR using any of these methods:"
echo "  1. Double-click the desktop shortcut (if created)"
echo "  2. Run: ./launch_app.sh"
echo "  3. Run: $PYTHON_CMD launch_app.py"
echo "  4. Run: $PYTHON_CMD app.py"
echo ""
echo "The application will be available at: http://localhost:5000"
