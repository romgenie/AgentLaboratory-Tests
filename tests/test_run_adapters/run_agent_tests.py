#!/usr/bin/env python3
"""
Adapter script to run agent tests.

This script runs the agent class tests to verify agent functionality.
"""

import os
import sys
import subprocess

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    """Main function to run agent tests."""
    # Get the file paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    test_file = os.path.join(project_root, "tests/unit_tests/test_agent_classes.py")
    
    # Check if test file exists
    if not os.path.exists(test_file):
        print(f"Error: Test file not found: {test_file}")
        return 1
    
    try:
        # Run the tests
        print("\n* Running agent class tests *\n")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/test_agent_classes.py", "-v"], 
            cwd=project_root
        )
        
        # Check the result
        if result.returncode == 0:
            print("\n✅ Agent class tests passed successfully!\n")
        else:
            print("\n❌ Agent class tests failed.\n")
            
        return result.returncode
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())