import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.token_utils import get_token_count, truncate_to_token_limit
from inference.query_model import query_model

@pytest.mark.performance
class TestTokenOptimization:
    """Performance tests for token optimization and usage."""
    
    @pytest.fixture
    def sample_long_text(self):
        """Fixture to create a sample long text for testing."""
        # Generate a text with approximately 2000 tokens
        return " ".join(["word" for _ in range(10000)])
    
    @pytest.fixture
    def sample_prompts(self):
        """Fixture to create sample prompts of different lengths."""
        return {
            "small": "Summarize the main points of transformers.",
            "medium": " ".join(["word" for _ in range(500)]),
            "large": " ".join(["word" for _ in range(2000)]),
        }
    
    def test_token_count_performance(self, sample_long_text):
        """Test the performance of token counting function."""
        # Measure time for token counting
        start_time = time.time()
        token_count = get_token_count(sample_long_text)
        end_time = time.time()
        
        # Assert reasonable performance (should be very fast)
        assert end_time - start_time < 0.1  # Should be much faster than 100ms
        assert token_count > 1000  # Sanity check that we're counting a large number of tokens
    
    def test_truncation_performance(self, sample_long_text):
        """Test the performance of text truncation function."""
        # Measure time for truncation
        start_time = time.time()
        truncated_text = truncate_to_token_limit(sample_long_text, 1000)
        end_time = time.time()
        
        # Assert reasonable performance
        assert end_time - start_time < 0.1  # Should be much faster than 100ms
        assert get_token_count(truncated_text) <= 1000  # Verify truncation worked correctly
    
    @patch('inference.query_model.query_model')
    def test_token_usage_tracking(self, mock_query_model):
        """Test that token usage is tracked correctly during model queries."""
        # Configure mock
        mock_query_model.return_value = "Model response"
        
        # Set up token tracking
        inference.TOKENS_IN = {}
        inference.TOKENS_OUT = {}
        
        # Make a sample query
        query_model(
            model_str="gpt-4o",
            prompt="This is a test prompt",
            system_prompt="You are a helpful assistant"
        )
        
        # Check that tokens were tracked
        assert "gpt-4o" in inference.TOKENS_IN
        assert "gpt-4o" in inference.TOKENS_OUT
        assert inference.TOKENS_IN["gpt-4o"] > 0
        assert inference.TOKENS_OUT["gpt-4o"] > 0
    
    @patch('inference.query_model.query_model')
    def test_context_window_optimization(self, mock_query_model, sample_prompts):
        """Test optimization strategies for working within context windows."""
        # Configure mock
        mock_query_model.return_value = "Model response"
        
        # Test with different prompt sizes
        for prompt_name, prompt in sample_prompts.items():
            # Calculate token count
            prompt_tokens = get_token_count(prompt)
            
            # Simulate different context window constraints
            context_windows = [4000, 8000, 16000, 32000]
            
            for window in context_windows:
                # Skip tests where prompt is already smaller than window
                if prompt_tokens < window / 2:
                    continue
                    
                # Test optimization strategy
                if prompt_tokens > window - 1000:  # Leave room for response
                    # Truncate to fit
                    optimized_prompt = truncate_to_token_limit(prompt, window - 1000)
                    assert get_token_count(optimized_prompt) <= window - 1000
                    
                    # Measure performance impact
                    start_time = time.time()
                    truncate_to_token_limit(prompt, window - 1000)
                    end_time = time.time()
                    
                    # Optimization should be fast
                    assert end_time - start_time < 0.1  # Should be much faster than 100ms