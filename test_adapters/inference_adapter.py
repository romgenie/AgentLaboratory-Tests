"""
Inference adapter for tests.

This module provides adapter functions that expose the inference functionality
that tests expect, without modifying the original code.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Union

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the actual implementation
from inference.query_model import query_model as original_query_model

# Enhanced query_model with more testing capabilities
def query_model(model_str, prompt, system_prompt=None, openai_api_key=None, temp=0.7, max_tokens=None):
    """
    Query a language model with enhanced testing capabilities.
    
    Args:
        model_str (str): Model identifier
        prompt (str): Input prompt
        system_prompt (str, optional): System prompt
        openai_api_key (str, optional): OpenAI API key
        temp (float, optional): Temperature parameter
        max_tokens (int, optional): Maximum tokens in response
        
    Returns:
        str: Model response
    """
    # Call the original implementation
    return original_query_model(model_str, prompt, system_prompt, openai_api_key, temp, max_tokens)

def calculate_token_usage(prompt: str, model_str: str = "gpt-4") -> Dict[str, int]:
    """
    Calculate token usage for a given prompt and model.
    
    Args:
        prompt (str): The prompt text
        model_str (str): Model identifier
        
    Returns:
        dict: Token usage information
    """
    # Simple mock implementation for testing
    return {
        "prompt_tokens": len(prompt) // 4,  # Very rough approximation
        "completion_tokens": len(prompt) // 8,
        "total_tokens": len(prompt) // 4 + len(prompt) // 8
    }

def estimate_cost(tokens: Dict[str, int], model_str: str = "gpt-4") -> float:
    """
    Estimate cost for a given token usage and model.
    
    Args:
        tokens (dict): Token usage information
        model_str (str): Model identifier
        
    Returns:
        float: Estimated cost in USD
    """
    # Mock cost rates for testing
    cost_rates = {
        "gpt-4": {"prompt": 0.00003, "completion": 0.00006},
        "gpt-4o": {"prompt": 0.00005, "completion": 0.00015},
        "o1-preview": {"prompt": 0.00015, "completion": 0.00025},
        "deepseek-chat": {"prompt": 0.00001, "completion": 0.00002},
        "default": {"prompt": 0.00002, "completion": 0.00004}
    }
    
    # Get cost rates for the model, defaulting to "default" if not found
    rates = cost_rates.get(model_str, cost_rates["default"])
    
    # Calculate cost
    prompt_cost = tokens["prompt_tokens"] * rates["prompt"]
    completion_cost = tokens["completion_tokens"] * rates["completion"]
    
    return prompt_cost + completion_cost

def track_request(model_str: str, prompt: str, response: str) -> Dict[str, Any]:
    """
    Track an API request for monitoring and logging.
    
    Args:
        model_str (str): Model identifier
        prompt (str): Input prompt
        response (str): Model response
        
    Returns:
        dict: Request tracking information
    """
    # Calculate token usage
    tokens = calculate_token_usage(prompt, model_str)
    
    # Estimate cost
    cost = estimate_cost(tokens, model_str)
    
    # Create tracking information
    return {
        "model": model_str,
        "prompt_length": len(prompt),
        "response_length": len(response),
        "tokens": tokens,
        "cost": cost,
        "timestamp": "2023-01-01T00:00:00Z"  # Mock timestamp for testing
    }

# Create any additional functionality or aliases needed by tests
__all__ = [
    'query_model', 
    'calculate_token_usage', 
    'estimate_cost', 
    'track_request'
]