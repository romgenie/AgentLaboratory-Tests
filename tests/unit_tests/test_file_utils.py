import pytest
import os
import sys
import json
import tempfile
from unittest.mock import patch, mock_open

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.file_utils import (
    ensure_directory_exists,
    write_text_to_file,
    read_text_from_file,
    save_json,
    load_json
)


class TestFileUtils:
    """Test suite for file utility functions."""
    
    def test_ensure_directory_exists_new_dir(self):
        """Test ensuring a new directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "test_dir")
            
            # Verify directory doesn't exist
            assert not os.path.exists(test_dir)
            
            # Create directory
            ensure_directory_exists(test_dir)
            
            # Verify directory was created
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
    
    def test_ensure_directory_exists_existing_dir(self):
        """Test ensuring an existing directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Directory already exists
            
            # Should not raise an error
            ensure_directory_exists(temp_dir)
            
            # Directory should still exist
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)
    
    def test_write_and_read_text_file(self):
        """Test writing to and reading from a text file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_file.txt")
            test_content = "Test content\nLine 2\nLine 3"
            
            # Write content to file
            write_text_to_file(test_file, test_content)
            
            # Verify file exists
            assert os.path.exists(test_file)
            
            # Read content from file
            read_content = read_text_from_file(test_file)
            
            # Verify content matches
            assert read_content == test_content
    
    def test_write_text_to_nonexistent_dir(self):
        """Test writing to a file in a nonexistent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with nonexistent subdirectory
            nonexistent_dir = os.path.join(temp_dir, "nonexistent")
            test_file = os.path.join(nonexistent_dir, "test_file.txt")
            test_content = "Test content"
            
            # The parent directory does not exist yet
            assert not os.path.exists(nonexistent_dir)
            
            # Write content to file - should create parent directory
            write_text_to_file(test_file, test_content)
            
            # Verify directory and file exist
            assert os.path.exists(nonexistent_dir)
            assert os.path.exists(test_file)
            
            # Verify content was written correctly
            assert read_text_from_file(test_file) == test_content
    
    def test_read_nonexistent_file(self):
        """Test reading from a nonexistent file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "nonexistent.txt")
            
            # Verify file doesn't exist
            assert not os.path.exists(test_file)
            
            # Reading should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                read_text_from_file(test_file)
    
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
    
    def test_save_json_nonexistent_dir(self):
        """Test saving JSON to a file in a nonexistent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with nonexistent subdirectory
            nonexistent_dir = os.path.join(temp_dir, "nonexistent")
            test_file = os.path.join(nonexistent_dir, "test_data.json")
            test_data = {"key": "value"}
            
            # The parent directory does not exist yet
            assert not os.path.exists(nonexistent_dir)
            
            # Save JSON data - should create parent directory
            save_json(test_file, test_data)
            
            # Verify directory and file exist
            assert os.path.exists(nonexistent_dir)
            assert os.path.exists(test_file)
            
            # Verify data was saved correctly
            assert load_json(test_file) == test_data
    
    def test_load_nonexistent_json(self):
        """Test loading from a nonexistent JSON file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "nonexistent.json")
            
            # Verify file doesn't exist
            assert not os.path.exists(test_file)
            
            # Loading should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                load_json(test_file)
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON raises JSONDecodeError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "invalid.json")
            
            # Write invalid JSON
            with open(test_file, "w") as f:
                f.write("This is not valid JSON")
            
            # Loading should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                load_json(test_file)