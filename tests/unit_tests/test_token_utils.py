import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.token_utils import count_tokens, truncate_to_token_limit


@patch('utils.token_utils.tiktoken')
class TestTokenUtils:
    """Test suite for token utility functions."""
    
    def setup_tiktoken_mock(self, mock_tiktoken, token_counts=None):
        """Helper to set up the tiktoken mock with appropriate behavior."""
        # Create a mock encoding
        mock_encoding = MagicMock()
        
        # Reset any previous configurations
        mock_encoding.reset_mock()
        
        # Configure the encode method
        if isinstance(token_counts, list):
            mock_encoding.encode.side_effect = token_counts
        else:
            # Default behavior is to return fixed token arrays based on the test case
            mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens by default
            
        # Configure the decode method to return a substring of the input
        mock_encoding.decode.return_value = "Truncated text"
        
        # Configure tiktoken to return our mock encoding
        mock_tiktoken.encoding_for_model.return_value = mock_encoding
        
        return mock_encoding
    
    def test_count_tokens_with_short_text(self, mock_tiktoken):
        """Test counting tokens with short text."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        
        # Execute
        token_count = count_tokens("This is a short test text", "gpt-4o")
        
        # Verify
        assert token_count == 5
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        mock_encoding.encode.assert_called_with("This is a short test text")
    
    def test_count_tokens_with_long_text(self, mock_tiktoken):
        """Test counting tokens with long text."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        # Set up a long token array
        long_tokens = list(range(1000))
        mock_encoding.encode.return_value = long_tokens
        
        # Execute
        long_text = "Long text " * 100
        token_count = count_tokens(long_text, "gpt-4o")
        
        # Verify
        assert token_count == 1000
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        mock_encoding.encode.assert_called_with(long_text)
    
    def test_count_tokens_with_special_characters(self, mock_tiktoken):
        """Test counting tokens with text containing special characters."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        # Special characters might use more tokens
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 tokens
        
        # Execute
        special_text = "Text with special chars: 😊 🔥 ⚡ 🎉"
        token_count = count_tokens(special_text, "gpt-4o")
        
        # Verify
        assert token_count == 8
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        mock_encoding.encode.assert_called_with(special_text)
    
    def test_count_tokens_with_code(self, mock_tiktoken):
        """Test counting tokens with code blocks."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        # Code might use different tokenization
        mock_encoding.encode.return_value = [i for i in range(20)]  # 20 tokens
        
        # Execute
        code_text = """```python
def hello_world():
    print("Hello, world!")
```"""
        token_count = count_tokens(code_text, "gpt-4o")
        
        # Verify
        assert token_count == 20
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        mock_encoding.encode.assert_called_with(code_text)
    
    def test_count_tokens_with_different_models(self, mock_tiktoken):
        """Test counting tokens with different models."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        
        # Execute with different models
        models = ["gpt-4o", "gpt-4o-mini", "claude-3-7-sonnet-20250219"]
        for model in models:
            token_count = count_tokens("Test text", model)
            
            # Verify
            assert token_count == 5
            mock_tiktoken.encoding_for_model.assert_called_with(model)
    
    def test_truncate_to_token_limit_no_truncation_needed(self, mock_tiktoken):
        """Test truncating text when no truncation is needed."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        
        # Execute
        text = "This is a short test text"
        result = truncate_to_token_limit(text, 10, "gpt-4o")
        
        # Verify
        assert result == text  # No truncation should happen
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        mock_encoding.encode.assert_called_once_with(text)
    
    def test_truncate_to_token_limit_truncation_needed(self, mock_tiktoken):
        """Test truncating text when truncation is needed."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        
        # Test with text that needs truncation
        # Just make the encode return a long list once
        original_tokens = list(range(20))  # 20 tokens
        mock_encoding.encode.return_value = original_tokens
        mock_encoding.decode.return_value = "Truncated test text"
        
        # Execute
        text = "This is a longer test text that should be truncated to fit within the token limit."
        result = truncate_to_token_limit(text, 10, "gpt-4o")
        
        # Verify
        assert result == "Truncated test text"
        mock_encoding.encode.assert_called_with(text)
        mock_encoding.decode.assert_called_once()
    
    def test_truncate_to_token_limit_edge_cases(self, mock_tiktoken):
        """Test truncating text with edge cases like empty text or zero limit."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        
        # Test with empty string
        result = truncate_to_token_limit("", 10, "gpt-4o")
        assert result == ""
        
        # Test with zero token limit
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        result = truncate_to_token_limit("Some text", 0, "gpt-4o")
        assert result == ""  # Should return empty string for 0 token limit
    
    def test_truncate_to_token_limit_different_models(self, mock_tiktoken):
        """Test truncating text with different models."""
        # Setup
        mock_encoding = self.setup_tiktoken_mock(mock_tiktoken)
        
        # Original text has 20 tokens, truncate to 10
        original_tokens = list(range(20))
        truncated_tokens = original_tokens[:10]
        mock_encoding.encode.side_effect = [original_tokens, truncated_tokens]
        mock_encoding.decode.return_value = "Truncated text"
        
        # Execute with different model
        text = "This is text that should be truncated."
        result = truncate_to_token_limit(text, 10, "gpt-4o-mini")
        
        # Verify
        assert result == "Truncated text"
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o-mini")