#!/usr/bin/env python3
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

def check_requirements():
    """Check if required tools are installed."""
    requirements = {
        "python3": "Python 3.8 or higher"
    }
    
    missing = []
    for cmd, desc in requirements.items():
        if not is_command_available(cmd):
            missing.append(f"{desc} ({cmd})")
    
    if missing:
        print("ERROR: Missing required tools:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease install these tools before running the analyzer.")
        sys.exit(1)

def setup_environment():
    """Install dependencies if needed."""
    print("Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def is_server_running():
    """Check if the Flask server is running and accepting connections."""
    try:
        response = requests.get("http://localhost:5000")
        return response.status_code == 200
    except ConnectionError:
        return False

def open_browser():
    """Open the browser after ensuring the server is running."""
    max_attempts = 30  # Maximum number of attempts to check server
    attempt = 0
    
    print("Waiting for server to start...")
    while attempt < max_attempts:
        if is_server_running():
            print("Server is ready! Opening browser...")
            webbrowser.open("http://localhost:5000")
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
    
    # Run the Flask application
    app_cmd = "python app.py"
    
    print("\n SCALAR is running!")
    print(" Access the application at: http://localhost:5000")
    print(" Press Ctrl+C to stop the application\n")
    
    try:
        # Execute the Flask app
        subprocess.run(app_cmd, shell=True)
    except KeyboardInterrupt:
        print("\n\nShutting down SCALAR...")
        print("Application stopped successfully.")

if __name__ == "__main__":
    print("\n=== SCALAR ===\n")
    check_requirements()
    setup_environment()
    run_application()
