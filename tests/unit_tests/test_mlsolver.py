import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mlsolver.command import Command
from mlsolver.replace import Replace
from mlsolver.edit import Edit
from mlsolver.mle_solver import MLESolver, get_score, code_repair, execute_code, extract_prompt

class TestCommand:
    """Test suite for base Command class and its implementations."""
    
    def test_command_interface(self):
        """Test that Command class defines required interface methods."""
        cmd = Command()
        
        # Verify Command has required abstract methods
        assert hasattr(cmd, 'docstring')
        assert hasattr(cmd, 'execute_command')
        assert hasattr(cmd, 'matches_command')
        assert hasattr(cmd, 'parse_command')
        
        # Verify the cmd_type attribute is set
        assert hasattr(cmd, 'cmd_type')
        assert cmd.cmd_type == "OTHER"

class TestReplace:
    """Test suite for Replace command implementation."""
    
    def test_replace_init(self):
        """Test Replace command initialization."""
        replace_cmd = Replace()
        assert replace_cmd.cmd_type == "CODE-replace"
        
    def test_replace_docstring(self):
        """Test Replace command docstring method."""
        replace_cmd = Replace()
        docstring = replace_cmd.docstring()
        assert isinstance(docstring, str)
        assert "REPLACE" in docstring
        assert "code replacing tool" in docstring.lower()
        
    def test_replace_matches_command(self):
        """Test Replace command matching method."""
        replace_cmd = Replace()
        
        # Should match
        assert replace_cmd.matches_command("```REPLACE\ndef function():\n    pass\n```")
        
        # Should not match
        assert not replace_cmd.matches_command("```EDIT 1 2\ndef function():\n    pass\n```")
        assert not replace_cmd.matches_command("Some random text without a command")
        
    def test_replace_execute_command(self):
        """Test Replace command execution."""
        replace_cmd = Replace()
        
        # Simple test case
        test_code = "def test_function():\n    return 42"
        args = (test_code,)
        
        result = replace_cmd.execute_command(args)
        assert result == test_code


class TestEdit:
    """Test suite for Edit command implementation."""
    
    def test_edit_init(self):
        """Test Edit command initialization."""
        edit_cmd = Edit()
        assert edit_cmd.cmd_type == "CODE-edit"
        
    def test_edit_docstring(self):
        """Test Edit command docstring method."""
        edit_cmd = Edit()
        docstring = edit_cmd.docstring()
        assert isinstance(docstring, str)
        assert "EDIT" in docstring
        assert "code editing tool" in docstring.lower()
        
    def test_edit_matches_command(self):
        """Test Edit command matching method."""
        edit_cmd = Edit()
        
        # Should match
        assert edit_cmd.matches_command("```EDIT 1 2\ndef function():\n    pass\n```")
        
        # Should not match
        assert not edit_cmd.matches_command("```REPLACE\ndef function():\n    pass\n```")
        assert not edit_cmd.matches_command("Some random text without a command")


@patch('mlsolver.mle_solver.query_model')
class TestMLESolver:
    """Test suite for MLESolver class."""
    
    @pytest.fixture
    def sample_dataset_code(self):
        """Provide sample dataset code for testing."""
        return "import numpy as np\nimport pandas as pd\n\ndef load_data():\n    return np.random.rand(100, 10), np.random.randint(0, 2, 100)"
    
    @pytest.fixture
    def sample_plan(self):
        """Provide a sample research plan for testing."""
        return "Build a machine learning model to classify the data with at least 80% accuracy."
    
    @pytest.fixture
    def sample_insights(self):
        """Provide sample insights for testing."""
        return "Recent research shows that ensemble methods often perform better on this type of data."
    
    @pytest.fixture
    def mle_solver(self, sample_dataset_code, sample_plan, sample_insights):
        """Initialize an MLESolver instance for testing."""
        return MLESolver(
            dataset_code=sample_dataset_code,
            openai_api_key="fake_api_key",
            notes=["Use cross-validation"],
            plan=sample_plan,
            insights=sample_insights,
            llm_str="gpt-4o"
        )
    
    def test_mle_solver_init(self, _, mle_solver, sample_dataset_code, sample_plan, sample_insights):
        """Test MLESolver initialization."""
        assert mle_solver.dataset_code == sample_dataset_code
        assert mle_solver.plan == sample_plan
        assert mle_solver.insights == sample_insights
        assert mle_solver.llm_str == "gpt-4o"
        assert mle_solver.notes == ["Use cross-validation"]
        assert mle_solver.max_steps == 10
        
    def test_system_prompt(self, _, mle_solver):
        """Test system prompt generation."""
        prompt = mle_solver.system_prompt()
        assert isinstance(prompt, str)
        assert "expert machine learning engineer" in prompt.lower()
        assert mle_solver.plan in prompt
        assert mle_solver.insights in prompt
        assert "dataset code" in prompt.lower()
        
    def test_command_descriptions(self, _, mle_solver):
        """Test command descriptions."""
        mle_solver.commands = [Replace(), Edit()]
        descriptions = mle_solver.command_descriptions()
        assert isinstance(descriptions, str)
        assert "EDIT" in descriptions
        assert "REPLACE" in descriptions
        
    @patch('mlsolver.mle_solver.execute_code')
    @patch('mlsolver.mle_solver.get_score')
    def test_process_command_replace(self, mock_get_score, mock_execute_code, mock_query_model, mle_solver):
        """Test processing a Replace command."""
        # Configure mocks
        mock_execute_code.return_value = "Test execution output"
        mock_get_score.return_value = (0.85, "Score summary", True)
        
        # Set up the command and code
        mle_solver.commands = [Replace()]
        mle_solver.code_lines = ["# Old code"]
        mle_solver.dataset_code = "# Dataset code"
        
        # Test command
        cmd_str = "```REPLACE\n# New code\n```"
        result = mle_solver.process_command(cmd_str)
        
        # Check results
        assert isinstance(result, tuple)
        assert len(result) == 5
        assert isinstance(result[0], str)  # cmd_str
        assert isinstance(result[1], list)  # code_lines
        assert isinstance(result[3], bool)  # should_execute_code
        assert result[4] == 0.85  # score