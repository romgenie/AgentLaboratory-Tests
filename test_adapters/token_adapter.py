"""
Token utilities adapter for tests.

This module provides adapter functions that make the existing token utilities
compatible with the test suite without modifying the original code.
"""

import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import original functions
from utils.token_utils import count_tokens, truncate_to_token_limit


# Create aliases for functions with different names
get_token_count = count_tokens

# Export the functions expected by tests
__all__ = ['get_token_count', 'truncate_to_token_limit']