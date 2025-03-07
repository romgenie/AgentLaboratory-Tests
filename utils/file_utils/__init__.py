import os
import json


def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if it doesn't.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        None
    """
    os.makedirs(directory_path, exist_ok=True)


def write_text_to_file(file_path, content):
    """
    Write text content to a file.
    
    Args:
        file_path (str): Path to the file
        content (str): Text content to write
        
    Returns:
        None
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_text_from_file(file_path):
    """
    Read text content from a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File content
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def save_json(file_path, data):
    """
    Save data as JSON to a file.
    
    Args:
        file_path (str): Path to the file
        data (dict/list): Data to save
        
    Returns:
        None
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_json(file_path):
    """
    Load JSON data from a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict/list: Loaded data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)