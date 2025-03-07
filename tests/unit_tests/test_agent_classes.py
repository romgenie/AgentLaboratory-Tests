import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from test_adapters.laboratory_adapter import (
    BaseAgentAdapter as BaseAgent,
    ProfessorAgentAdapter as ProfessorAgent,
    PhDStudentAgentAdapter as PhDStudentAgent,
    MLEngineerAgentAdapter as MLEngineerAgent,
    mock_query_model as query_model
)

# Create a concrete test agent implementation with its own test methods
class _TestAgentHelper(BaseAgent):
    """Concrete implementation of the BaseAgent class for testing."""
    
    def __init__(self, name, expertise, personality_traits, model):
        """Initialize the test agent with extra test properties."""
        super().__init__(name, expertise, personality_traits, model)
        self.last_call = None
        self.test_responses = []
    
    def test_method(self, input_text):
        """A test method specific to this test implementation."""
        result = f"Processed {input_text} with {self.name}"
        self.test_responses.append(result)
        return result

class TestBaseAgent:
    """Test suite for the BaseAgent class."""

    @pytest.fixture
    def base_agent(self):
        """Create an instance of _TestAgentHelper for testing."""
        return _TestAgentHelper(
            name="Test Agent",
            expertise=["Testing"],
            personality_traits=["methodical"],
            model="test-model"
        )
    
    def test_initialization(self, base_agent):
        """Test that the agent initializes with the correct default values."""
        assert base_agent.name == "Test Agent"
        assert base_agent.expertise == ["Testing"]
        assert base_agent.personality_traits == ["methodical"]
        assert base_agent.model == "test-model"
        assert base_agent.memory == []
        assert base_agent.conversation_history == []

    def test_get_response(self, base_agent):
        """Test the get_response method."""
        # Call get_response
        response = base_agent.get_response("Test prompt for the agent")
        
        # Verify response format
        assert "Response from Test Agent about" in response
        assert "Test prompt for" in response
    
    def test_add_to_memory(self, base_agent):
        """Test adding interactions to memory."""
        # Add to memory
        base_agent.add_to_memory("Test prompt", "Test response")
        
        # Verify memory was updated
        assert len(base_agent.memory) == 1
        assert base_agent.memory[0]["prompt"] == "Test prompt"
        assert base_agent.memory[0]["response"] == "Test response"
        
        # Add another entry
        base_agent.add_to_memory("Second prompt", "Second response")
        
        # Verify second entry
        assert len(base_agent.memory) == 2
        assert base_agent.memory[1]["prompt"] == "Second prompt"
        assert base_agent.memory[1]["response"] == "Second response"
    
    def test_get_system_prompt(self, base_agent):
        """Test getting the system prompt."""
        # Get system prompt
        system_prompt = base_agent.get_system_prompt()
        
        # Verify content
        assert "Test Agent" in system_prompt
        assert "Testing" in system_prompt
        assert "methodical" in system_prompt
        
    def test_analyze_approach(self, base_agent):
        """Test analyzing a research approach."""
        # Call analyze_approach
        analysis = base_agent.analyze_approach("AI Safety", "ethical concerns")
        
        # Verify response format
        assert "Test Agent's analysis of ethical concerns for AI Safety" in analysis

    def test_custom_test_method(self, base_agent):
        """Test the custom test method added to our TestAgentHelper."""
        # Call the custom method
        result = base_agent.test_method("sample input")
        
        # Verify response and state update
        assert result == "Processed sample input with Test Agent"
        assert len(base_agent.test_responses) == 1
        assert base_agent.test_responses[0] == "Processed sample input with Test Agent"


class TestSpecializedAgents:
    """Test specialized agent implementations."""
    
    @pytest.fixture
    def professor_agent(self):
        return ProfessorAgent(
            name="Professor Smith",
            expertise=["Computer Science", "Machine Learning"],
            personality_traits=["analytical", "thorough"],
            model="test-model"
        )
        
    @pytest.fixture
    def phd_student_agent(self):
        return PhDStudentAgent(
            name="PhD Student Jones",
            expertise=["Data Science", "Neural Networks"],
            personality_traits=["curious", "dedicated"],
            model="test-model"
        )
        
    @pytest.fixture
    def ml_engineer_agent(self):
        return MLEngineerAgent(
            name="ML Engineer Taylor",
            expertise=["Deep Learning", "Model Optimization"],
            personality_traits=["practical", "detail-oriented"],
            model="test-model"
        )
    
    def test_professor_agent_phases(self, professor_agent):
        """Test that professor has the correct phases."""
        assert professor_agent.phases == ["report writing"]
        assert "a computer science professor" in professor_agent.role_description()
        
    def test_phd_student_agent_phases(self, phd_student_agent):
        """Test that PhD student has the correct phases."""
        expected_phases = [
            "literature review",
            "plan formulation",
            "running experiments",
            "results interpretation",
            "report writing",
            "report refinement",
        ]
        assert phd_student_agent.phases == expected_phases
        assert phd_student_agent.lit_review == []
        assert "computer science PhD student" in phd_student_agent.role_description()
        
    def test_ml_engineer_phases(self, ml_engineer_agent):
        """Test that ML engineer has the correct phases."""
        expected_phases = [
            "data preparation",
            "running experiments",
        ]
        assert ml_engineer_agent.phases == expected_phases
        assert "machine learning engineer" in ml_engineer_agent.role_description()
        
    @patch('inference.query_model')
    def test_phd_student_add_review(self, mock_query, phd_student_agent):
        """Test adding a review to the literature review."""
        # Setup mock arxiv engine
        mock_arxiv_engine = MagicMock()
        mock_arxiv_engine.retrieve_full_paper_text.return_value = "Full paper text"
        
        # Add a review
        message, _ = phd_student_agent.add_review(
            "2104.12871\nThis paper discusses transformer architectures", 
            mock_arxiv_engine
        )
        
        # Verify
        assert "Successfully added" in message
        assert len(phd_student_agent.lit_review) == 1
        assert phd_student_agent.lit_review[0]["arxiv_id"] == "2104.12871"
        assert phd_student_agent.lit_review[0]["full_text"] == "Full paper text"
        assert "transformer architectures" in phd_student_agent.lit_review[0]["summary"]
        
    def test_phd_student_format_review(self, phd_student_agent):
        """Test formatting the literature review."""
        # Add mock entries to lit_review
        phd_student_agent.lit_review = [
            {"arxiv_id": "2104.12871", "full_text": "text1", "summary": "Transformers paper"},
            {"arxiv_id": "1904.00554", "full_text": "text2", "summary": "NLP research"}
        ]
        
        # Get formatted review
        formatted = phd_student_agent.format_review()
        
        # Verify
        assert "literature review" in formatted
        assert "2104.12871" in formatted
        assert "1904.00554" in formatted
        assert "Transformers paper" in formatted
        assert "NLP research" in formatted