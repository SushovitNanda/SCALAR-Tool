#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCALAR Launcher Script
Compatible with both 'python' and 'python3' commands on Windows and Linux
"""
import os
import sys
import subprocess
import webbrowser
import time
import signal
import platform
import threading
import socket
import requests
from requests.exceptions import ConnectionError

def get_python_command():
    """Get the appropriate Python command for the current system."""
    # Check if we're running with python3
    if sys.version_info.major == 3:
        # Try to find python3 first, then fall back to python
        if platform.system() == "Windows":
            # On Windows, try 'python' first (which is usually Python 3)
            if is_command_available("python"):
                return "python"
        else:
            # On Unix-like systems, try 'python3' first
            if is_command_available("python3"):
                return "python3"
            elif is_command_available("python"):
                return "python"
    
    # Fallback to the current executable
    return sys.executable

def is_command_available(command):
    """Check if a command is available on the system PATH."""
    if platform.system() == "Windows":
        check_cmd = f"where {command}"
    else:
        check_cmd = f"which {command}"
    
    try:
        subprocess.check_output(check_cmd, shell=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print(f"ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python and try again.")
        sys.exit(1)

def check_requirements():
    """Check if required tools are installed."""
    print("Checking Python version...")
    check_python_version()
    
    # Check for pip
    try:
        import pip
        print("✓ pip is available")
    except ImportError:
        print("ERROR: pip is not available. Please install pip.")
        sys.exit(1)

def setup_environment():
    """Install dependencies if needed."""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)

def is_server_running():
    """Check if the Flask server is running and accepting connections."""
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        return response.status_code == 200
    except (ConnectionError, requests.exceptions.Timeout):
        return False

def open_browser():
    """Open the browser after ensuring the server is running."""
    max_attempts = 30  # Maximum number of attempts to check server
    attempt = 0
    
    print("Waiting for server to start...")
    while attempt < max_attempts:
        if is_server_running():
            print("Server is ready! Opening browser...")
            try:
                webbrowser.open("http://localhost:5000")
            except Exception as e:
                print(f"Warning: Could not open browser automatically: {e}")
                print("Please manually open: http://localhost:5000")
            return
        time.sleep(1)
        attempt += 1
        if attempt % 5 == 0:  # Show progress every 5 attempts
            print(f"Still waiting for server... ({attempt}/{max_attempts})")
    
    print("Warning: Could not connect to server. Please try refreshing your browser.")

def run_application():
    """Run the application."""
    print("\n Starting SCALAR...\n")
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Use the same Python interpreter that's running this script
    python_cmd = get_python_command()
    app_cmd = [python_cmd, "app.py"]
    
    print("\n SCALAR is running!")
    print(" Access the application at: http://localhost:5000")
    print(" Press Ctrl+C to stop the application\n")
    
    try:
        # Execute the Flask app using the same Python interpreter
        subprocess.run(app_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Failed to start Flask application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nShutting down SCALAR...")
        print("Application stopped successfully.")

if __name__ == "__main__":
    print("\n=== SCALAR ===\n")
    check_requirements()
    setup_environment()
    run_application()
