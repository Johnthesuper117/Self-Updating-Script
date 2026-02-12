"""
Module: updater.py
Version: 2.0.0
Author: Johnthesuper117
Description: A modular, zip-based auto-updater for complex directory structures.
Usage:
    - CLI: python updater.py --check (or --update)
    - Code: from updater import AutoUpdater
"""

import os
import sys
import json
import shutil
import logging
import requests
import zipfile
import io
import argparse

# --- CONFIGURATION DEFAULTS ---
# Replace these with your actual repo details or pass them into the class
DEFAULT_OWNER = "Johnthesuper117"
DEFAULT_REPO = "Self-Updating-Script"
DEFAULT_BRANCH = "main"

# Logging Setup
logging.basicConfig(level=logging.INFO, format='[Updater] %(message)s')
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, owner=DEFAULT_OWNER, repo=DEFAULT_REPO, branch=DEFAULT_BRANCH, target_dir="."):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.target_dir = os.path.abspath(target_dir)
        
        # GitHub URLs
        self.version_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/version.json"
        self.zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        
        # Local version file path
        self.local_version_file = os.path.join(self.target_dir, "version.json")

    def get_local_version(self):
        """Reads the local version.json file."""
        if not os.path.exists(self.local_version_file):
            logger.warning("Local version.json not found. Assuming version 0.0.0")
            return "0.0.0"
        
        try:
            with open(self.local_version_file, 'r') as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
        except Exception as e:
            logger.error(f"Error reading local version: {e}")
            return "0.0.0"

    def get_remote_version(self):
        """Fetches the remote version.json from GitHub."""
        try:
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("version")
        except Exception as e:
            logger.error(f"Failed to check remote version: {e}")
            return None

    def check_for_updates(self):
        """
        Compares local and remote versions.
        Returns: (bool, str, str) -> (update_available, local_ver, remote_ver)
        """
        local_ver = self.get_local_version()
        remote_ver = self.get_remote_version()

        if remote_ver and remote_ver != local_ver:
            # Simple string compare. For semver, use 'packaging.version'
            if remote_ver > local_ver:
                logger.info(f"Update Available: {local_ver} -> {remote_ver}")
                return True, local_ver, remote_ver
        
        logger.info(f"System up to date ({local_ver}).")
        return False, local_ver, remote_ver

    def do_update(self):
        """
        Downloads the repo zip, extracts it, and overwrites local files.
        """
        logger.info(f"Downloading update from {self.zip_url}...")
        
        try:
            # 1. Download Zip
            response = requests.get(self.zip_url, stream=True)
            response.raise_for_status()
            
            # 2. Extract in Memory
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # GitHub zips usually have a root folder like 'Repo-main/'
                # We need to strip that root folder to update the current dir correctly.
                root_folder = z.namelist()[0].split('/')[0]
                
                logger.info(f"Extracting files (Root: {root_folder})...")
                
                for member in z.infolist():
                    # Skip directories, we only care about files
                    if member.is_dir():
                        continue
                    
                    # Remove the root folder name from the path
                    # e.g., 'Repo-main/src/main.py' -> 'src/main.py'
                    rel_path = str(member.filename).split('/', 1)[1]
                    
                    if not rel_path: 
                        continue # Skip the root folder itself

                    target_path = os.path.join(self.target_dir, rel_path)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Write file
                    with open(target_path, 'wb') as f:
                        f.write(z.read(member))
                        
            logger.info("Files updated successfully.")
            logger.info("Update complete. Please restart the application.")
            return True

        except Exception as e:
            logger.error(f"Critical Update Error: {e}")
            return False

# --- CLI & FUNCTIONAL ENTRY POINTS ---

def update_now():
    """Helper function to run the update immediately."""
    updater = AutoUpdater()
    available, _, _ = updater.check_for_updates()
    if available:
        updater.do_update()

def restart_program():
    """
    Restarts the current program.
    Note: This will not work if the script is running in an IDE console 
    (like PyCharm or VS Code internal terminal). It works best in a 
    standard Command Prompt or Bash terminal.
    """
    print("Restarting application...")
    
    # Get the current Python interpreter executable (e.g., /usr/bin/python3 or python.exe)
    python = sys.executable
    
    # Get the arguments passed to the script (e.g., main.py --verbose)
    args = sys.argv
    
    # Re-execute the program with the same arguments
    # os.execv replaces the process, so no code after this line runs.
    os.execv(python, [python] + args)

def check_only():
    """Helper function to just check."""
    updater = AutoUpdater()
    updater.check_for_updates()

if __name__ == "__main__":
    # Command Line Interface
    parser = argparse.ArgumentParser(description="Auto-Update Module")
    parser.add_argument('--check', action='store_true', help="Check for updates without installing.")
    parser.add_argument('--update', action='store_true', help="Check and apply updates if available.")
    parser.add_argument('--force', action='store_true', help="Force re-download regardless of version.")
    parser.add_argument('--restart', action='store_true', help="Restart the application after update.")
    
    args = parser.parse_args()
    
    updater = AutoUpdater()
    
    if args.force:
        logger.info("Forcing update...")
        updater.do_update()
        restart_program()
    elif args.update:
        available, _, _ = updater.check_for_updates()
        if available:
            updater.do_update()
            restart_program()
    else:
        # Default behavior if run directly: Just check
        updater.check_for_updates()