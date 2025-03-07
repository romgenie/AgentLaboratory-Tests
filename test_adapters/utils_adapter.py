"""
Utils adapter for tests.

This module provides adapter functions for utility classes and functions
that tests expect, without modifying the original code.
"""

import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import utilities from their respective modules
from utils.file_utils import ensure_directory_exists, write_text_to_file, read_text_from_file, save_json, load_json
from test_adapters.text_utils_adapter import truncate_text, extract_code_blocks
from utils.token_utils import count_tokens, truncate_to_token_limit

# Create aliases for functions with different names
get_token_count = count_tokens

# Export all functions expected by tests
__all__ = [
    # File utilities
    'ensure_directory_exists',
    'write_text_to_file',
    'read_text_from_file',
    'save_json',
    'load_json',
    
    # Text utilities
    'truncate_text',
    'extract_code_blocks',
    
    # Token utilities
    'get_token_count',
    'truncate_to_token_limit'
]