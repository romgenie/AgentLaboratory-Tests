import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import modules needed for integration testing
from agents.professor_agent import ProfessorAgent
from agents.phd_student_agent import PhDStudentAgent
from agents.reviewers_agent import ReviewersAgent
from agents_phases.plan_formulation import PlanFormulation
from agents_phases.literature_review import LiteratureReview
from agents_phases.data_preparation import DataPreparation

@pytest.mark.integration
class TestResearchPhaseIntegration:
    """Integration tests for the research phase workflow."""
    
    @pytest.fixture
    def mock_agents(self):
        """Fixture to create mock agents for integration testing."""
        professor = ProfessorAgent(
            name="Test Professor",
            expertise=["Machine Learning", "NLP"],
            personality_traits=["analytical", "thorough"],
            model="gpt-4o"
        )
        
        phd_student = PhDStudentAgent(
            name="Test PhD Student",
            expertise=["Deep Learning", "Transformer Models"],
            personality_traits=["creative", "curious"],
            model="gpt-4o"
        )
        
        reviewers = ReviewersAgent(
            name="Test Reviewers Panel",
            expertise=["Machine Learning", "Research Methods", "Statistics"],
            personality_traits=["critical", "detail-oriented"],
            model="gpt-4o"
        )
        
        return {
            "professor": professor,
            "phd_student": phd_student,
            "reviewers": reviewers
        }
    
    @pytest.fixture
    def test_research_dir(self, tmpdir):
        """Fixture to create a temporary research directory."""
        research_dir = os.path.join(str(tmpdir), "research")
        os.makedirs(research_dir, exist_ok=True)
        return research_dir
    
    @patch('agents_tools.arxiv_search.search_arxiv')
    @patch('agents_tools.semantic_scholar_search.search_semantic_scholar')
    @patch('agents.professor_agent.ProfessorAgent.get_response')
    @patch('agents.phd_student_agent.PhDStudentAgent.get_response')
    @patch('agents.reviewers_agent.ReviewersAgent.get_response')
    def test_literature_to_plan_flow(self, mock_reviewers_response, mock_phd_response, 
                                   mock_professor_response, mock_semantic_scholar, 
                                   mock_arxiv, mock_agents, test_research_dir):
        """Test the flow from literature review to plan formulation."""
        # Configure mocks
        mock_arxiv.return_value = [
            {
                'id': '2201.12345',
                'title': 'Advanced Methods in Machine Learning',
                'authors': ['John Smith', 'Jane Doe'],
                'summary': 'This paper presents advanced methods in machine learning.',
                'published': '2022-01-15'
            }
        ]
        
        mock_semantic_scholar.return_value = [
            {
                'paperId': 'abc123',
                'title': 'Deep Learning in Natural Language Processing',
                'authors': [{'name': 'John Smith'}, {'name': 'Jane Doe'}],
                'abstract': 'This paper explores deep learning approaches in NLP.',
                'year': 2021,
                'citationCount': 150
            }
        ]
        
        # Mock agent responses for literature review
        mock_phd_response.side_effect = [
            "Initial literature analysis...",
            "Key insights: Insight 1, Insight 2",
            "Methodologies: Method A, Method B",
            "Research gaps: Gap X, Gap Y",
            "Literature synthesis: Research synthesis..."
        ]
        
        # Mock agent responses for plan formulation
        mock_professor_response.side_effect = [
            "Research Question 1\nResearch Question 2",
            "Objective 1\nObjective 2",
            "Finalized plan: Plan details..."
        ]
        
        mock_phd_response.side_effect = [
            "Methodology Step 1\nMethodology Step 2\nMethodology Step 3",
            "Experiment plan: Experiment details..."
        ]
        
        mock_reviewers_response.return_value = "Review feedback: Comments..."
        
        # Test the integration between literature review and plan formulation
        literature_review = LiteratureReview(
            phd_student_agent=mock_agents["phd_student"],
            research_topic="Test Research Topic",
            research_dir=test_research_dir
        )
        
        # Execute literature review
        lit_results = literature_review.execute()
        
        # Verify literature review results
        assert isinstance(lit_results, dict)
        assert "papers" in lit_results
        assert "key_insights" in lit_results
        assert "methodologies" in lit_results
        assert "research_gaps" in lit_results
        assert "synthesis" in lit_results
        
        # Create plan formulation with literature review results
        plan_formulation = PlanFormulation(
            professor_agent=mock_agents["professor"],
            phd_student_agent=mock_agents["phd_student"],
            reviewers_agent=mock_agents["reviewers"],
            research_topic="Test Research Topic",
            literature_review=lit_results,
            research_dir=test_research_dir
        )
        
        # Execute plan formulation
        plan_results = plan_formulation.execute()
        
        # Verify plan formulation results
        assert isinstance(plan_results, dict)
        assert "research_questions" in plan_results
        assert "objectives" in plan_results
        assert "methodology" in plan_results
        
        # Verify the integration by checking if literature review insights
        # were used in the plan formulation
        assert mock_professor_response.call_count >= 2
        assert mock_phd_response.call_count >= 4
        assert mock_reviewers_response.call_count >= 1