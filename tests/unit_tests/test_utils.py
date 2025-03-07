import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.file_utils import (
    ensure_directory_exists,
    write_text_to_file,
    read_text_from_file,
    save_json,
    load_json
)
from utils.text_utils import (
    truncate_text,
    extract_code_blocks,
    remove_markdown_formatting
)
from utils.token_utils import (
    count_tokens,
    truncate_to_token_limit
)


class TestFileUtils:
    """Test suite for file utility functions."""
    
    def test_ensure_directory_exists(self):
        """Test directory creation functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "test_directory")
            
            # Directory should not exist initially
            assert not os.path.exists(test_dir)
            
            # Create directory
            ensure_directory_exists(test_dir)
            
            # Verify directory was created
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
            
            # Function should not raise error when directory already exists
            ensure_directory_exists(test_dir)
    
    def test_write_and_read_text_file(self):
        """Test writing to and reading from text files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_file.txt")
            test_content = "This is test content.\nWith multiple lines."
            
            # Write content to file
            write_text_to_file(test_file, test_content)
            
            # Verify file exists
            assert os.path.exists(test_file)
            
            # Read content from file
            read_content = read_text_from_file(test_file)
            
            # Verify content matches
            assert read_content == test_content
    
    def test_save_and_load_json(self):
        """Test saving and loading JSON data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_data.json")
            test_data = {
                "string": "value",
                "number": 42,
                "list": [1, 2, 3],
                "nested": {"key": "value"}
            }
            
            # Save JSON data
            save_json(test_file, test_data)
            
            # Verify file exists
            assert os.path.exists(test_file)
            
            # Load JSON data
            loaded_data = load_json(test_file)
            
            # Verify data matches
            assert loaded_data == test_data


class TestTextUtils:
    """Test suite for text utility functions."""
    
    def test_truncate_text(self):
        """Test text truncation functionality."""
        test_text = "This is a long piece of text that needs to be truncated."
        
        # Truncate to 10 characters
        truncated = truncate_text(test_text, 10)
        assert len(truncated) <= 13  # 10 chars + "..."
        assert truncated == "This is a..."
        
        # Test when no truncation needed
        assert truncate_text(test_text, 100) == test_text
        
        # Test empty string
        assert truncate_text("", 10) == ""
    
    def test_extract_code_blocks(self):
        """Test extracting code blocks from markdown."""
        markdown_text = """
        # Test Header
        
        Here is some regular text.
        
        ```python
        def test_function():
            return "Hello World"
        ```
        
        More text here.
        
        ```javascript
        function testFunc() {
            return "JS";
        }
        ```
        """
        
        code_blocks = extract_code_blocks(markdown_text)
        
        assert len(code_blocks) == 2
        assert "def test_function():" in code_blocks[0]
        assert "function testFunc()" in code_blocks[1]
    
    def test_remove_markdown_formatting(self):
        """Test removing markdown formatting from text."""
        markdown_text = """
        # Header
        
        **Bold text** and *italic text*.
        
        - List item 1
        - List item 2
        
        [Link text](http://example.com)
        
        ```
        Code block
        ```
        """
        
        plain_text = remove_markdown_formatting(markdown_text)
        
        # Headers are converted to plain text
        assert "# Header" not in plain_text
        assert "Header" in plain_text
        
        # Formatting is removed
        assert "**Bold text**" not in plain_text
        assert "Bold text" in plain_text
        assert "*italic text*" not in plain_text
        assert "italic text" in plain_text
        
        # Lists are preserved as plain text
        assert "List item 1" in plain_text
        assert "List item 2" in plain_text
        
        # Links are simplified
        assert "[Link text](http://example.com)" not in plain_text
        assert "Link text" in plain_text


@patch('utils.token_utils.tiktoken')
class TestTokenUtils:
    """Test suite for token utility functions."""
    
    def test_count_tokens(self, mock_tiktoken):
        """Test token counting functionality."""
        # Setup mock
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding
        
        # Test token counting
        token_count = count_tokens("This is a test text", "gpt-4o")
        
        # Verify result
        assert token_count == 5
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
    
    def test_truncate_to_token_limit(self, mock_tiktoken):
        """Test truncating text to token limit."""
        # Setup mock
        mock_encoding = MagicMock()
        
        # First call - full text (10 tokens)
        # Second call - truncated text (5 tokens)
        mock_encoding.encode.side_effect = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [1, 2, 3, 4, 5]
        ]
        mock_encoding.decode.return_value = "Truncated text"
        mock_tiktoken.encoding_for_model.return_value = mock_encoding
        
        # Test truncation
        result = truncate_to_token_limit("This is a longer text that should be truncated", 5, "gpt-4o")
        
        # Verify result
        assert result == "Truncated text"
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")