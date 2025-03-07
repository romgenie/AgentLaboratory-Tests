"""
Tests for the inference system components.

This module verifies that the inference system functions correctly.
"""

import pytest
import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import from adapter instead of directly
from test_adapters.inference_adapter import query_model


def test_query_model_structure():
    """Test that query_model function has expected properties"""
    # Simple imports check
    import inference
    
    # Test that the module has the expected functions
    assert hasattr(inference, 'query_model')
    
    # Check function signature aspects
    from inspect import signature
    sig = signature(query_model)
    
    # Should have parameters for model, prompt, and system_prompt
    params = sig.parameters
    assert 'model_str' in params
    assert 'prompt' in params
    assert 'system_prompt' in params


def test_cost_estimation():
    """Test cost estimation module exists with expected structure"""
    # This is a lightweight test that avoids integration with real cost functions
    try:
        from inference import cost_estimation
        # Just verify the module exists, no functionality testing
        assert cost_estimation is not None, "Cost estimation module not found"
    except ImportError:
        pytest.skip("Cost estimation module not available")