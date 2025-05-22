#!/usr/bin/env python3
"""
Simple script to create a folder named "delete later"
"""

import os
import sys

def create_folder():
    """Create a folder named 'delete later' in the current directory"""
    folder_name = "delete later"
    
    try:
        # Create the directory
        os.makedirs(folder_name, exist_ok=True)
        print(f"✓ Folder '{folder_name}' created successfully")
        
        # Verify the folder exists
        if os.path.exists(folder_name) and os.path.isdir(folder_name):
            print(f"✓ Folder '{folder_name}' exists and is accessible")
            return True
        else:
            print(f"✗ Failed to verify folder '{folder_name}' existence")
            return False
            
    except PermissionError:
        print(f"✗ Permission denied: Cannot create folder '{folder_name}'")
        return False
    except OSError as e:
        print(f"✗ OS Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_folder()
    sys.exit(0 if success else 1)
