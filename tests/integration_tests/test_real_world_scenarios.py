import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import components for testing
from ai_lab_repo import AgentLabRepository
from agents.professor_agent import ProfessorAgent
from agents.phd_student_agent import PhDStudentAgent
from agents.sw_engineer_agent import SWEngineerAgent
from agents.ml_engineer_agent import MLEngineerAgent
from agents_phases.literature_review import LiteratureReview
from agents_phases.plan_formulation import PlanFormulation
from agents_phases.running_experiments import RunningExperiments
from agents_phases.report_writing import ReportWriting


class TestRealWorldScenarios:
    """Test suite for real-world research scenarios."""
    
    @pytest.fixture
    def test_research_environment(self):
        """Set up a test research environment with temp directories."""
        # Create temp directory for research outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            research_dir = os.path.join(temp_dir, "research_output")
            os.makedirs(research_dir, exist_ok=True)
            
            # Return temp directories
            yield {
                "base_dir": temp_dir,
                "research_dir": research_dir
            }
    
    @pytest.fixture
    def mock_api_calls(self):
        """Mock all API calls to external services."""
        patches = []
        
        # Mock ArXiv search
        arxiv_patch = patch('agents_tools.arxiv_search.search_arxiv')
        mock_arxiv = arxiv_patch.start()
        mock_arxiv.return_value = [{
            'id': '2304.12345',
            'title': 'Deep Learning for Time Series Forecasting: A Comprehensive Review',
            'authors': ['Jane Smith', 'John Doe'],
            'summary': 'This paper reviews recent advances in deep learning for time series forecasting.',
            'published': '2023-04-15'
        }]
        patches.append(arxiv_patch)
        
        # Mock Semantic Scholar search
        semantic_patch = patch('agents_tools.semantic_scholar_search.search_semantic_scholar')
        mock_semantic = semantic_patch.start()
        mock_semantic.return_value = [{
            'paperId': 'abc123',
            'title': 'Transformer-based Models for Time Series Analysis',
            'authors': [{'name': 'Alice Johnson'}, {'name': 'Bob Williams'}],
            'abstract': 'We present a novel transformer architecture for time series forecasting.',
            'year': 2022,
            'citationCount': 125
        }]
        patches.append(semantic_patch)
        
        # Mock code execution
        code_exec_patch = patch('agents_tools.code_executor.execute_code')
        mock_code_exec = code_exec_patch.start()
        mock_code_exec.return_value = {
            'output': 'Model training complete. Test accuracy: 0.92',
            'error': None,
            'figures': ['figure1.png', 'figure2.png']
        }
        patches.append(code_exec_patch)
        
        # Mock the LLM API calls
        query_patch = patch('inference.query_model.query_model')
        mock_query = query_patch.start()
        
        # Different responses based on context
        def mock_query_response(model_str, prompt, system_prompt=None, **kwargs):
            if 'literature review' in prompt.lower():
                return "Based on the reviewed papers, transformer-based models show promising results for time series forecasting."
            elif 'plan' in prompt.lower():
                return "Research Plan:\n1. Implement baseline LSTM model\n2. Implement transformer model\n3. Compare results on benchmark datasets"
            elif 'experiment' in prompt.lower():
                return "Experiment Results:\nThe transformer model achieved 92% accuracy, outperforming the LSTM baseline (87%)."
            elif 'report' in prompt.lower() or 'write' in prompt.lower():
                return "# Research Report\n\n## Introduction\nTime series forecasting is essential in many domains.\n\n## Methodology\nWe implemented both LSTM and transformer models.\n\n## Results\nThe transformer model outperformed the LSTM baseline."
            else:
                return "I've analyzed the information and have some insights to share."
        
        mock_query.side_effect = mock_query_response
        patches.append(query_patch)
        
        yield {
            "arxiv": mock_arxiv,
            "semantic_scholar": mock_semantic,
            "code_executor": mock_code_exec,
            "llm_api": mock_query
        }
        
        # Stop all patches
        for p in patches:
            p.stop()
    
    @pytest.fixture
    def repository_config(self):
        """Provide configuration for the agent laboratory."""
        return {
            "api_key": "fake-api-key",
            "llm_backend": "gpt-4o",
            "research_topic": "Time Series Forecasting with Transformer Models",
            "copilot_mode": False,
            "compile_latex": False,
            "verbose": True
        }
    
    @pytest.mark.parametrize("research_topic", [
        "Time Series Forecasting with Transformer Models",
        "Optimizing Transformer Models for Edge Devices",
        "Knowledge Distillation in Large Language Models"
    ])
    def test_end_to_end_research_workflow(self, research_topic, test_research_environment, mock_api_calls, repository_config):
        """Test complete research workflow with different research topics."""
        # Update config with parametrized research topic
        config = repository_config.copy()
        config["research_topic"] = research_topic
        
        # Initialize repository with mocks and temp directories
        with patch('os.makedirs'), patch('os.path.exists', return_value=True):
            repository = AgentLabRepository(
                api_key=config["api_key"],
                llm_backend=config["llm_backend"],
                research_topic=config["research_topic"],
                research_dir=test_research_environment["research_dir"],
                copilot_mode=config["copilot_mode"],
                compile_latex=config["compile_latex"],
                verbose=config["verbose"]
            )
            
            # Execute each phase with mocked components
            with patch.object(repository, 'literature_review') as mock_lit_review, \
                 patch.object(repository, 'plan_formulation') as mock_plan, \
                 patch.object(repository, 'running_experiments') as mock_experiments, \
                 patch.object(repository, 'report_writing') as mock_report:
                
                # Configure mocks to simulate successful completion
                mock_lit_review.return_value = True
                mock_plan.return_value = True
                mock_experiments.return_value = True
                mock_report.return_value = True
                
                # Run the research workflow
                result = repository.run_research()
                
                # Verify all phases were executed
                assert mock_lit_review.called
                assert mock_plan.called
                assert mock_experiments.called
                assert mock_report.called
                
                # Verify successful completion
                assert result is True
    
    def test_literature_review_phase(self, test_research_environment, mock_api_calls, repository_config):
        """Test the literature review phase with simulated papers."""
        # Initialize literature review phase
        professor = ProfessorAgent(
            name="Professor Roberts",
            expertise=["Machine Learning", "Time Series Analysis"],
            personality_traits=["analytical", "thorough"],
            model=repository_config["llm_backend"]
        )
        
        phd_student = PhDStudentAgent(
            name="PhD Student Chen",
            expertise=["Deep Learning", "Research Methods"],
            personality_traits=["detail-oriented", "curious"],
            model=repository_config["llm_backend"]
        )
        
        lit_review = LiteratureReview(
            professor_agent=professor,
            phd_student_agent=phd_student,
            research_topic=repository_config["research_topic"],
            research_dir=test_research_environment["research_dir"]
        )
        
        # Execute literature review with mocked API calls
        with patch.object(lit_review, 'search_literature') as mock_search, \
             patch.object(lit_review, 'analyze_papers') as mock_analyze, \
             patch.object(lit_review, 'synthesize_findings') as mock_synthesize:
            
            # Configure mocks
            mock_search.return_value = [
                {"title": "Paper 1", "authors": ["Author A"], "abstract": "Abstract 1"},
                {"title": "Paper 2", "authors": ["Author B"], "abstract": "Abstract 2"}
            ]
            mock_analyze.return_value = {
                "key_insights": ["Insight 1", "Insight 2"],
                "methodologies": ["Method A", "Method B"],
                "research_gaps": ["Gap X", "Gap Y"]
            }
            mock_synthesize.return_value = "Literature Review Report: We found several important insights..."
            
            # Run the phase
            result = lit_review.execute()
            
            # Verify all steps were executed
            assert mock_search.called
            assert mock_analyze.called
            assert mock_synthesize.called
            
            # Verify result contains expected sections
            assert result["key_insights"] is not None
            assert result["methodologies"] is not None
            assert result["research_gaps"] is not None
            
            # Verify output file was generated (mocked)
            with patch('builtins.open', create=True), \
                 patch('json.dump'):
                lit_review.save_results(result)
    
    def test_running_experiments_phase(self, test_research_environment, mock_api_calls, repository_config):
        """Test the experiment running phase with simulated code execution."""
        # Initialize agents
        sw_engineer = SWEngineerAgent(
            name="SW Engineer Taylor",
            expertise=["Software Engineering", "Python", "TensorFlow"],
            personality_traits=["systematic", "detail-oriented"],
            model=repository_config["llm_backend"]
        )
        
        ml_engineer = MLEngineerAgent(
            name="ML Engineer Rivera",
            expertise=["Machine Learning", "Neural Networks", "Optimization"],
            personality_traits=["creative", "analytical"],
            model=repository_config["llm_backend"]
        )
        
        # Simulate plan from previous phase
        research_plan = {
            "objectives": ["Implement and compare transformer models for time series forecasting"],
            "methodology": ["Implement baseline", "Implement transformer", "Compare results"],
            "experiments": ["Experiment 1: LSTM baseline", "Experiment 2: Transformer model"],
            "evaluation_metrics": ["Accuracy", "RMSE", "Training time"]
        }
        
        # Initialize experiments phase
        experiments = RunningExperiments(
            sw_engineer_agent=sw_engineer,
            ml_engineer_agent=ml_engineer,
            research_topic=repository_config["research_topic"],
            research_plan=research_plan,
            research_dir=test_research_environment["research_dir"]
        )
        
        # Execute experiments with mocked code execution
        with patch.object(experiments, 'design_experiments') as mock_design, \
             patch.object(experiments, 'implement_code') as mock_implement, \
             patch.object(experiments, 'execute_experiments') as mock_execute, \
             patch.object(experiments, 'analyze_results') as mock_analyze:
            
            # Configure mocks
            mock_design.return_value = ["Experiment setup 1", "Experiment setup 2"]
            mock_implement.return_value = "# Code implementation\nimport tensorflow as tf\n# Model implementation"
            mock_execute.return_value = {
                "experiment1": {"accuracy": 0.87, "rmse": 0.12},
                "experiment2": {"accuracy": 0.92, "rmse": 0.08}
            }
            mock_analyze.return_value = "The transformer model outperformed the LSTM baseline."
            
            # Run the phase
            result = experiments.execute()
            
            # Verify all steps were executed
            assert mock_design.called
            assert mock_implement.called
            assert mock_execute.called
            assert mock_analyze.called
            
            # Verify result contains expected sections
            assert "code" in result
            assert "results" in result
            assert "analysis" in result
            
            # Verify output files were generated (mocked)
            with patch('builtins.open', create=True), \
                 patch('json.dump'):
                experiments.save_results(result)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])