import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the main application module
import ai_lab_repo

@pytest.mark.integration
class TestApplicationIntegration:
    """Integration tests for the main application."""
    
    @pytest.fixture
    def mock_args(self):
        """Fixture to create mock command line arguments."""
        args = MagicMock()
        args.api_key = "test_api_key"
        args.llm_backend = "gpt-4o"
        args.research_topic = "Attention mechanisms in transformers"
        args.copilot_mode = "false"
        args.output_file = "test_output.pdf"
        args.compile_latex = "false"
        args.load_existing = False
        args.load_existing_path = None
        args.save_interval = 5
        args.save_checkpoint = True
        return args
    
    @pytest.fixture
    def mock_laboratory(self):
        """Fixture to create a mock AILaboratory instance."""
        laboratory = MagicMock()
        laboratory.set_model.return_value = None
        laboratory.perform_research.return_value = {
            "research_plan": {"objectives": ["Objective 1", "Objective 2"]},
            "literature_review": {"papers": ["Paper 1", "Paper 2"]},
            "data_preparation": {"data_sources": ["Dataset 1"]},
            "experiments": {"results": {"accuracy": 0.92}},
            "report": {"title": "Research Report", "content": "Report content"}
        }
        return laboratory
    
    @patch('ai_lab_repo.AILaboratory')
    @patch('ai_lab_repo.parse_args')
    def test_main_workflow(self, mock_parse_args, mock_ai_laboratory, mock_args, mock_laboratory):
        """Test the main application workflow."""
        # Configure mocks
        mock_parse_args.return_value = mock_args
        mock_ai_laboratory.return_value = mock_laboratory
        
        # Call the main function
        with patch('builtins.print') as mock_print:
            ai_lab_repo.main()
        
        # Verify the laboratory was initialized correctly
        mock_ai_laboratory.assert_called_once()
        
        # Verify the model was set
        mock_laboratory.set_model.assert_called_once_with("gpt-4o")
        
        # Verify research was performed
        mock_laboratory.perform_research.assert_called_once_with(
            research_topic="Attention mechanisms in transformers",
            human_in_loop=False,
            save_interval=5,
            save_path='state_saves/checkpoint'
        )
        
        # Verify that results were printed
        mock_print.assert_any_call("Research Complete!")
    
    @patch('ai_lab_repo.AILaboratory')
    @patch('ai_lab_repo.parse_args')
    def test_copilot_mode(self, mock_parse_args, mock_ai_laboratory, mock_args, mock_laboratory):
        """Test the application with copilot mode enabled."""
        # Update args to enable copilot mode
        mock_args.copilot_mode = "true"
        mock_parse_args.return_value = mock_args
        mock_ai_laboratory.return_value = mock_laboratory
        
        # Call the main function
        with patch('builtins.print') as mock_print:
            ai_lab_repo.main()
        
        # Verify research was performed with human_in_loop=True
        mock_laboratory.perform_research.assert_called_once_with(
            research_topic="Attention mechanisms in transformers",
            human_in_loop=True,
            save_interval=5,
            save_path='state_saves/checkpoint'
        )
    
    @patch('ai_lab_repo.AILaboratory')
    @patch('ai_lab_repo.parse_args')
    @patch('ai_lab_repo.load_laboratory_state')
    def test_load_existing(self, mock_load_state, mock_parse_args, mock_ai_laboratory, 
                          mock_args, mock_laboratory):
        """Test loading an existing laboratory state."""
        # Update args to load existing state
        mock_args.load_existing = True
        mock_args.load_existing_path = "saved_state.pkl"
        mock_parse_args.return_value = mock_args
        mock_ai_laboratory.return_value = mock_laboratory
        
        # Mock the state loading
        mock_load_state.return_value = {"state": "loaded"}
        
        # Call the main function
        with patch('builtins.print') as mock_print:
            ai_lab_repo.main()
        
        # Verify state was loaded
        mock_load_state.assert_called_once_with("saved_state.pkl")
        
        # Verify the laboratory was initialized with the loaded state
        mock_ai_laboratory.assert_called_once()
        
    @patch('ai_lab_repo.AILaboratory')
    @patch('ai_lab_repo.parse_args')
    def test_error_handling(self, mock_parse_args, mock_ai_laboratory, mock_args, mock_laboratory):
        """Test error handling in the main application."""
        # Configure mocks to raise an exception
        mock_parse_args.return_value = mock_args
        mock_ai_laboratory.return_value = mock_laboratory
        mock_laboratory.perform_research.side_effect = Exception("Test error")
        
        # Call the main function
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit):
                ai_lab_repo.main()
        
        # Verify error was printed
        mock_print.assert_any_call("Error during research process: Test error")