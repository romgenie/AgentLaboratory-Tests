#!/usr/bin/env python3
"""
Adapter script to run Semantic Scholar search tests.

This script runs the Semantic Scholar search tests that use the Semantic Scholar adapter.
"""

import os
import sys
import subprocess

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    """Main function to run Semantic Scholar search tests."""
    # Get the file paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    test_file = os.path.join(project_root, "tests/unit_tests/test_agent_tools/test_semantic_scholar_search.py")
    
    # Check if test file exists
    if not os.path.exists(test_file):
        print(f"Error: Semantic Scholar test file not found: {test_file}")
        return 1
    
    # Check if adapter exists
    adapter_file = os.path.join(project_root, "test_adapters/semantic_scholar_adapter.py")
    if not os.path.exists(adapter_file):
        print(f"Error: Semantic Scholar adapter not found: {adapter_file}")
        return 1
    
    try:
        # Run the tests
        print("\n* Running Semantic Scholar search tests *\n")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/test_agent_tools/test_semantic_scholar_search.py", "-v"], 
            cwd=project_root
        )
        
        # Check the result
        if result.returncode == 0:
            print("\n✅ Semantic Scholar search tests passed successfully!\n")
        else:
            print("\n❌ Semantic Scholar search tests failed.\n")
            
        return result.returncode
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())