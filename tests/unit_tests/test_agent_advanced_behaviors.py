import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents import BaseAgent, ProfessorAgent, PhDStudentAgent

# Helper class for advanced behavior testing
class _TestableAgent(BaseAgent):
    """Extended agent for testing advanced behaviors."""
    
    def __init__(self, model="test-model", **kwargs):
        super().__init__(model=model, **kwargs)
        self.reasoning_steps = []
        self.adaptation_events = []
        self.context_window_usage = []
        
    def context(self, phase):
        return "Test context"
        
    def phase_prompt(self, phase):
        return "Test phase prompt"
        
    def role_description(self):
        return "Test role"
        
    def command_descriptions(self, phase):
        return "Test command descriptions"
        
    def example_command(self, phase):
        return "Test example command"
        
    def add_reasoning_step(self, step_description, context_size=0):
        """Record a reasoning step with context window usage."""
        self.reasoning_steps.append(step_description)
        self.context_window_usage.append(context_size)
        
    def adapt_to_input(self, input_data, adaptation_type):
        """Record an adaptation event."""
        self.adaptation_events.append({
            "input": input_data,
            "adaptation_type": adaptation_type
        })
        return f"Adapted to {adaptation_type}"

class TestAdvancedAgentBehaviors:
    """Test suite for advanced agent behaviors."""
    
    @pytest.fixture
    def test_agent(self):
        """Create a testable agent instance."""
        return _TestableAgent(
            model="test-model", 
            notes=[{"phases": ["test_phase"], "note": "Test note"}],
            max_steps=50
        )
    
    def test_complex_reasoning_patterns(self, test_agent):
        """Test an agent's ability to follow complex reasoning patterns."""
        # Simulate a complex reasoning flow
        test_agent.add_reasoning_step("Initial problem analysis", 500)
        test_agent.add_reasoning_step("Identify key variables", 650)
        test_agent.add_reasoning_step("Formulate hypothesis", 800)
        test_agent.add_reasoning_step("Design experiment", 950)
        test_agent.add_reasoning_step("Analyze results", 1100)
        test_agent.add_reasoning_step("Draw conclusions", 1250)
        
        # Verify reasoning flow
        assert len(test_agent.reasoning_steps) == 6
        assert "hypothesis" in test_agent.reasoning_steps[2]
        assert "conclusions" in test_agent.reasoning_steps[5]
        
        # Verify increasing context usage
        assert all(test_agent.context_window_usage[i] < test_agent.context_window_usage[i+1] 
                 for i in range(len(test_agent.context_window_usage)-1))
    
    def test_agent_adaptation(self, test_agent):
        """Test agent adaptation to unexpected inputs."""
        # Test adaptation to different inputs
        test_agent.adapt_to_input("Unclear research question", "clarification")
        test_agent.adapt_to_input("Contradictory experimental results", "reconciliation")
        test_agent.adapt_to_input("New relevant literature", "knowledge_update")
        test_agent.adapt_to_input("Failed code execution", "error_handling")
        
        # Verify adaptation events
        assert len(test_agent.adaptation_events) == 4
        assert test_agent.adaptation_events[0]["adaptation_type"] == "clarification"
        assert "Contradictory" in test_agent.adaptation_events[1]["input"]
        assert test_agent.adaptation_events[2]["adaptation_type"] == "knowledge_update"
        assert "Failed code" in test_agent.adaptation_events[3]["input"]
    
    def test_context_window_management(self, test_agent):
        """Test effective context window management."""
        # Create a large history that would exceed context limits
        for i in range(10):
            test_agent.history.append((None, f"Historical entry {i} with substantial content" * 20))
        
        # Add current context elements
        current_context = {
            "literature": "Extensive literature review..." * 30,
            "experiments": "Detailed experiment logs..." * 25,
            "code": "Multi-file codebase..." * 40,
            "results": "Comprehensive results analysis..." * 35
        }
        
        # Simulate context pruning
        def prune_context(context, max_tokens):
            """Mock function to prune context to fit in window."""
            pruned = {}
            total_size = 0
            
            # Priority order: results, code, experiments, literature
            priority_keys = ["results", "code", "experiments", "literature"]
            
            for key in priority_keys:
                # Simulate token counting by character length / 4
                content = context[key]
                content_size = len(content) // 4
                
                if total_size + content_size <= max_tokens:
                    # Full content fits
                    pruned[key] = content
                    total_size += content_size
                else:
                    # Need to truncate
                    available_tokens = max_tokens - total_size
                    truncated_content = content[:available_tokens * 4]
                    if len(truncated_content) > 50:  # Only include if meaningful content remains
                        pruned[key] = truncated_content + "... [truncated]"
                        total_size = max_tokens
                    break
            
            return pruned, total_size
            
        # Test pruning at different context sizes
        pruned_4k, size_4k = prune_context(current_context, 4000)
        pruned_8k, size_8k = prune_context(current_context, 8000)
        pruned_16k, size_16k = prune_context(current_context, 16000)
        pruned_32k, size_32k = prune_context(current_context, 32000)
        
        # Verify pruning behavior
        assert size_4k <= 4000
        assert size_8k <= 8000
        assert size_16k <= 16000
        assert size_32k <= 32000
        
        # Verify priority ordering is maintained
        if len(pruned_4k) < 4:
            assert "results" in pruned_4k  # Results preserved first
        if len(pruned_8k) < 4 and len(pruned_8k) > 1:
            assert "results" in pruned_8k and "code" in pruned_8k  # Results and code preserved
            
        # As context window grows, more content is preserved
        assert len(pruned_4k.keys()) <= len(pruned_8k.keys()) <= len(pruned_16k.keys()) <= len(pruned_32k.keys())
    
    def test_handling_contradictory_information(self, test_agent):
        """Test agent's ability to handle contradictory information."""
        # Set up contradictory information
        contradictions = [
            {
                "source_1": {"claim": "Method A outperforms Method B", "confidence": 0.8},
                "source_2": {"claim": "Method B outperforms Method A", "confidence": 0.7}
            },
            {
                "source_1": {"claim": "Parameter X should be increased", "confidence": 0.6},
                "source_2": {"claim": "Parameter X should be decreased", "confidence": 0.9}
            }
        ]
        
        # Function to resolve contradictions
        def resolve_contradiction(contradiction):
            """Mock function to resolve contradictory information."""
            # Simple resolution strategy: choose higher confidence source
            if contradiction["source_1"]["confidence"] > contradiction["source_2"]["confidence"]:
                return {
                    "resolved_claim": contradiction["source_1"]["claim"],
                    "resolution_method": "confidence_based",
                    "winning_source": "source_1"
                }
            else:
                return {
                    "resolved_claim": contradiction["source_2"]["claim"],
                    "resolution_method": "confidence_based",
                    "winning_source": "source_2"
                }
                
        # Resolve contradictions
        resolutions = [resolve_contradiction(c) for c in contradictions]
        
        # Verify resolutions
        assert resolutions[0]["winning_source"] == "source_1"  # Higher confidence
        assert "Method A outperforms" in resolutions[0]["resolved_claim"]
        
        assert resolutions[1]["winning_source"] == "source_2"  # Higher confidence
        assert "Parameter X should be decreased" in resolutions[1]["resolved_claim"]
        
        assert all(r["resolution_method"] == "confidence_based" for r in resolutions)
        
        # In a real implementation, more sophisticated resolution strategies would be tested:
        # - Evidence-based resolution
        # - Hybrid methods
        # - External verification
        # - Uncertainty propagation