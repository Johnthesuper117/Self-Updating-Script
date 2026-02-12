"""
File: main.py
Version: 1.0.1
Author: Johnthesuper117
Description: A self-updating Python script using GitHub as the source of truth.
"""

import os
import sys
import time
import requests # Requires: pip install requests
import json
import logging

# --- CONFIGURATION ---
CURRENT_VERSION = "1.0.1"
REPO_URL = "https://raw.githubusercontent.com/Johnthesuper117/Self-Updating-Script/main/"
VERSION_FILE_URL = REPO_URL + "version.json"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def restart_script():
    """
    Restarts the current script.
    This replaces the current process with a new one using the same arguments.
    """
    logging.info("Respawning process...")
    time.sleep(1)  # Give the OS a moment to release file handles if needed
    
    # sys.executable gives the path to the python interpreter
    # sys.argv gives the list of arguments passed to the script
    os.execv(sys.executable, [sys.executable] + sys.argv)

def check_for_updates():
    """
    Checks the remote GitHub repo for a newer version.
    Returns: None
    """
    logging.info(f"Checking for updates... (Current Version: {CURRENT_VERSION})")
    
    try:
        # 1. Fetch remote version info
        response = requests.get(VERSION_FILE_URL)
        response.raise_for_status()
        remote_data = response.json()
        
        remote_version = remote_data.get("version")
        script_url = remote_data.get("url")

        # 2. Compare Versions (Simple String Comparison)
        # Note: For complex versioning (1.10 > 1.9), use 'packaging.version' library.
        if remote_version > CURRENT_VERSION:
            logging.info(f"Update found! Remote: {remote_version} > Local: {CURRENT_VERSION}")
            perform_update(script_url, remote_version)
        else:
            logging.info("System is up to date.")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error checking updates: {e}")
    except json.JSONDecodeError:
        logging.error("Failed to parse version info from remote.")

def perform_update(url, version):
    """
    Downloads the new script, overwrites the current file, and restarts.
    """
    logging.info(f"Downloading version {version} from {url}...")
    
    try:
        # 1. Download the new code
        response = requests.get(url)
        response.raise_for_status()
        new_code = response.text
        
        # 2. Integrity Check (Basic)
        # Ensure we didn't download an empty file or a 404 error page
        if "def " not in new_code and "import " not in new_code:
            logging.error("Downloaded file does not look like Python code. Aborting.")
            return

        # 3. Overwrite the current file
        # __file__ is the path to the current running script
        current_file_path = os.path.abspath(__file__)
        
        with open(current_file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
            
        logging.info("File overwritten successfully.")
        
        # 4. Restart to apply changes
        restart_script()
        
    except Exception as e:
        logging.error(f"Update failed: {e}")

def main_application_logic():
    """
    Your actual application logic goes here.
    """
    print(f"\n--- Running Core Logic (v{CURRENT_VERSION}) ---")
    print("Doing work... [Processing Data]")
    print("Doing work... [Calculating Matrix]")
    time.sleep(2)
    print("Cycle complete.\n")

if __name__ == "__main__":
    # 1. Check for updates immediately on startup
    check_for_updates()
    
    # 2. Run the main application
    while True:
        main_application_logic()
        
        # Optional: Check for updates periodically in the loop
        # check_for_updates() 
        time.sleep(5)