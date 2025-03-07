import re


def truncate_text(text, max_length=100):
    """
    Truncate text to a maximum length, adding ellipsis if truncated.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def extract_code_blocks(markdown_text):
    """
    Extract code blocks from markdown text.
    
    Args:
        markdown_text (str): Markdown text
        
    Returns:
        list: List of code block contents
    """
    # Match code blocks: ```...``` or ```language...```
    # This pattern handles variations in indentation and whitespace
    pattern = r'```(?:\w+)?\s*(.*?)\s*```'
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    # Strip leading/trailing whitespace from each extracted block
    return [match.strip() for match in matches]


def remove_markdown_formatting(markdown_text):
    """
    Remove markdown formatting from text.
    
    Args:
        markdown_text (str): Markdown formatted text
        
    Returns:
        str: Plain text
    """
    # Remove headers
    text = re.sub(r'#+\s+(.*?)\n', r'\1\n', markdown_text)
    
    # Remove bold and italic formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Remove link formatting
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    return text