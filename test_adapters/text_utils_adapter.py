"""
Text utilities adapter for tests.

This module adapts the original text utilities to work with tests
without modifying the original code.
"""

import re
import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Define adapter functions that match what tests expect

def truncate_text(text, max_length):
    """
    Truncate text to a maximum length, adding an ellipsis if needed.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length for the text
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    if max_length <= 3:
        return "." * max_length
        
    return text[:max_length-3] + "..."

def extract_code_blocks(text):
    """
    Extract code blocks from text (marked with triple backticks).
    
    Args:
        text (str): Text to extract code blocks from
        
    Returns:
        list: List of code block contents
    """
    pattern = r"```(?:\w*\n)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]