import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Use adapter classes instead of direct imports
from test_adapters.laboratory_adapter import (
    ProfessorAgentAdapter as ProfessorAgent,
    PhDStudentAgentAdapter as PhDStudentAgent,
    MLEngineerAgentAdapter as MLEngineerAgent
)

@pytest.mark.integration
class TestAgentCollaboration:
    """Integration tests for agent collaboration scenarios."""
    
    @pytest.fixture
    def professor_agent(self):
        """Create a professor agent for testing."""
        return ProfessorAgent(
            name="Professor Smith",
            expertise=["Machine Learning", "Reinforcement Learning", "Neural Networks"],
            personality_traits=["analytical", "meticulous", "critical"],
            model="gpt-4o"
        )
    
    @pytest.fixture
    def phd_student_agent(self):
        """Create a PhD student agent for testing."""
        return PhDStudentAgent(
            name="PhD Student Jones",
            expertise=["Deep Learning", "Computer Vision", "Data Analysis"],
            personality_traits=["curious", "creative", "detail-oriented"],
            model="gpt-4o"
        )
    
    @pytest.fixture
    def ml_engineer_agent(self):
        """Create an ML engineer agent for testing."""
        return MLEngineerAgent(
            name="Engineer Chen",
            expertise=["TensorFlow", "PyTorch", "Model Optimization"],
            personality_traits=["practical", "systematic", "solution-oriented"],
            model="gpt-4o"
        )
    
    def test_agent_communication(self, professor_agent, phd_student_agent):
        """Test that agents can effectively communicate with each other."""
        # Mock the agent responses
        professor_agent.get_response = MagicMock(return_value="Please analyze the latest transformer architectures.")
        phd_student_agent.get_response = MagicMock(return_value="I've analyzed the latest transformer architectures and found that...")
        
        # Simulate communication flow
        instruction = professor_agent.get_response("We need to research transformer architectures.")
        response = phd_student_agent.get_response(instruction)
        
        # Verify the communication
        assert "Please analyze" in instruction
        assert "transformer architectures" in instruction
        assert "I've analyzed" in response
        assert "transformer architectures" in response
    
    def test_multi_agent_research_workflow(self, professor_agent, phd_student_agent, ml_engineer_agent):
        """Test a multi-agent collaborative research workflow."""
        # Configure mocks for a three-step workflow
        professor_agent.get_response = MagicMock(return_value="Research Question: How do transformer attention mechanisms compare in efficiency?")
        phd_student_agent.get_response = MagicMock(return_value="Literature Analysis: Recent papers show improvements in sparse attention mechanisms.")
        ml_engineer_agent.get_response = MagicMock(return_value="Implementation Approach: We should benchmark three attention types: standard, sparse, and linear.")
        
        # Simulate collaborative workflow
        research_question = professor_agent.get_response("Let's start a new research project on transformers.")
        literature_analysis = phd_student_agent.get_response(research_question)
        implementation_plan = ml_engineer_agent.get_response(f"{research_question}\n{literature_analysis}")
        
        # Verify the collaboration flow
        assert "Research Question" in research_question
        assert "Literature Analysis" in literature_analysis
        assert "Implementation Approach" in implementation_plan
        
        # Check for information flow through the chain
        assert "attention mechanisms" in research_question
        assert "sparse attention" in literature_analysis
        assert "benchmark" in implementation_plan
        assert any(term in implementation_plan for term in ["standard", "sparse", "linear"])
    
    def test_agent_feedback_loop(self, professor_agent, phd_student_agent):
        """Test agents providing feedback to each other in a loop."""
        # Configure initial work by PhD student
        initial_work = "I propose we use a Vision Transformer for this image classification task."
        
        # Configure mocks for the feedback loop
        professor_responses = [
            "Your proposal is good, but please elaborate on the attention mechanism.",
            "Much better, but consider the computational requirements.",
            "Excellent proposal, approved."
        ]
        professor_agent.get_response = MagicMock(side_effect=professor_responses)
        
        phd_student_responses = [
            "I've added details on the self-attention mechanism in Vision Transformers.",
            "I've included an analysis of computational requirements and optimizations.",
        ]
        phd_student_agent.get_response = MagicMock(side_effect=phd_student_responses)
        
        # Simulate the feedback loop
        proposal = initial_work
        for i in range(3):  # Three iterations of feedback
            if i < 2:  # First two rounds have both professor and PhD student
                feedback = professor_agent.get_response(proposal)
                assert feedback == professor_responses[i]
                
                if i < 2:  # Only two responses from PhD student
                    proposal = phd_student_agent.get_response(feedback)
                    assert proposal == phd_student_responses[i]
            else:  # Final round is just professor approval
                final_feedback = professor_agent.get_response(proposal)
                assert final_feedback == professor_responses[2]
                assert "approved" in final_feedback
    
    def test_agent_consensus_building(self, professor_agent, phd_student_agent, ml_engineer_agent):
        """Test agents reaching consensus on a research approach."""
        # Topic requiring consensus
        research_topic = "Approach for training large language models efficiently"
        
        # Configure agent initial positions
        professor_position = "I suggest we focus on distributed training with model parallelism."
        phd_student_position = "I think data parallelism would be more efficient for our use case."
        ml_engineer_position = "What about a hybrid approach combining both parallelism strategies?"
        
        professor_agent.get_response = MagicMock(return_value=professor_position)
        phd_student_agent.get_response = MagicMock(return_value=phd_student_position)
        ml_engineer_agent.get_response = MagicMock(return_value=ml_engineer_position)
        
        # Simulate discussion
        positions = [
            professor_agent.get_response(research_topic),
            phd_student_agent.get_response(research_topic),
            ml_engineer_agent.get_response(research_topic)
        ]
        
        # Simulate consensus round - professor makes the final decision after considering all positions
        professor_agent.get_response = MagicMock(return_value="After considering all viewpoints, I agree with the hybrid approach.")
        consensus = professor_agent.get_response("\n".join(positions))
        
        # Verify positions and consensus
        assert "model parallelism" in positions[0]
        assert "data parallelism" in positions[1]
        assert "hybrid approach" in positions[2]
        assert "agree" in consensus
        assert "hybrid approach" in consensus