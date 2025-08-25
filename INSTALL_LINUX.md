# SCALAR Ubuntu/Debian Manual Installation Guide

This guide provides manual installation and usage instructions for SCALAR on Ubuntu and Debian systems only.

## Supported Distributions

- Ubuntu 18.04+
- Debian 10+

## Prerequisites

### 1. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python 3.8+

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Verify Python Installation

```bash
python3 --version
pip3 --version
```

Ensure Python version is 3.8 or higher.

## Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SushovitNanda/sclara.git
   cd sclara
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Make scripts executable:
   ```bash
   chmod +x launch_app.py
   chmod +x launch_app.sh
   chmod +x install_dependencies.sh
   ```

## Running the Application

### Option 1: Using the Launch Script
```bash
./launch_app.sh
```

### Option 2: Using Python Directly
```bash
python3 launch_app.py
```

### Option 3: Using the Flask App Directly
```bash
python3 app.py
```

### Option 4: Command Line Interface
```bash
python3 main.py
```

## Troubleshooting

### Permission Issues

If you encounter permission errors:

```bash
# Make all scripts executable
chmod +x *.sh *.py

# Check file permissions
ls -la *.sh *.py
```

### Python Command Issues

If `python3` is not found:

```bash
# Check available Python versions
which python
which python3

# Create a symlink if needed
sudo ln -s /usr/bin/python3 /usr/bin/python
```

### Dependency Issues

If pip installation fails:

```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install with user flag
python3 -m pip install --user -r requirements.txt

# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Browser Issues

If the browser doesn't open automatically:

```bash
# Install a browser
sudo apt install firefox

# Manually open the application
firefox http://localhost:5000
```

### Port Issues

If port 5000 is already in use:

```bash
# Check what's using port 5000
sudo netstat -tulpn | grep :5000

# Kill the process if needed
sudo kill -9 <PID>
```

## System Requirements

- RAM: Minimum 4GB, Recommended 8GB+
- Storage: Minimum 2GB free space
- CPU: Any modern multi-core processor
- Network: Active internet connection for Wikipedia API

## Uninstallation

To remove SCALAR:

```bash
# Remove the application directory
rm -rf /path/to/sclara

# Remove virtual environment (if used)
rm -rf venv
```

## Support

For additional help:

1. Check the main README.md file
2. Review terminal output for error messages
3. Ensure all dependencies are installed correctly
4. Verify Python version compatibility
5. Check firewall and network settings

## Distribution-Specific Notes

### Ubuntu/Debian
- Uses `apt` package manager
- Python 3 is the default Python version
