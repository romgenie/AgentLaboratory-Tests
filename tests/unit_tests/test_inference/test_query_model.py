import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from inference.query_model import query_model

class TestQueryModel:
    """Test suite for query_model functionality."""
    
    def test_query_model_openai(self):
        """Test that query_model handles OpenAI models correctly."""
        result = query_model(
            model_str="gpt-4o",
            prompt="What is the capital of France?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "OpenAI model response to:" in result
    
    def test_query_model_deepseek(self):
        """Test that query_model handles DeepSeek models correctly."""
        result = query_model(
            model_str="deepseek-chat",
            prompt="What is the capital of Germany?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "DeepSeek model response to:" in result
    
    def test_query_model_unknown(self):
        """Test that query_model handles unknown models correctly."""
        result = query_model(
            model_str="custom-model",
            prompt="What is the capital of Italy?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "Unknown model response to:" in result
    
    def test_query_model_parameters(self):
        """Test that query_model accepts all expected parameters."""
        result = query_model(
            model_str="gpt-4o",
            prompt="What is the capital of Spain?",
            system_prompt="You are a helpful assistant.",
            openai_api_key="fake_api_key",
            temp=0.5,
            max_tokens=100
        )
        
        assert isinstance(result, str)