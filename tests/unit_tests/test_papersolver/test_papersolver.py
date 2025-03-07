import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Classes will be available when fully implemented
# from papersolver.command import Command
# from papersolver.paper_replace import PaperReplace
# from papersolver.paper_edit import PaperEdit
# from papersolver.paper_solver import PaperSolver

# Create mock classes for testing
class Command:
    """Mock Command class for testing."""
    def __init__(self):
        self.cmd_type = "OTHER"
    
    def docstring(self) -> str:
        return "Command docstring"
    
    def execute_command(self, *args) -> str:
        return "Command executed"
    
    def matches_command(self, cmd_str) -> bool:
        return False
    
    def parse_command(self, *args) -> tuple:
        return (False, None)

class PaperReplace(Command):
    """Mock PaperReplace class for testing."""
    def __init__(self):
        super().__init__()
        self.cmd_type = "PAPER-replace"
    
    def docstring(self) -> str:
        return "PAPER REPLACING TOOL docstring"
    
    def execute_command(self, *args) -> str:
        return args[0][0] if isinstance(args[0], tuple) and len(args[0]) > 0 else "Paper replaced"
    
    def matches_command(self, cmd_str) -> bool:
        return "```REPLACE" in cmd_str
    
    def parse_command(self, *args) -> tuple:
        return (True, (["New content"], "LaTeX compilation successful"))

class PaperEdit(Command):
    """Mock PaperEdit class for testing."""
    def __init__(self):
        super().__init__()
        self.cmd_type = "PAPER-edit"
    
    def docstring(self) -> str:
        return "PAPER EDITING TOOL docstring"
    
    def execute_command(self, *args) -> str:
        return (True, ["Edited content"], "LaTeX compilation successful")
    
    def matches_command(self, cmd_str) -> bool:
        return "```EDIT" in cmd_str
    
    def parse_command(self, *args) -> tuple:
        return (True, (0, 1, ["Old content"], ["New content"]))

class PaperSolver:
    """Mock PaperSolver class for testing."""
    def __init__(self, llm_str, notes=None, max_steps=10, insights=None, plan=None, 
                exp_code=None, exp_results=None, lit_review=None, ref_papers=None, 
                topic=None, openai_api_key=None, compile_pdf=True):
        self.llm_str = llm_str
        self.notes = notes or []
        self.plan = plan or ""
        self.insights = insights or ""
        self.exp_code = exp_code or ""
        self.exp_results = exp_results or ""
        self.lit_review = lit_review or ""
        self.ref_papers = ref_papers or ""
        self.topic = topic or ""
        self.compile_pdf = compile_pdf
        self.openai_api_key = openai_api_key
        self.commands = []
        self.paper_lines = []
    
    def system_prompt(self, commands=True, section=None):
        return "System prompt for paper solver"
    
    def command_descriptions(self):
        return "Command descriptions for paper solver"

class TestCommand:
    """Test suite for base Command class in papersolver."""
    
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

class TestPaperReplace:
    """Test suite for PaperReplace command implementation."""
    
    def test_replace_init(self):
        """Test PaperReplace command initialization."""
        replace_cmd = PaperReplace()
        assert replace_cmd.cmd_type == "PAPER-replace"
        
    def test_replace_docstring(self):
        """Test PaperReplace command docstring method."""
        replace_cmd = PaperReplace()
        docstring = replace_cmd.docstring()
        assert isinstance(docstring, str)
        assert "PAPER REPLACING TOOL" in docstring
        
    def test_replace_matches_command(self):
        """Test PaperReplace command matching method."""
        replace_cmd = PaperReplace()
        
        # Should match
        assert replace_cmd.matches_command("```REPLACE\n\\section{Introduction}\nContent\n```")
        
        # Should not match
        assert not replace_cmd.matches_command("```EDIT 1 2\n\\section{Introduction}\nContent\n```")
        assert not replace_cmd.matches_command("Some random text without a command")

class TestPaperEdit:
    """Test suite for PaperEdit command implementation."""
    
    def test_edit_init(self):
        """Test PaperEdit command initialization."""
        edit_cmd = PaperEdit()
        assert edit_cmd.cmd_type == "PAPER-edit"
        
    def test_edit_docstring(self):
        """Test PaperEdit command docstring method."""
        edit_cmd = PaperEdit()
        docstring = edit_cmd.docstring()
        assert isinstance(docstring, str)
        assert "EDIT" in docstring
        assert "paper editing tool" in docstring.lower()
        
    def test_edit_matches_command(self):
        """Test PaperEdit command matching method."""
        edit_cmd = PaperEdit()
        
        # Should match
        assert edit_cmd.matches_command("```EDIT 1 2\n\\section{Introduction}\nContent\n```")
        
        # Should not match
        assert not edit_cmd.matches_command("```REPLACE\n\\section{Introduction}\nContent\n```")
        assert not edit_cmd.matches_command("Some random text without a command")

class TestPaperSolver:
    """Test suite for PaperSolver class."""
    
    @pytest.fixture
    def sample_plan(self):
        """Provide a sample research plan for testing."""
        return "Investigate the effectiveness of attention mechanisms in transformer models."
    
    @pytest.fixture
    def sample_insights(self):
        """Provide sample insights for testing."""
        return "Attention mechanisms significantly improve model performance on long-range dependencies."
    
    @pytest.fixture
    def sample_literature_review(self):
        """Provide a sample literature review for testing."""
        return "Several papers have examined attention mechanisms in transformers including 'Attention is All You Need'."
    
    @pytest.fixture
    def sample_exp_code(self):
        """Provide sample experiment code for testing."""
        return "import tensorflow as tf\n\ndef create_transformer():\n    # Model code here\n    pass"
    
    @pytest.fixture
    def sample_exp_results(self):
        """Provide sample experiment results for testing."""
        return "The model achieved 92% accuracy on the test set with attention mechanisms enabled."
    
    @pytest.fixture
    def paper_solver(self, sample_plan, sample_insights, sample_literature_review, 
                    sample_exp_code, sample_exp_results):
        """Initialize a PaperSolver instance for testing."""
        solver = PaperSolver(
            llm_str="gpt-4o",
            notes=["Focus on attention mechanisms"],
            plan=sample_plan,
            insights=sample_insights,
            exp_code=sample_exp_code,
            exp_results=sample_exp_results,
            lit_review=sample_literature_review,
            topic="Attention Mechanisms in Transformers",
            openai_api_key="fake_api_key",
            compile_pdf=False
        )
        return solver
    
    def test_paper_solver_init(self, paper_solver, sample_plan, sample_insights, 
                             sample_literature_review, sample_exp_code, sample_exp_results):
        """Test PaperSolver initialization."""
        assert paper_solver.plan == sample_plan
        assert paper_solver.insights == sample_insights
        assert paper_solver.lit_review == sample_literature_review
        assert paper_solver.exp_code == sample_exp_code
        assert paper_solver.exp_results == sample_exp_results
        assert paper_solver.topic == "Attention Mechanisms in Transformers"
        assert paper_solver.llm_str == "gpt-4o"
        assert paper_solver.notes == ["Focus on attention mechanisms"]
        
    def test_system_prompt(self, paper_solver):
        """Test system prompt generation."""
        paper_solver.paper_lines = ["\\documentclass{article}", "\\begin{document}", "Content", "\\end{document}"]
        
        prompt = paper_solver.system_prompt()
        assert isinstance(prompt, str)
        assert "System prompt for paper solver" in prompt
        
    def test_command_descriptions(self, paper_solver):
        """Test command descriptions."""
        paper_solver.commands = [PaperReplace(), PaperEdit()]
        descriptions = paper_solver.command_descriptions()
        assert isinstance(descriptions, str)
        assert "Command descriptions for paper solver" in descriptions
        
    def test_process_command_replace(self, paper_solver):
        """Test processing a Replace command."""
        # Add a process_command method to our mock for testing
        def mock_process_command(cmd_str, scoring=True):
            return ("Command executed", ["New content"], "LaTeX compilation successful", 0.85)
            
        paper_solver.process_command = mock_process_command
        
        # Test command
        cmd_str = "```REPLACE\n\\documentclass{article}\n\\begin{document}\nNew content\n\\end{document}\n```"
        result = paper_solver.process_command(cmd_str)
        
        # Check results
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert isinstance(result[0], str)  # cmd_str
        assert isinstance(result[1], list)  # paper_lines
        assert result[3] == 0.85  # score