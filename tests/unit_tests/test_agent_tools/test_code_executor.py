import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from agents_tools.code_executor import execute_code

class TestCodeExecutor:
    """Test suite for code execution functionality."""
    
    def test_execute_code_returns_dict(self):
        """Test that execute_code returns a dictionary with expected keys."""
        code = "print('Hello, world!')"
        result = execute_code(code)
        
        assert isinstance(result, dict)
        assert 'output' in result
        assert 'error' in result
        assert 'figures' in result
    
    def test_execute_code_with_timeout(self):
        """Test that execute_code accepts a timeout parameter."""
        code = "import time; time.sleep(0.1); print('Done')"
        result = execute_code(code, timeout=1)
        
        assert isinstance(result, dict)
        assert 'output' in result
    
    def test_execute_code_result_structure(self):
        """Test that execute_code results have the expected structure."""
        code = "print('Test')"
        result = execute_code(code)
        
        assert isinstance(result['output'], str)
        assert result['error'] is None or isinstance(result['error'], str)
        assert isinstance(result['figures'], list)
        
        for figure in result['figures']:
            assert isinstance(figure, str)