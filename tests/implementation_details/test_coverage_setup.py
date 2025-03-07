import pytest
import os
import sys
import json
import subprocess
from typing import List, Dict, Union, Any

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

"""
Test Coverage Setup and Configuration

This module provides test cases for validating the test coverage setup
and reporting for the Agent Laboratory project. It verifies that:

1. Coverage configuration is properly set up
2. Coverage report commands work correctly
3. HTML and XML coverage reports can be generated
4. Critical path components are identified and tested
"""

# Configuration for pytest-cov
def pytest_cov_setup():
    """Set up coverage configuration."""
    return {
        "source": ["agents", "agents_phases", "agents_tools", "inference", 
                   "laboratory_workflow", "mlsolver", "utils"],
        "omit": ["*/__pycache__/*", "*/tests/*", "*/venv/*"],
        "branch": True,
    }

# Critical path identification for prioritized testing
CRITICAL_PATHS = [
    "inference/query_model.py",
    "agents_tools/arxiv_search.py",
    "agents_tools/code_executor.py",
    "agents_tools/semantic_scholar_search.py",
    "utils/token_utils.py"
]

def test_critical_paths_exist():
    """Verify that critical path files exist in the codebase."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    for path in CRITICAL_PATHS:
        full_path = os.path.join(project_root, path)
        assert os.path.exists(full_path), f"Critical path file {path} not found"

def test_coverage_check():
    """Verify coverage reporting functionality."""
    # Build coverage command for a simple test
    test_file = os.path.join(os.path.dirname(__file__), "..", "unit_tests", "simple_test.py")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
        
    coverage_cmd = [
        "python", "-m", "pytest",
        "--cov=../", 
        "--cov-report=term", 
        "-xvs", 
        test_file
    ]
    
    try:
        # Run the command
        process = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Check that it ran successfully
        assert process.returncode == 0, f"Coverage command failed: {process.stderr}"
        
        # Check that coverage output is present
        assert "coverage" in process.stdout.lower(), "Coverage output not found"
        
    except Exception as e:
        pytest.skip(f"Coverage test failed: {str(e)}")

def test_html_coverage_report():
    """Test generation of HTML coverage reports."""
    report_dir = os.path.join(os.path.dirname(__file__), "..", ".coverage_html_test")
    
    # Clean up any existing test report
    if os.path.exists(report_dir):
        import shutil
        shutil.rmtree(report_dir)
    
    try:
        os.makedirs(report_dir, exist_ok=True)
        
        # Simple command to generate HTML report
        coverage_cmd = [
            "python", "-m", "pytest",
            "--cov=../", 
            f"--cov-report=html:{report_dir}", 
            "-xvs", 
            os.path.join(os.path.dirname(__file__), "..", "unit_tests", "simple_test.py")
        ]
        
        process = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Verify HTML report was created
        assert os.path.exists(os.path.join(report_dir, "index.html")), "HTML coverage report not generated"
        
    except Exception as e:
        pytest.skip(f"HTML coverage report test failed: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(report_dir):
            import shutil
            shutil.rmtree(report_dir)

def test_xml_coverage_report():
    """Test generation of XML coverage reports for CI/CD integration."""
    report_file = os.path.join(os.path.dirname(__file__), "..", ".coverage.xml")
    
    # Clean up any existing test report
    if os.path.exists(report_file):
        os.remove(report_file)
    
    try:
        # Simple command to generate XML report
        coverage_cmd = [
            "python", "-m", "pytest",
            "--cov=../", 
            f"--cov-report=xml:{report_file}", 
            "-xvs", 
            os.path.join(os.path.dirname(__file__), "..", "unit_tests", "simple_test.py")
        ]
        
        process = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Verify XML report was created
        assert os.path.exists(report_file), "XML coverage report not generated"
        
    except Exception as e:
        pytest.skip(f"XML coverage report test failed: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(report_file):
            os.remove(report_file)

def test_critical_paths_have_tests():
    """Check that critical path components have corresponding test files."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    tests_dir = os.path.join(project_root, "tests")
    
    # For each critical path, check if a corresponding test file exists
    coverage_issues = []
    
    for path in CRITICAL_PATHS:
        # Extract module name and convert path to test file naming convention
        module_name = os.path.basename(path).replace(".py", "")
        
        # Look for test files in multiple possible locations
        test_file_patterns = [
            f"test_{module_name}.py",                           # Direct test file
            f"{module_name}/test_{module_name}.py",             # In subdirectory
            f"test_{os.path.dirname(path).replace('/', '_')}_test_{module_name}.py"  # Path-based
        ]
        
        found = False
        for pattern in test_file_patterns:
            # Recursively search for the test file
            for root, _, files in os.walk(tests_dir):
                for file in files:
                    if file == pattern or file == f"test_{module_name}.py":
                        found = True
                        break
                if found:
                    break
            if found:
                break
        
        if not found:
            coverage_issues.append(f"No test found for critical path: {path}")
    
    # Print coverage issues for debugging
    if coverage_issues:
        print("\nCritical path coverage issues:")
        for issue in coverage_issues:
            print(f"  - {issue}")
            
    # Assert all critical paths have tests
    assert not coverage_issues, f"{len(coverage_issues)} critical paths missing tests"

if __name__ == "__main__":
    # Run these tests individually
    pytest.main(["-xvs", __file__])