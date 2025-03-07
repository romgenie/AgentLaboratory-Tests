#!/usr/bin/env python3
"""
Adapter script to run inference system tests.

This script runs the inference system tests and query model tests using
the inference adapter.
"""

import os
import sys
import shutil
import subprocess

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    """Main function to run inference system tests."""
    # Get the project root and file paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    original_file = os.path.join(project_root, "tests/unit_tests/test_inference/test_query_model.py")
    adapter_file = os.path.join(project_root, "tests/unit_tests/test_inference/test_query_model.py.adapter")
    backup_file = os.path.join(project_root, "tests/unit_tests/test_inference/test_query_model.py.original")
    
    # Check if adapter file exists
    if not os.path.exists(adapter_file):
        print(f"Error: Adapter file not found: {adapter_file}")
        return 1
    
    # Backup the original file if it exists
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"Original file backed up to: {backup_file}")
    
    try:
        # Copy the adapter file to the test location
        shutil.copy2(adapter_file, original_file)
        print(f"Adapter file copied to: {original_file}")
        
        # Run the inference system tests
        print("\n* Running inference system tests *\n")
        
        # First run the main inference system test
        result1 = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/test_inference_system.py", "-v"], 
            cwd=project_root
        )
        
        # Then run the enhanced query model tests
        print("\n* Running enhanced query model tests *\n")
        result2 = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/test_inference/test_query_model.py", "-v"], 
            cwd=project_root
        )
        
        # Determine overall success
        if result1.returncode == 0 and result2.returncode == 0:
            print("\n✅ All inference tests passed successfully!\n")
            return 0
        else:
            print("\n❌ Some inference tests failed.\n")
            return 1
            
    finally:
        # Restore the original file
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, original_file)
            os.remove(backup_file)
            print(f"Original file restored.")

if __name__ == "__main__":
    sys.exit(main())