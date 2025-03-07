import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import from test adapter
from test_adapters.inference_adapter import query_model, curr_cost_est

class TestInferenceModule:
    """Tests for the inference module functionality."""
    
    def test_curr_cost_est(self):
        """Test the current cost estimation function."""
        # Import for patch.dict
        from inference import TOKENS_IN, TOKENS_OUT
        
        # Using patch.dict to mock the global dictionaries without modifying global state
        with patch.dict('inference.TOKENS_IN', {}), patch.dict('inference.TOKENS_OUT', {}):
            # Set known values
            TOKENS_IN["gpt-4o-mini"] = 1000
            TOKENS_OUT["gpt-4o-mini"] = 500
            
            # Calculate expected cost based on rates in curr_cost_est
            expected_cost = (1000 * 0.150 / 1000000) + (500 * 0.6 / 1000000)
            
            # Get actual cost
            actual_cost = curr_cost_est()
            
            # Assert they match
            assert abs(actual_cost - expected_cost) < 1e-10, f"Expected {expected_cost}, got {actual_cost}"
    
    @patch('openai.OpenAI')
    def test_query_model_gpt4o_mini(self, mock_openai):
        """Test querying the GPT-4o-mini model."""
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Setup mock completion
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Call function with test inputs
        result = query_model(
            model_str="gpt-4o-mini",
            prompt="Test prompt",
            system_prompt="Test system prompt",
            openai_api_key="fake-api-key",
            print_cost=False
        )
        
        # Check that OpenAI client was called correctly
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the result is correct
        assert result == "Test response"