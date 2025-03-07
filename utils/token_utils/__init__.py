import tiktoken


def count_tokens(text, model="gpt-4o"):
    """
    Count the number of tokens in a text string for a given model.
    
    Args:
        text (str): Text to count tokens for
        model (str): Model to use for tokenization
        
    Returns:
        int: Number of tokens
    """
    if not text:
        return 0
        
    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)
    
    # Encode the text and count tokens
    tokens = encoding.encode(text)
    return len(tokens)


def truncate_to_token_limit(text, token_limit, model="gpt-4o"):
    """
    Truncate text to fit within a token limit.
    
    Args:
        text (str): Text to truncate
        token_limit (int): Maximum number of tokens
        model (str): Model to use for tokenization
        
    Returns:
        str: Truncated text
    """
    # Handle edge cases
    if not text or token_limit <= 0:
        return ""
        
    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)
    
    # Encode the text
    tokens = encoding.encode(text)
    
    # Check if truncation is needed
    if len(tokens) <= token_limit:
        return text
    
    # Truncate tokens and decode back to text
    truncated_tokens = tokens[:token_limit]
    truncated_text = encoding.decode(truncated_tokens)
    
    return truncated_text