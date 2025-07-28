#!/usr/bin/env python3
import subprocess
import webbrowser
import time
import signal
import sys
import os
from threading import Thread

def kill_port(port):
    """Kill process on port using system commands"""
    try:
        subprocess.run(['lsof', '-ti', f':{port}'], 
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(['kill', '-9', f'$(lsof -ti :{port})'], 
                     shell=True, stderr=subprocess.PIPE)
        print(f"Killed existing process on port {port}")
    except subprocess.CalledProcessError:
        pass  # No process found on port

def main():
    # Configuration
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_FILE = "app.py"
    HOST = "127.0.0.1"
    PORT = 3000
    
    # Change to script directory
    print(f"Changing to directory: {SCRIPT_DIR}")
    os.chdir(SCRIPT_DIR)
    
    # Check if app file exists
    if not os.path.exists(APP_FILE):
        print(f"Error: {APP_FILE} not found in directory {SCRIPT_DIR}")
        sys.exit(1)
    
    # Kill any existing process on the port
    kill_port(PORT)
    time.sleep(1)
    
    print(f"Starting Flask app: {APP_FILE}")
    print("Flask output will be shown below:")
    print("-" * 40)
    
    # Start Flask and show output in real-time
    try:
        flask_process = subprocess.Popen([sys.executable, APP_FILE])
        
        # Wait a moment then open browser
        time.sleep(3)
        url = f"http://{HOST}:{PORT}"
        print(f"\nOpening browser: {url}")
        webbrowser.open(url)
        
        print("Press Ctrl+C to stop the server")
        
        # Wait for the process or user interrupt
        flask_process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        try:
            flask_process.terminate()
            time.sleep(2)
            if flask_process.poll() is None:
                flask_process.kill()
        except:
            pass
        kill_port(PORT)
        print("Server stopped")

if __name__ == "__main__":
    main()