import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import io

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the main application module
import ai_lab_repo

"""
CLI Interaction Tests Module

This module provides test cases for validating the command-line interface
interactions with the Agent Laboratory application.

Tests verify:
1. Application launch with different argument combinations
2. Help text display
3. Error messages for invalid arguments
4. Research topic input handling
5. Model selection handling
"""

@pytest.mark.integration
class TestCLIInteractions:
    """Tests for command-line interface interactions with the application."""
    
    @pytest.fixture
    def mock_args(self):
        """Fixture to create mock command line arguments."""
        args = MagicMock()
        args.api_key = "test_api_key"
        args.llm_backend = "gpt-4o"
        args.research_topic = "Attention mechanisms in transformers"
        args.research_dir = "research_dir"
        args.copilot_mode = "false"
        args.compile_latex = "true"
        args.verbose = True
        args.load_existing = False
        args.load_existing_path = None
        args.language = "English"
        return args
    
    @pytest.fixture
    def mock_repository(self):
        """Fixture to create a mock AgentLabRepository instance."""
        repository = MagicMock()
        repository.run_research.return_value = True
        return repository
    
    @patch('ai_lab_repo.AgentLabRepository')
    @patch('ai_lab_repo.parse_args')
    def test_launch_with_different_arguments(self, mock_parse_args, mock_repository_class, mock_args, mock_repository):
        """Test the application can be launched with different argument combinations."""
        # Configure mocks
        mock_parse_args.return_value = mock_args
        mock_repository_class.return_value = mock_repository
        
        # Call the main function
        with patch('builtins.print') as mock_print:
            ai_lab_repo.main()
        
        # Verify the repository was initialized correctly
        mock_repository_class.assert_called_once_with(
            api_key="test_api_key",
            llm_backend="gpt-4o",
            research_topic="Attention mechanisms in transformers",
            research_dir="research_dir",
            copilot_mode=False,
            compile_latex=True,
            verbose=True,
            load_existing=False,
            load_existing_path=None,
            language="English"
        )
        
        # Verify research was run
        mock_repository.run_research.assert_called_once()
    
    @patch('ai_lab_repo.parse_args')
    def test_help_text_display(self, mock_parse_args):
        """Test help text displays correctly."""
        # Mock an args object with help=True
        mock_args = MagicMock()
        mock_args.help = True
        mock_parse_args.return_value = mock_args
        
        # Mock the print_help method
        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            # Test help text display
            with patch('sys.stdout', new=io.StringIO()):
                with pytest.raises(SystemExit):
                    ai_lab_repo.main()
                    
                # Verify help text was displayed
                mock_print_help.assert_called_once()
    
    @patch('ai_lab_repo.parse_args')
    def test_error_messages_for_invalid_arguments(self, mock_parse_args):
        """Test error messages for invalid arguments are meaningful."""
        # Configure mock to simulate error with invalid arguments
        error_message = "the following arguments are required: --api-key, --llm-backend, --research-topic"
        mock_parse_args.side_effect = ValueError(error_message)
        
        # Test error handling
        with patch('sys.stderr', new=io.StringIO()):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit):
                    ai_lab_repo.main()
                
                # Verify error message was displayed
                mock_print.assert_any_call(f"Error: {error_message}")
    
    @patch('ai_lab_repo.AgentLabRepository')
    @patch('ai_lab_repo.parse_args')
    def test_research_topic_handling(self, mock_parse_args, mock_repository_class, mock_args, mock_repository):
        """Test the application handles research topic input correctly."""
        # Setup complex research topic with special characters
        complex_topic = "Quantum computing & ML: integration approaches for the 2020s"
        mock_args.research_topic = complex_topic
        mock_parse_args.return_value = mock_args
        mock_repository_class.return_value = mock_repository
        
        # Call the main function
        with patch('builtins.print'):
            ai_lab_repo.main()
        
        # Verify topic was correctly passed to the repository
        call_args, _ = mock_repository_class.call_args
        assert call_args[2] == complex_topic
    
    @patch('ai_lab_repo.AgentLabRepository')
    @patch('ai_lab_repo.parse_args')
    def test_model_selection_handling(self, mock_parse_args, mock_repository_class, mock_args, mock_repository):
        """Test the application handles model selection correctly."""
        # Test with different supported models
        supported_models = ["o1", "o1-preview", "o1-mini", "gpt-4o", "deepseek-chat"]
        
        for model in supported_models:
            # Reset mocks for each model test
            mock_repository_class.reset_mock()
            
            # Configure mock for this model
            mock_args.llm_backend = model
            mock_parse_args.return_value = mock_args
            mock_repository_class.return_value = mock_repository
            
            # Call the main function
            with patch('builtins.print'):
                ai_lab_repo.main()
            
            # Verify model was correctly passed to the repository
            call_args, _ = mock_repository_class.call_args
            assert call_args[1] == model, f"Failed with model: {model}"
            
    @patch('ai_lab_repo.AgentLabRepository')
    @patch('ai_lab_repo.parse_args')        
    def test_copilot_mode_handling(self, mock_parse_args, mock_repository_class, mock_args, mock_repository):
        """Test the application handles copilot mode correctly."""
        # Test with copilot mode enabled
        mock_args.copilot_mode = "true"
        mock_parse_args.return_value = mock_args
        mock_repository_class.return_value = mock_repository
        
        # Call the main function
        with patch('builtins.print'):
            ai_lab_repo.main()
        
        # Verify copilot mode was correctly passed to the repository
        call_args, _ = mock_repository_class.call_args
        assert call_args[4] == True, "Copilot mode not correctly set to True"
        
        # Test with copilot mode disabled
        mock_repository_class.reset_mock()
        mock_args.copilot_mode = "false"
        
        # Call the main function again
        with patch('builtins.print'):
            ai_lab_repo.main()
        
        # Verify copilot mode was correctly passed to the repository
        call_args, _ = mock_repository_class.call_args
        assert call_args[4] == False, "Copilot mode not correctly set to False"
        
    @patch('ai_lab_repo.AgentLabRepository')
    @patch('ai_lab_repo.parse_args')
    def test_language_selection_handling(self, mock_parse_args, mock_repository_class, mock_args, mock_repository):
        """Test the application handles language selection correctly."""
        # Test with different languages
        languages = ["English", "Chinese", "Spanish", "French", "Japanese"]
        
        for language in languages:
            # Reset mocks for each language test
            mock_repository_class.reset_mock()
            
            # Configure mock for this language
            mock_args.language = language
            mock_parse_args.return_value = mock_args
            mock_repository_class.return_value = mock_repository
            
            # Call the main function
            with patch('builtins.print'):
                ai_lab_repo.main()
            
            # Verify language was correctly passed to the repository
            call_args, _ = mock_repository_class.call_args
            assert call_args[9] == language, f"Failed with language: {language}"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])