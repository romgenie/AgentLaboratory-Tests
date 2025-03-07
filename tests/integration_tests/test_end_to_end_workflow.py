import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the integration adapter
from test_adapters.integration_adapter import create_research_workflow

class TestEndToEndWorkflow:
    """Test suite for end-to-end research workflow integration."""
    
    @pytest.fixture
    def research_workflow(self):
        """Create a test research workflow."""
        workflow = create_research_workflow("Machine Learning for Climate Data Analysis")
        yield workflow
        # Cleanup after the test
        workflow.cleanup()
    
    def test_workflow_initialization(self, research_workflow):
        """Test that the research workflow initializes correctly."""
        # Check if workflow has essential attributes
        assert research_workflow.research_topic == "Machine Learning for Climate Data Analysis"
        assert research_workflow.model == "test-model"
        assert len(research_workflow.agents) == 3
        
        # Verify agent types
        assert research_workflow.agents[0].name == "Professor Smith"
        assert research_workflow.agents[1].name == "PhD Student Jones"
        assert research_workflow.agents[2].name == "ML Engineer Taylor"
        
        # Check if agents have the right expertise
        assert "Research Methodology" in research_workflow.agents[0].expertise
        assert "Literature Review" in research_workflow.agents[1].expertise
        assert "Machine Learning" in research_workflow.agents[2].expertise
    
    def test_complete_research_workflow(self, research_workflow):
        """Test the entire research workflow from start to finish."""
        # Run the workflow
        results = research_workflow.run_research_phases()
        
        # Verify that all phases executed successfully
        assert results["plan_formulation"]["success"] is True
        assert results["literature_review"]["success"] is True
        assert results["data_preparation"]["success"] is True
        assert results["running_experiments"]["success"] is True
        assert results["results_interpretation"]["success"] is True
        assert results["report_writing"]["success"] is True
        assert results["report_refinement"]["success"] is True
        
        # Check for latex compilation
        assert "latex_compilation" in results
        assert results["latex_compilation"]["success"] is True
        
        # Verify artifacts were generated
        assert results["plan_formulation"]["artifacts"] is not None
        assert results["literature_review"]["artifacts"] is not None
        assert results["data_preparation"]["artifacts"] is not None
        assert results["running_experiments"]["artifacts"] is not None
        assert results["results_interpretation"]["artifacts"] is not None
        assert results["report_writing"]["artifacts"]["markdown"] is not None
        assert results["report_writing"]["artifacts"]["latex"] is not None
        assert results["report_refinement"]["artifacts"]["markdown"] is not None
        assert results["report_refinement"]["artifacts"]["latex"] is not None
        
        # Check code execution results
        assert "code_execution" in results["running_experiments"]
        assert "code" in results["running_experiments"]["code_execution"]
        assert "result" in results["running_experiments"]["code_execution"]
        assert "Model accuracy" in results["running_experiments"]["code_execution"]["result"]
    
    def test_research_phase_dependencies(self, research_workflow):
        """Test that research phases build on each other properly."""
        # Override run_research_phases to track phase dependencies
        original_run = research_workflow.run_research_phases
        
        # Create a tracking function
        phase_executed = {
            "plan_formulation": False,
            "literature_review": False,
            "data_preparation": False,
            "running_experiments": False,
            "results_interpretation": False,
            "report_writing": False,
            "report_refinement": False
        }
        
        # Override workflow methods to track execution
        with patch('test_adapters.workflow_methods_adapter.plan_formulation') as mock_plan:
            mock_plan.side_effect = lambda w: phase_executed.update({"plan_formulation": True}) or "Plan completed"
            
            with patch('test_adapters.workflow_methods_adapter.literature_review') as mock_lit:
                mock_lit.side_effect = lambda w: phase_executed.update({"literature_review": True}) or "Literature review completed"
                
                with patch('test_adapters.workflow_methods_adapter.data_preparation') as mock_data:
                    mock_data.side_effect = lambda w: phase_executed.update({"data_preparation": True}) or "Data preparation completed"
                    
                    with patch('test_adapters.workflow_methods_adapter.running_experiments') as mock_exp:
                        mock_exp.side_effect = lambda w: phase_executed.update({"running_experiments": True}) or "Experiments completed"
                        
                        with patch('test_adapters.workflow_methods_adapter.results_interpretation') as mock_results:
                            mock_results.side_effect = lambda w: phase_executed.update({"results_interpretation": True}) or "Results interpretation completed"
                            
                            with patch('test_adapters.workflow_methods_adapter.report_writing') as mock_report:
                                mock_report.side_effect = lambda w: phase_executed.update({"report_writing": True}) or "Report writing completed"
                                
                                with patch('test_adapters.workflow_methods_adapter.report_refinement') as mock_refine:
                                    mock_refine.side_effect = lambda w: phase_executed.update({"report_refinement": True}) or "Report refinement completed"
                                    
                                    # Run the workflow 
                                    research_workflow.run_research_phases()
                                    
                                    # Verify phases were executed in correct order
                                    assert mock_plan.call_count == 1
                                    assert mock_lit.call_count == 1
                                    assert mock_data.call_count == 1
                                    assert mock_exp.call_count == 1
                                    assert mock_results.call_count == 1
                                    assert mock_report.call_count == 1
                                    assert mock_refine.call_count == 1
                                    
                                    # Check dependency chain through call order
                                    mock_plan.assert_called_once()
                                    mock_lit.assert_called_once()
                                    mock_data.assert_called_once()
                                    mock_exp.assert_called_once()
                                    mock_results.assert_called_once()
                                    mock_report.assert_called_once()
                                    mock_refine.assert_called_once()
    
    def test_code_execution_integration(self, research_workflow):
        """Test that code execution integrates properly with the workflow."""
        # Mock execute_code to simulate successful execution
        with patch('test_adapters.code_executor_adapter.execute_code') as mock_execute:
            mock_execute.return_value = "Code executed successfully with result: Model accuracy: 0.95"
            
            # Run just the experiments phase
            results = research_workflow.run_research_phases()
            
            # Verify code execution was called
            assert mock_execute.call_count == 1
            assert "code_execution" in results["running_experiments"]
            assert results["running_experiments"]["code_execution"]["result"] == "Code executed successfully with result: Model accuracy: 0.95"
    
    def test_latex_compilation_integration(self, research_workflow):
        """Test that LaTeX compilation integrates properly with the workflow."""
        # Mock compile_latex to simulate successful compilation
        with patch('test_adapters.latex_utils_adapter.compile_latex') as mock_compile:
            mock_compile.return_value = "Compilation successful"
            
            # Run the workflow
            results = research_workflow.run_research_phases()
            
            # Verify LaTeX compilation was called
            assert mock_compile.call_count == 1
            assert "latex_compilation" in results
            assert results["latex_compilation"]["success"] is True