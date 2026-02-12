import time
from updater import AutoUpdater

def main():
    print("Initializing Super App...")
    
    # Initialize the updater
    # You can specify the repo here if you don't want to edit updater.py
    updater = AutoUpdater(owner="Johnthesuper117", repo="Self-Updating-Script")
    
    # Check for updates on startup
    update_available, local_v, remote_v = updater.check_for_updates()
    
    if update_available:
        print(f"New version {remote_v} detected!")
        user_choice = input("Update now? (y/n): ")
        if user_choice.lower() == 'y':
            success = updater.do_update()
            if success:
                print("Update finished! Exiting to allow restart.")
                exit() # Exit so the user or a service manager can restart the app
    
    # ... Rest of your application logic ...
    print(f"Running application version {local_v}")

if __name__ == "__main__":
    main()