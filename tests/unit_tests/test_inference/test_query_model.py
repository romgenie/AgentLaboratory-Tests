import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import from test_adapters instead of directly from inference
from test_adapters.inference_adapter import query_model

class TestQueryModel:
    """Test suite for query_model functionality."""
    
    @patch('test_adapters.inference_adapter.original_query_model')
    def test_query_model_openai(self, mock_query):
        """Test that query_model handles OpenAI models correctly."""
        mock_query.return_value = "OpenAI model response to: What is the capital of France?"
        
        result = query_model(
            model_str="gpt-4o",
            prompt="What is the capital of France?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "OpenAI model response to:" in result
    
    @patch('test_adapters.inference_adapter.original_query_model')
    def test_query_model_deepseek(self, mock_query):
        """Test that query_model handles DeepSeek models correctly."""
        mock_query.return_value = "DeepSeek model response to: What is the capital of Germany?"
        
        result = query_model(
            model_str="deepseek-chat",
            prompt="What is the capital of Germany?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "DeepSeek model response to:" in result
    
    @patch('test_adapters.inference_adapter.original_query_model')
    def test_query_model_unknown(self, mock_query):
        """Test that query_model handles unknown models correctly."""
        mock_query.return_value = "Unknown model response to: What is the capital of Italy?"
        
        result = query_model(
            model_str="custom-model",
            prompt="What is the capital of Italy?",
            system_prompt="You are a helpful assistant."
        )
        
        assert isinstance(result, str)
        assert "Unknown model response to:" in result
    
    @patch('test_adapters.inference_adapter.original_query_model')
    def test_query_model_parameters(self, mock_query):
        """Test that query_model accepts all expected parameters."""
        mock_query.return_value = "Test response"
        
        result = query_model(
            model_str="gpt-4o",
            prompt="What is the capital of Spain?",
            system_prompt="You are a helpful assistant.",
            openai_api_key="fake_api_key",
            temp=0.5,
            max_tokens=100
        )
        
        assert isinstance(result, str)