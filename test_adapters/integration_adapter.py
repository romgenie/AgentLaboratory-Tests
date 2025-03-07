#!/usr/bin/env python3
"""
Integration Test Adapter.

This module provides adapter implementations for integration testing,
combining multiple components to test their interactions.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import os
import sys
import json
import tempfile
import datetime

# Import individual component adapters
from test_adapters.laboratory_adapter import (
    BaseAgentAdapter,
    ProfessorAgentAdapter,
    PhDStudentAgentAdapter,
    MLEngineerAgentAdapter
)

from test_adapters.code_executor_adapter import execute_code
from test_adapters.latex_utils_adapter import compile_latex, escape_latex_special_chars
from test_adapters.workflow_methods_adapter import (
    plan_formulation,
    literature_review,
    data_preparation,
    running_experiments,
    results_interpretation,
    report_writing,
    report_refinement
)

class ResearchWorkflowAdapter:
    """
    Adapter for testing end-to-end research workflow integration.
    Combines multiple components to simulate a complete research process.
    """
    
    def __init__(self, research_topic, model_name="test-model"):
        """Initialize the research workflow with necessary components."""
        self.research_topic = research_topic
        self.model = model_name
        self.llm_backend = model_name
        self.progress = {}
        self.results = {}
        self.temp_dir = tempfile.mkdtemp(prefix="research_")
        self.output_files = {}
        
        # Create agents
        self.agents = [
            ProfessorAgentAdapter(name="Professor Smith", 
                                expertise=["Research Methodology", "Theoretical Frameworks"],
                                personality_traits=["analytical", "thorough"],
                                model=model_name),
            PhDStudentAgentAdapter(name="PhD Student Jones", 
                                expertise=["Literature Review", "Data Analysis"],
                                personality_traits=["curious", "detail-oriented"],
                                model=model_name),
            MLEngineerAgentAdapter(name="ML Engineer Taylor", 
                                expertise=["Machine Learning", "Software Engineering"],
                                personality_traits=["practical", "innovative"],
                                model=model_name)
        ]
    
    def run_research_phases(self):
        """Run all research phases in sequence and track results."""
        results = {}
        
        # Phase 1: Plan Formulation
        results["plan_formulation"] = {
            "success": True,
            "result": plan_formulation(self),
            "artifacts": self.get_artifacts("research_plan.md")
        }
        
        # Phase 2: Literature Review
        results["literature_review"] = {
            "success": True,
            "result": literature_review(self),
            "artifacts": self.get_artifacts("literature_review.md")
        }
        
        # Phase 3: Data Preparation
        results["data_preparation"] = {
            "success": True,
            "result": data_preparation(self),
            "artifacts": self.get_artifacts("data_preparation.md")
        }
        
        # Phase 4: Running Experiments
        # Create test code string (but don't execute it)
        test_code = """
# Test code for machine learning research
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Generate synthetic data - this code is not actually executed
X = np.random.rand(100, 10)
y = np.random.randint(0, 2, 100)

# Train a model
model = RandomForestClassifier(n_estimators=10)
model.fit(X[:80], y[:80])

# Evaluate the model
y_pred = model.predict(X[80:])
accuracy = accuracy_score(y[80:], y_pred)
print(f"Model accuracy: {accuracy:.2f}")
"""
        # Mock code execution for testing
        code_result = "Code executed successfully with result: Model accuracy: 0.95"
        self.test_code = test_code
        self.code_result = code_result
        
        results["running_experiments"] = {
            "success": True,
            "result": running_experiments(self),
            "artifacts": self.get_artifacts("experiments.md"),
            "code_execution": {
                "code": test_code,
                "result": code_result
            }
        }
        
        # Phase 5: Results Interpretation
        results["results_interpretation"] = {
            "success": True,
            "result": results_interpretation(self),
            "artifacts": self.get_artifacts("results_interpretation.md")
        }
        
        # Phase 6: Report Writing
        results["report_writing"] = {
            "success": True,
            "result": report_writing(self),
            "artifacts": {
                "markdown": self.get_artifacts("research_report.md"),
                "latex": self.get_artifacts("research_report.tex")
            }
        }
        
        # Phase 7: Report Refinement
        results["report_refinement"] = {
            "success": True,
            "result": report_refinement(self),
            "artifacts": {
                "markdown": self.get_artifacts("research_report_refined.md"),
                "latex": self.get_artifacts("research_report_refined.tex")
            }
        }
        
        # Create a mock LaTeX report for testing
        self.latex_report = "Mock LaTeX report content"
        
        # Mock LaTeX compilation for testing
        latex_result = "Compilation successful"
        results["latex_compilation"] = {
            "success": True,
            "result": latex_result
        }
        
        self.results = results
        return results
    
    def get_artifacts(self, filename):
        """Retrieve research artifacts generated during the workflow."""
        # Create research_dir if it doesn't exist
        os.makedirs("research_dir", exist_ok=True)
        
        filepath = os.path.join("research_dir", filename)
        
        # For tests, create a mock file if it doesn't exist
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Mock content for {filename}")
        
        # Read the file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Store in output_files for retrieval
        self.output_files[filename] = content
        return content
    
    def cleanup(self):
        """Clean up temporary files created during testing."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
        # Also clean research_dir if it was created
        if os.path.exists("research_dir"):
            # Only remove files we created
            for filename in self.output_files.keys():
                filepath = os.path.join("research_dir", filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            # Remove tex subdirectory if it exists and is empty
            tex_dir = os.path.join("research_dir", "tex")
            if os.path.exists(tex_dir) and not os.listdir(tex_dir):
                os.rmdir(tex_dir)
                
            # Remove research_dir if it's empty
            if os.path.exists("research_dir") and not os.listdir("research_dir"):
                os.rmdir("research_dir")

# Create a factory function to simplify creating workflow instances
def create_research_workflow(research_topic, model_name="test-model"):
    """Create a research workflow adapter instance for integration testing."""
    return ResearchWorkflowAdapter(research_topic, model_name)