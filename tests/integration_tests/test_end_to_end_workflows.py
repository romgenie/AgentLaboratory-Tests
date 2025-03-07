import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import ai_lab_repo
from agents.professor_agent import ProfessorAgent
from agents.phd_student_agent import PhDStudentAgent
from agents.ml_engineer_agent import MLEngineerAgent
from agents.reviewers_agent import ReviewersAgent
from agents_phases.plan_formulation import PlanFormulation
from agents_phases.literature_review import LiteratureReview
from agents_phases.running_experiments import RunningExperiments
from agents_phases.report_writing import ReportWriting

@pytest.mark.integration
class TestEndToEndWorkflows:
    """Integration tests for end-to-end research workflows."""
    
    @pytest.fixture
    def mock_agents(self):
        """Create a set of mock agents for testing."""
        agents = {
            "professor": MagicMock(spec=ProfessorAgent),
            "phd_student": MagicMock(spec=PhDStudentAgent),
            "ml_engineer": MagicMock(spec=MLEngineerAgent),
            "reviewers": MagicMock(spec=ReviewersAgent)
        }
        
        # Configure mock behaviors
        for name, agent in agents.items():
            agent.name = f"{name.capitalize()} Agent"
            agent.expertise = ["Machine Learning", "Research"]
            agent.personality_traits = ["analytical"]
            agent.model = "gpt-4o"
            agent.get_response = MagicMock(return_value=f"Response from {name} agent")
        
        return agents
    
    @pytest.fixture
    def mock_phases(self, mock_agents):
        """Create mock research phases for testing."""
        # Define outputs for each phase
        plan_output = {
            "research_questions": ["How effective are attention mechanisms in transformers?"],
            "objectives": ["Evaluate attention performance", "Compare mechanisms"],
            "methodology": ["Literature review", "Experiments", "Analysis"],
            "experiments": ["Test on language tasks", "Test on vision tasks"],
            "evaluation_metrics": ["Accuracy", "Efficiency"]
        }
        
        literature_output = {
            "papers": [{"title": "Paper 1", "authors": ["Author A"], "abstract": "Abstract 1"}],
            "key_insights": ["Insight 1", "Insight 2"],
            "methodologies": ["Method A", "Method B"],
            "research_gaps": ["Gap X", "Gap Y"],
            "synthesis": "Literature Review Summary"
        }
        
        experiments_output = {
            "experiments": ["Experiment 1", "Experiment 2"],
            "model_implementations": {"model_code": "def create_model(): pass"},
            "experiment_results": {
                "results": "Experiment results",
                "analysis": "The model achieved 92% accuracy."
            }
        }
        
        report_output = {
            "title": "Research Report: Attention Mechanisms in Transformers",
            "abstract": "This research investigates attention mechanisms...",
            "sections": {
                "introduction": "Introduction content...",
                "methodology": "Methodology content...",
                "results": "Results content...",
                "discussion": "Discussion content..."
            },
            "final_report": "Complete report content..."
        }
        
        # Create mock phase objects
        phases = {
            "plan_formulation": MagicMock(spec=PlanFormulation),
            "literature_review": MagicMock(spec=LiteratureReview),
            "running_experiments": MagicMock(spec=RunningExperiments),
            "report_writing": MagicMock(spec=ReportWriting)
        }
        
        # Configure mock behaviors
        phases["plan_formulation"].execute = MagicMock(return_value=plan_output)
        phases["literature_review"].execute = MagicMock(return_value=literature_output)
        phases["running_experiments"].execute = MagicMock(return_value=experiments_output)
        phases["report_writing"].execute = MagicMock(return_value=report_output)
        
        return phases
    
    @pytest.fixture
    def mock_laboratory(self, mock_agents, mock_phases):
        """Create a mock AILaboratory instance."""
        lab = MagicMock()
        lab.professor_agent = mock_agents["professor"]
        lab.phd_student_agent = mock_agents["phd_student"]
        lab.ml_engineer_agent = mock_agents["ml_engineer"]
        lab.reviewers_agent = mock_agents["reviewers"]
        
        # Configure laboratory methods
        lab.perform_research = MagicMock(return_value={
            "research_plan": mock_phases["plan_formulation"].execute(),
            "literature_review": mock_phases["literature_review"].execute(),
            "experiments": mock_phases["running_experiments"].execute(),
            "report": mock_phases["report_writing"].execute()
        })
        
        return lab
    
    @patch('ai_lab_repo.AILaboratory')
    def test_full_research_workflow(self, MockAILaboratory, mock_laboratory):
        """Test the full research workflow from start to finish."""
        # Configure the mock
        MockAILaboratory.return_value = mock_laboratory
        
        # Mock command line arguments
        with patch('sys.argv', ['ai_lab_repo.py', 
                               '--api-key', 'test_key',
                               '--llm-backend', 'gpt-4o',
                               '--research-topic', 'Attention Mechanisms in Transformers',
                               '--compile-latex', 'false']):
            
            # Run the main function with redirected stdout
            with patch('builtins.print'):
                ai_lab_repo.main()
            
            # Verify the laboratory was initialized and research was performed
            MockAILaboratory.assert_called_once()
            mock_laboratory.set_model.assert_called_once_with('gpt-4o')
            mock_laboratory.perform_research.assert_called_once()
            
            # Get the results from perform_research
            results = mock_laboratory.perform_research.return_value
            
            # Verify the results contain all expected components
            assert "research_plan" in results
            assert "literature_review" in results
            assert "experiments" in results
            assert "report" in results
            
            # Verify the contents of each component
            assert "research_questions" in results["research_plan"]
            assert "papers" in results["literature_review"]
            assert "experiment_results" in results["experiments"]
            assert "final_report" in results["report"]
    
    @patch('ai_lab_repo.AILaboratory')
    def test_copilot_mode_workflow(self, MockAILaboratory, mock_laboratory):
        """Test the research workflow with copilot mode enabled."""
        # Configure the mock
        MockAILaboratory.return_value = mock_laboratory
        
        # Mock command line arguments with copilot mode enabled
        with patch('sys.argv', ['ai_lab_repo.py', 
                               '--api-key', 'test_key',
                               '--llm-backend', 'gpt-4o',
                               '--research-topic', 'Attention Mechanisms in Transformers',
                               '--copilot-mode', 'true',
                               '--compile-latex', 'false']):
            
            # Run the main function with redirected stdout
            with patch('builtins.print'):
                ai_lab_repo.main()
            
            # Verify the laboratory was initialized and research was performed with human_in_loop=True
            MockAILaboratory.assert_called_once()
            mock_laboratory.perform_research.assert_called_once_with(
                research_topic="Attention Mechanisms in Transformers",
                human_in_loop=True,
                save_interval=5,
                save_path='state_saves/checkpoint'
            )
    
    @patch('ai_lab_repo.load_laboratory_state')
    @patch('ai_lab_repo.AILaboratory')
    def test_checkpoint_loading(self, MockAILaboratory, mock_load_state, mock_laboratory):
        """Test loading and continuing from a checkpoint."""
        # Configure the mocks
        MockAILaboratory.return_value = mock_laboratory
        mock_load_state.return_value = {"state": "saved_state_data"}
        
        # Mock command line arguments with checkpoint loading
        with patch('sys.argv', ['ai_lab_repo.py', 
                               '--api-key', 'test_key',
                               '--llm-backend', 'gpt-4o',
                               '--research-topic', 'Attention Mechanisms in Transformers',
                               '--load-existing', 'True',
                               '--load-existing-path', 'state_saves/test_checkpoint',
                               '--compile-latex', 'false']):
            
            # Run the main function with redirected stdout
            with patch('builtins.print'):
                ai_lab_repo.main()
            
            # Verify state was loaded and passed to AILaboratory initialization
            mock_load_state.assert_called_once_with('state_saves/test_checkpoint')
            MockAILaboratory.assert_called_once()
            
            # Check that research continues from the loaded state
            mock_laboratory.perform_research.assert_called_once()
    
    def test_phase_sequence_integrity(self, mock_phases):
        """Test that phases execute in the correct sequence with proper data flow."""
        # Phase outputs
        plan_output = mock_phases["plan_formulation"].execute()
        literature_output = mock_phases["literature_review"].execute()
        experiments_output = mock_phases["running_experiments"].execute()
        report_output = mock_phases["report_writing"].execute()
        
        # Verify data dependencies between phases are maintained
        assert "research_questions" in plan_output, "Plan must produce research questions"
        assert "papers" in literature_output, "Literature review must produce papers"
        assert "experiment_results" in experiments_output, "Experiments must produce results"
        assert "final_report" in report_output, "Report writing must produce a final report"
        
        # Validate that all phases have the expected structure
        assert len(plan_output["research_questions"]) > 0, "Research questions should not be empty"
        assert len(literature_output["papers"]) > 0, "Literature review should include papers"
        assert "analysis" in experiments_output["experiment_results"], "Experiments should include analysis"
        assert len(report_output["sections"]) >= 4, "Report should contain at least 4 sections"
        
        # Verify that key information from earlier phases appears in the final report
        report_content = report_output["final_report"].lower()
        assert "attention mechanisms" in report_content, "Report should mention key research topic"
        assert "accuracy" in report_content, "Report should mention key results"