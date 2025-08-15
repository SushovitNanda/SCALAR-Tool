# SCALAR Linux Installation Guide

This guide provides detailed instructions for installing and running SCALAR on Linux systems.

## Supported Linux Distributions

- Ubuntu 18.04+
- Debian 10+
- CentOS 7+
- RHEL 7+
- Fedora 30+
- openSUSE Leap 15+
- Arch Linux

## Prerequisites

### 1. Update System Packages

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
```

**CentOS/RHEL:**
```bash
sudo yum update -y
```

**Fedora:**
```bash
sudo dnf update -y
```

### 2. Install Python 3.8+

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv -y
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip -y
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip -y
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip -y
```

### 3. Verify Python Installation

```bash
python3 --version
pip3 --version
```

Ensure Python version is 3.8 or higher.

## Installation Methods

### Method 1: Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SushovitNanda/sclara.git
   cd sclara
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```

3. **Follow the prompts:**
   - The script will check your system
   - Install dependencies automatically
   - Optionally create a desktop shortcut
   - Provide instructions for running the application

### Method 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SushovitNanda/sclara.git
   cd sclara
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Make scripts executable:**
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
sudo apt install firefox  # Ubuntu/Debian
sudo yum install firefox  # CentOS/RHEL
sudo dnf install firefox  # Fedora

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

- **RAM:** Minimum 4GB, Recommended 8GB+
- **Storage:** Minimum 2GB free space
- **CPU:** Any modern multi-core processor
- **Network:** Active internet connection for Wikipedia API

## Desktop Integration

### Create Desktop Shortcut

The setup script can create a desktop shortcut automatically. If you want to create it manually:

```bash
cat > ~/Desktop/SCALAR.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SCALAR
Comment=Semantic Clustering and Labeling Based Toolkit
Exec=$(pwd)/launch_app.sh
Icon=terminal
Terminal=true
Categories=Development;Science;
EOF

chmod +x ~/Desktop/SCALAR.desktop
```

### Add to Application Menu

```bash
sudo cp ~/Desktop/SCALAR.desktop /usr/share/applications/
```

## Uninstallation

To remove SCALAR:

```bash
# Remove the application directory
rm -rf /path/to/sclara

# Remove desktop shortcut
rm ~/Desktop/SCALAR.desktop

# Remove from application menu
sudo rm /usr/share/applications/SCALAR.desktop

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
- Desktop environment integration works well

### CentOS/RHEL
- Uses `yum` or `dnf` package manager
- May need to enable EPEL repository for additional packages
- SELinux might need configuration for network access

### Fedora
- Uses `dnf` package manager
- Latest Python versions available
- Good desktop integration

### Arch Linux
- Uses `pacman` package manager
- Rolling release with latest packages
- Manual configuration might be required for some dependencies
