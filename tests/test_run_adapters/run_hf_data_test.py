#!/usr/bin/env python3
"""
Adapter script to run Hugging Face data search tests.

This script runs the HF data search tests that use the HF data adapter.
"""

import os
import sys
import shutil
import subprocess

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    """Main function to run HF data search tests."""
    # Get the file paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    original_file = os.path.join(project_root, "tests/unit_tests/test_agent_tools/test_hf_data_search.py")
    adapter_file = os.path.join(project_root, "tests/unit_tests/test_agent_tools/test_hf_data_search.py.adapter")
    backup_file = os.path.join(project_root, "tests/unit_tests/test_agent_tools/test_hf_data_search.py.original")
    
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
        
        # Run the tests
        print("\n* Running HF data search tests *\n")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/test_agent_tools/test_hf_data_search.py", "-v"], 
            cwd=project_root
        )
        
        # Check the result
        if result.returncode == 0:
            print("\n✅ HF data search tests passed successfully!\n")
        else:
            print("\n❌ HF data search tests failed.\n")
            
        return result.returncode
    
    finally:
        # Restore the original file
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, original_file)
            os.remove(backup_file)
            print(f"Original file restored.")

if __name__ == "__main__":
    sys.exit(main())