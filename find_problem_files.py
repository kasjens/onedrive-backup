#!/usr/bin/env python3

import subprocess
import json
import sys

def find_problematic_path():
    """Find the specific path causing ObjectHandle errors"""
    
    print("Scanning OneDrive for problematic files/folders...")
    print("This may take a few minutes...\n")
    
    # Start with root and progressively go deeper
    paths_to_check = ["onedrive:"]
    problematic_paths = []
    
    while paths_to_check:
        current_path = paths_to_check.pop(0)
        print(f"Checking: {current_path}")
        
        # Try to list this specific path
        cmd = ["rclone", "lsd", current_path, "--max-depth", "1"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if "ObjectHandle is Invalid" in result.stderr or "invalidResourceId" in result.stderr:
                print(f"  ❌ ERROR found at: {current_path}")
                problematic_paths.append(current_path)
                # Don't traverse deeper into problematic paths
                continue
                
            if result.returncode == 0:
                # Parse output to get subdirectories
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # Extract directory name (last column)
                        parts = line.split()
                        if len(parts) >= 4:
                            dir_name = ' '.join(parts[3:])
                            if current_path == "onedrive:":
                                new_path = f"onedrive:{dir_name}"
                            else:
                                new_path = f"{current_path}/{dir_name}"
                            paths_to_check.append(new_path)
                print(f"  ✓ OK")
            else:
                print(f"  ⚠ Warning: Non-zero return code but no ObjectHandle error")
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠ Timeout checking path")
        except Exception as e:
            print(f"  ⚠ Error: {e}")
    
    print("\n" + "="*50)
    if problematic_paths:
        print("PROBLEMATIC PATHS FOUND:")
        for path in problematic_paths:
            print(f"  - {path}")
        print("\nYou can exclude these paths from your backup by adding them to exclude_patterns in config.json")
    else:
        print("No problematic paths found.")
        print("The error might be transient or related to specific file operations.")
    
    return problematic_paths

def test_specific_path(path):
    """Test a specific path for errors"""
    print(f"Testing path: {path}")
    cmd = ["rclone", "lsd", path, "--max-depth", "1", "-vv"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "ObjectHandle is Invalid" in result.stderr or "invalidResourceId" in result.stderr:
        print(f"ERROR: ObjectHandle is Invalid for path: {path}")
        print("\nDetailed error output:")
        print(result.stderr)
        return False
    else:
        print(f"Path is accessible: {path}")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific path provided as argument
        test_specific_path(sys.argv[1])
    else:
        # Scan for problematic paths
        find_problematic_path()