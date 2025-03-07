#!/usr/bin/env python3
"""
Adapter for Laboratory Workflow Methods.

This module provides adapter implementations for the laboratory workflow methods
to facilitate testing without modifying the original code.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import os
import sys
import json
import datetime
from unittest.mock import MagicMock

# Import laboratory adapter for agent classes
from test_adapters.laboratory_adapter import (
    BaseAgentAdapter,
    ProfessorAgentAdapter,
    PhDStudentAgentAdapter,
    MLEngineerAgentAdapter
)

class WorkflowMethodsAdapter:
    """
    Base adapter class for laboratory workflow methods.
    Provides common utilities used across workflow method modules.
    """
    
    @staticmethod
    def create_agent(agent_type, **kwargs):
        """Create an agent of the specified type for testing."""
        if agent_type.lower() == 'professor':
            return ProfessorAgentAdapter(**kwargs)
        elif agent_type.lower() == 'phd':
            return PhDStudentAgentAdapter(**kwargs)
        elif agent_type.lower() == 'ml':
            return MLEngineerAgentAdapter(**kwargs)
        else:
            return BaseAgentAdapter(**kwargs)
            
    @staticmethod
    def save_output(content, filename, directory="research_dir"):
        """Save content to a file in the specified directory."""
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save the content
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath
        
    @staticmethod
    def load_data(filepath):
        """Load data from a file."""
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.endswith('.json'):
                return json.load(f)
            else:
                return f.read()


# Adapter implementations for workflow methods
class SetModelAdapter:
    """Adapter for the set_model workflow method."""
    
    @staticmethod
    def set_model(workflow, model_name):
        """Set the model to use for the workflow."""
        workflow.model = model_name
        workflow.llm_backend = model_name
        
        # Update model for all agents
        for agent in workflow.agents:
            agent.model = model_name
            
        return f"Model set to {model_name} for workflow and all agents."


class SaveStateAdapter:
    """Adapter for the save_state workflow method."""
    
    @staticmethod
    def save_state(workflow, save_dir="state_saves", filename=None):
        """Save the current state of the workflow."""
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_slug = workflow.research_topic.lower().replace(" ", "_")[:20]
            filename = f"{topic_slug}_{timestamp}.json"
        
        # For mock objects, make sure we have all required attributes with default values
        # Handle the case where MagicMock objects might not have the expected attributes
        agents_data = []
        for agent in workflow.agents:
            agent_dict = {"name": getattr(agent, "name", "Unknown"), "expertise": []}
            if hasattr(agent, "expertise"):
                # Handle the case where expertise might not be a list
                expertise = agent.expertise
                if not isinstance(expertise, list):
                    expertise = [str(expertise)]
                agent_dict["expertise"] = expertise
            agents_data.append(agent_dict)
            
        # Create a state dictionary
        state = {
            "research_topic": workflow.research_topic,
            "model": getattr(workflow, "model", "unknown-model"),
            "timestamp": datetime.datetime.now().isoformat(),
            "agents": agents_data,
            "progress": getattr(workflow, "progress", {}),
            "results": getattr(workflow, "results", {})
        }
        
        # Save the state
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            
        return filepath


class SetAgentAttrAdapter:
    """Adapter for the set_agent_attr workflow method."""
    
    @staticmethod
    def set_agent_attr(workflow, agent_name, attr_name, attr_value):
        """Set an attribute on an agent in the workflow."""
        # Find the agent
        agent = None
        for a in workflow.agents:
            if a.name == agent_name:
                agent = a
                break
                
        if agent is None:
            return f"Agent {agent_name} not found."
            
        # Set the attribute
        setattr(agent, attr_name, attr_value)
        return f"Set {attr_name}={attr_value} on agent {agent_name}."


class ResetAgentsAdapter:
    """Adapter for the reset_agents workflow method."""
    
    @staticmethod
    def reset_agents(workflow):
        """Reset all agents in the workflow."""
        # For testing purposes, we'll just reset the modified attributes
        # instead of creating new agent instances
        
        # In a real implementation we would create new agent instances,
        # but for testing we'll modify the mock objects directly
        for agent in workflow.agents:
            # Reset agent attributes to their original values
            if hasattr(agent, 'original_name'):
                agent.name = agent.original_name
            if hasattr(agent, 'original_expertise'):
                agent.expertise = agent.original_expertise
            if hasattr(agent, 'original_personality_traits'):
                agent.personality_traits = agent.original_personality_traits
            
            # Store original values for future resets
            if not hasattr(agent, 'original_name'):
                agent.original_name = agent.name
            if not hasattr(agent, 'original_expertise'):
                agent.original_expertise = agent.expertise
            if not hasattr(agent, 'original_personality_traits'):
                agent.personality_traits = agent.personality_traits
            
        return "All agents have been reset to their initial state."


class PerformResearchAdapter:
    """Adapter for the perform_research workflow method."""
    
    @staticmethod
    def perform_research(workflow, topic=None):
        """Execute the full research workflow on a topic."""
        if topic:
            workflow.research_topic = topic
            
        # Execute research phases in sequence
        workflow.plan_formulation()
        workflow.literature_review()
        workflow.data_preparation()
        workflow.running_experiments()
        workflow.results_interpretation()
        workflow.report_writing()
        workflow.report_refinement()
        
        return f"Research completed on topic: {workflow.research_topic}"


class PlanFormulationAdapter:
    """Adapter for the plan_formulation workflow method."""
    
    @staticmethod
    def plan_formulation(workflow):
        """Execute the plan formulation phase."""
        # Get the professor agent
        professor = None
        for agent in workflow.agents:
            if isinstance(agent, ProfessorAgentAdapter):
                professor = agent
                break
                
        if professor is None:
            return "Plan formulation failed: No professor agent found."
            
        # Generate a research plan
        plan = f"# Research Plan for: {workflow.research_topic}\n\n"
        plan += "## Research Questions\n"
        plan += "1. What are the key factors affecting this research area?\n"
        plan += "2. How can we improve existing approaches?\n\n"
        plan += "## Methodology\n"
        plan += "- Literature review of key papers\n"
        plan += "- Data collection and preparation\n"
        plan += "- Model development and experimentation\n"
        plan += "- Analysis and interpretation of results\n\n"
        
        # Save the plan
        workflow.research_plan = plan
        WorkflowMethodsAdapter.save_output(plan, "research_plan.md")
        
        workflow.progress = {"plan_formulation": True}
        return "Plan formulation completed successfully."


class LiteratureReviewAdapter:
    """Adapter for the literature_review workflow method."""
    
    @staticmethod
    def literature_review(workflow):
        """Execute the literature review phase."""
        # Get the PhD student agent
        phd_student = None
        for agent in workflow.agents:
            if isinstance(agent, PhDStudentAgentAdapter):
                phd_student = agent
                break
                
        if phd_student is None:
            return "Literature review failed: No PhD student agent found."
            
        # Generate a literature review
        review = f"# Literature Review for: {workflow.research_topic}\n\n"
        review += "## Key Papers\n\n"
        review += "### Paper 1: Important Research in the Field\n"
        review += "This paper established the foundational concepts used in the field.\n\n"
        review += "### Paper 2: Recent Advances\n"
        review += "This recent paper demonstrates significant improvements in methodology.\n\n"
        review += "## Summary of Findings\n"
        review += "The literature suggests several promising directions for further research.\n"
        
        # Save the review
        workflow.literature_review = review
        WorkflowMethodsAdapter.save_output(review, "literature_review.md")
        
        workflow.progress = {**workflow.progress, "literature_review": True}
        return "Literature review completed successfully."


class DataPreparationAdapter:
    """Adapter for the data_preparation workflow method."""
    
    @staticmethod
    def data_preparation(workflow):
        """Execute the data preparation phase."""
        # Get the ML engineer agent
        ml_engineer = None
        for agent in workflow.agents:
            if isinstance(agent, MLEngineerAgentAdapter):
                ml_engineer = agent
                break
                
        if ml_engineer is None:
            return "Data preparation failed: No ML engineer agent found."
            
        # Generate a data preparation report
        report = f"# Data Preparation for: {workflow.research_topic}\n\n"
        report += "## Dataset Description\n"
        report += "Sample dataset with 1000 records and 10 features.\n\n"
        report += "## Preprocessing Steps\n"
        report += "1. Data cleaning\n"
        report += "2. Feature normalization\n"
        report += "3. Train/test split\n\n"
        report += "## Final Dataset Statistics\n"
        report += "Training set: 800 samples\n"
        report += "Testing set: 200 samples\n"
        
        # Save the report
        workflow.data_preparation = report
        WorkflowMethodsAdapter.save_output(report, "data_preparation.md")
        
        workflow.progress = {**workflow.progress, "data_preparation": True}
        return "Data preparation completed successfully."


class RunningExperimentsAdapter:
    """Adapter for the running_experiments workflow method."""
    
    @staticmethod
    def running_experiments(workflow):
        """Execute the experiments phase."""
        # Get the ML engineer agent
        ml_engineer = None
        for agent in workflow.agents:
            if isinstance(agent, MLEngineerAgentAdapter):
                ml_engineer = agent
                break
                
        if ml_engineer is None:
            return "Experiments failed: No ML engineer agent found."
            
        # Generate an experiments report
        report = f"# Experiments for: {workflow.research_topic}\n\n"
        report += "## Experimental Setup\n"
        report += "Models tested: Random Forest, Neural Network, XGBoost\n\n"
        report += "## Results\n"
        report += "| Model | Accuracy | F1 Score |\n"
        report += "| ----- | -------- | -------- |\n"
        report += "| Random Forest | 0.85 | 0.84 |\n"
        report += "| Neural Network | 0.88 | 0.87 |\n"
        report += "| XGBoost | 0.89 | 0.88 |\n\n"
        report += "## Analysis\n"
        report += "XGBoost performed best across all metrics.\n"
        
        # Save the report
        workflow.experiments = report
        WorkflowMethodsAdapter.save_output(report, "experiments.md")
        
        workflow.progress = {**workflow.progress, "running_experiments": True}
        return "Experiments completed successfully."


class ResultsInterpretationAdapter:
    """Adapter for the results_interpretation workflow method."""
    
    @staticmethod
    def results_interpretation(workflow):
        """Execute the results interpretation phase."""
        # Get the PhD student agent
        phd_student = None
        for agent in workflow.agents:
            if isinstance(agent, PhDStudentAgentAdapter):
                phd_student = agent
                break
                
        if phd_student is None:
            return "Results interpretation failed: No PhD student agent found."
            
        # Generate a results interpretation report
        report = f"# Results Interpretation for: {workflow.research_topic}\n\n"
        report += "## Key Findings\n"
        report += "1. XGBoost outperformed other models with 89% accuracy\n"
        report += "2. Feature importance analysis revealed key factors\n\n"
        report += "## Implications\n"
        report += "These results suggest that tree-based ensemble methods are most effective for this problem.\n\n"
        report += "## Limitations\n"
        report += "The dataset size was limited, and results might not generalize to all scenarios.\n"
        
        # Save the report
        workflow.results = report
        WorkflowMethodsAdapter.save_output(report, "results_interpretation.md")
        
        workflow.progress = {**workflow.progress, "results_interpretation": True}
        return "Results interpretation completed successfully."


class ReportWritingAdapter:
    """Adapter for the report_writing workflow method."""
    
    @staticmethod
    def report_writing(workflow):
        """Execute the report writing phase."""
        # Get all agents
        agents = workflow.agents
                
        # Generate a report
        report = f"# Research Report: {workflow.research_topic}\n\n"
        report += "## Abstract\n"
        report += "This research explores novel approaches to the problem domain.\n\n"
        report += "## Introduction\n"
        report += "The research topic addresses significant challenges in the field.\n\n"
        report += "## Methodology\n"
        report += "We employed a systematic approach to data collection and analysis.\n\n"
        report += "## Results\n"
        report += "Our experiments demonstrated significant improvements over baseline methods.\n\n"
        report += "## Discussion\n"
        report += "The findings have important implications for theory and practice.\n\n"
        report += "## Conclusion\n"
        report += "This research contributes valuable insights to the field.\n\n"
        
        # Create LaTeX version
        latex_report = f"""\\documentclass{{article}}
\\title{{Research Report: {workflow.research_topic}}}
\\author{{Research Team}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\section{{Abstract}}
This research explores novel approaches to the problem domain.

\\section{{Introduction}}
The research topic addresses significant challenges in the field.

\\section{{Methodology}}
We employed a systematic approach to data collection and analysis.

\\section{{Results}}
Our experiments demonstrated significant improvements over baseline methods.

\\section{{Discussion}}
The findings have important implications for theory and practice.

\\section{{Conclusion}}
This research contributes valuable insights to the field.

\\end{{document}}
"""
        
        # Save the reports
        workflow.report = report
        workflow.latex_report = latex_report
        WorkflowMethodsAdapter.save_output(report, "research_report.md")
        WorkflowMethodsAdapter.save_output(latex_report, "research_report.tex")
        
        workflow.progress = {**workflow.progress, "report_writing": True}
        return "Report writing completed successfully."


class ReportRefinementAdapter:
    """Adapter for the report_refinement workflow method."""
    
    @staticmethod
    def report_refinement(workflow):
        """Execute the report refinement phase."""
        # Get the professor agent
        professor = None
        for agent in workflow.agents:
            if isinstance(agent, ProfessorAgentAdapter):
                professor = agent
                break
                
        if professor is None:
            return "Report refinement failed: No professor agent found."
            
        # Ensure report exists
        if not hasattr(workflow, 'report') or not workflow.report:
            return "Report refinement failed: No report to refine."
            
        # "Refine" the report
        workflow.report += "\n\n## Acknowledgments\n"
        workflow.report += "This research was supported by the research team.\n"
        
        # Update LaTeX version
        if hasattr(workflow, 'latex_report') and workflow.latex_report:
            workflow.latex_report = workflow.latex_report.replace(
                r"\end{document}",
                r"\section{Acknowledgments}" + "\nThis research was supported by the research team.\n\n" + r"\end{document}"
            )
        
        # Save the refined reports
        WorkflowMethodsAdapter.save_output(workflow.report, "research_report_refined.md")
        if hasattr(workflow, 'latex_report') and workflow.latex_report:
            WorkflowMethodsAdapter.save_output(workflow.latex_report, "research_report_refined.tex")
        
        workflow.progress = {**workflow.progress, "report_refinement": True}
        return "Report refinement completed successfully."


class HumanInLoopAdapter:
    """Adapter for the human_in_loop workflow method."""
    
    @staticmethod
    def human_in_loop(workflow, phase, message=None, input_func=None):
        """
        Simulate human-in-the-loop interaction for testing.
        
        Args:
            workflow: The workflow instance
            phase: The current research phase
            message: Optional message to display
            input_func: Function for getting user input (for mocking)
            
        Returns:
            str: Simulated human feedback
        """
        # Use provided input function or create a mock one
        if input_func is None:
            input_func = lambda _: "proceed"  # Default mock response
            
        # Format message if provided
        display_message = message if message else f"Human-in-loop for phase: {phase}"
        
        # Get "user" input
        user_input = input_func(display_message)
        
        # Process the input
        if user_input.lower() in ["proceed", "continue", "yes", "y"]:
            workflow.progress = {**workflow.progress, f"human_approval_{phase}": True}
            return f"Human approved phase: {phase}"
        elif user_input.lower() in ["modify", "change", "edit"]:
            return f"Human requested modifications to phase: {phase}"
        else:
            return f"Human provided feedback: {user_input}"


# Export the adapter classes as module-level functions
def set_model(workflow, model_name):
    return SetModelAdapter.set_model(workflow, model_name)

def save_state(workflow, save_dir="state_saves", filename=None):
    return SaveStateAdapter.save_state(workflow, save_dir, filename)

def set_agent_attr(workflow, agent_name, attr_name, attr_value):
    return SetAgentAttrAdapter.set_agent_attr(workflow, agent_name, attr_name, attr_value)

def reset_agents(workflow):
    return ResetAgentsAdapter.reset_agents(workflow)

def perform_research(workflow, topic=None):
    return PerformResearchAdapter.perform_research(workflow, topic)

def plan_formulation(workflow):
    return PlanFormulationAdapter.plan_formulation(workflow)

def literature_review(workflow):
    return LiteratureReviewAdapter.literature_review(workflow)

def data_preparation(workflow):
    return DataPreparationAdapter.data_preparation(workflow)

def running_experiments(workflow):
    return RunningExperimentsAdapter.running_experiments(workflow)

def results_interpretation(workflow):
    return ResultsInterpretationAdapter.results_interpretation(workflow)

def report_writing(workflow):
    return ReportWritingAdapter.report_writing(workflow)

def report_refinement(workflow):
    return ReportRefinementAdapter.report_refinement(workflow)

def human_in_loop(workflow, phase, message=None, input_func=None):
    return HumanInLoopAdapter.human_in_loop(workflow, phase, message, input_func)