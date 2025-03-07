#!/usr/bin/env python3
"""
Sets up GitHub Actions workflows for the project.

This script copies the GitHub Actions workflow files to the .github/workflows directory.
"""

import os
import shutil
import sys

def main():
    """Main function to set up GitHub Actions workflows."""
    # Get the directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    
    # Source files
    standard_workflow = os.path.join(current_dir, "github_actions_workflow.yml")
    adapter_workflow = os.path.join(current_dir, "github_actions_adapter_workflow.yml")
    
    # Target directory
    github_dir = os.path.join(project_root, ".github")
    workflows_dir = os.path.join(github_dir, "workflows")
    
    # Create target directories if they don't exist
    os.makedirs(workflows_dir, exist_ok=True)
    
    # Target files
    standard_target = os.path.join(workflows_dir, "tests.yml")
    adapter_target = os.path.join(workflows_dir, "adapter_tests.yml")
    
    # Copy the workflow files
    try:
        shutil.copy2(standard_workflow, standard_target)
        print(f"✅ Copied standard workflow to {standard_target}")
        
        shutil.copy2(adapter_workflow, adapter_target)
        print(f"✅ Copied adapter workflow to {adapter_target}")
        
        print("\nGitHub Actions workflows set up successfully!")
        print("Run the following commands to commit the changes:")
        print("  git add .github/workflows/")
        print("  git commit -m \"Add GitHub Actions workflows for testing\"")
        
        return 0
    except Exception as e:
        print(f"❌ Error setting up GitHub Actions workflows: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())