#!/bin/bash
echo "=== Making SCALAR Scripts Executable ==="
echo ""

# Make all shell scripts executable
chmod +x *.sh

# Make Python scripts executable
chmod +x *.py

echo "✓ All scripts are now executable"
echo ""
echo "You can now run:"
echo "  ./setup_linux.sh     - First-time setup"
echo "  ./launch_app.sh      - Launch the application"
echo "  ./install_dependencies.sh - Install dependencies only"
echo ""
echo "Or run Python scripts directly:"
echo "  python3 launch_app.py"
echo "  python3 app.py"
echo "  python3 main.py"
