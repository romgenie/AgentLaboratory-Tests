import pytest
import os
import sys
import re

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.text_utils import (
    truncate_text,
    extract_code_blocks,
    remove_markdown_formatting
)


class TestTextUtils:
    """Test suite for text utility functions."""
    
    def test_truncate_text_no_truncation_needed(self):
        """Test truncate_text when the text is already shorter than max_length."""
        text = "Short text"
        max_length = 20
        
        result = truncate_text(text, max_length)
        
        assert result == text
        assert len(result) < max_length
    
    def test_truncate_text_truncation_needed(self):
        """Test truncate_text when the text needs to be truncated."""
        text = "This is a longer text that needs to be truncated"
        max_length = 10
        
        result = truncate_text(text, max_length)
        
        assert len(result) <= max_length + 3  # +3 for "..."
        assert result.endswith("...")
        assert result.startswith(text[:max_length])
    
    def test_truncate_text_edge_cases(self):
        """Test truncate_text with edge cases like empty string or very short max_length."""
        # Empty string
        assert truncate_text("", 10) == ""
        
        # Very short max_length
        result = truncate_text("Hello world", 3)
        assert result == "Hel..."
        
        # Max length of 0
        result = truncate_text("Hello", 0)
        assert result == "..."
    
    def test_extract_code_blocks_simple(self):
        """Test extract_code_blocks with simple code blocks."""
        markdown = """
        Here is some text.
        
        ```
        def simple_function():
            return "Hello, world!"
        ```
        
        And more text.
        """
        
        code_blocks = extract_code_blocks(markdown)
        
        assert len(code_blocks) == 1
        assert "def simple_function():" in code_blocks[0]
        assert "return \"Hello, world!\"" in code_blocks[0]
    
    def test_extract_code_blocks_with_language(self):
        """Test extract_code_blocks with language-specific code blocks."""
        markdown = """
        Python code:
        
        ```python
        def python_function():
            return "Python"
        ```
        
        JavaScript code:
        
        ```javascript
        function jsFunction() {
            return "JavaScript";
        }
        ```
        """
        
        code_blocks = extract_code_blocks(markdown)
        
        assert len(code_blocks) == 2
        assert "def python_function():" in code_blocks[0]
        assert "function jsFunction()" in code_blocks[1]
    
    def test_extract_code_blocks_no_blocks(self):
        """Test extract_code_blocks with text that has no code blocks."""
        markdown = """
        This is just plain text.
        
        With multiple paragraphs.
        
        But no code blocks.
        """
        
        code_blocks = extract_code_blocks(markdown)
        
        assert len(code_blocks) == 0
    
    def test_extract_code_blocks_nested_backticks(self):
        """Test extract_code_blocks with nested backticks inside code blocks."""
        markdown = """
        ```python
        def function_with_backticks():
            # This has a backtick: `inline code`
            return "Nested backticks"
        ```
        """
        
        code_blocks = extract_code_blocks(markdown)
        
        assert len(code_blocks) == 1
        assert "def function_with_backticks():" in code_blocks[0]
        assert "`inline code`" in code_blocks[0]
    
    def test_remove_markdown_formatting_basic(self):
        """Test remove_markdown_formatting with basic Markdown elements."""
        markdown = """
        # Heading 1
        
        ## Heading 2
        
        This text has **bold** and *italic* formatting.
        
        - List item 1
        - List item 2
        """
        
        plain_text = remove_markdown_formatting(markdown)
        
        # Headers should be converted to plain text
        assert "# Heading 1" not in plain_text
        assert "## Heading 2" not in plain_text
        assert "Heading 1" in plain_text
        assert "Heading 2" in plain_text
        
        # Bold and italic formatting should be removed
        assert "**bold**" not in plain_text
        assert "*italic*" not in plain_text
        assert "bold" in plain_text
        assert "italic" in plain_text
        
        # List items should be preserved
        assert "List item 1" in plain_text
        assert "List item 2" in plain_text
    
    def test_remove_markdown_formatting_links_and_code(self):
        """Test remove_markdown_formatting with links and code blocks."""
        markdown = """
        This has a [link](https://example.com) and `inline code`.
        
        ```
        Code block
        with multiple
        lines
        ```
        """
        
        plain_text = remove_markdown_formatting(markdown)
        
        # Links should be simplified
        assert "[link](https://example.com)" not in plain_text
        assert "link" in plain_text
        
        # Inline code formatting should be removed
        assert "`inline code`" not in plain_text
        assert "inline code" in plain_text
        
        # Code blocks should be removed
        assert "```" not in plain_text
        # In this implementation, the code block content is removed
        assert "Code block" not in plain_text
        assert "with multiple" not in plain_text
        assert "lines" not in plain_text