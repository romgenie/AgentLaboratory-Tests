import pytest
import sys
import os
import time
import gc
import psutil
import tracemalloc
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.token_utils import get_token_count, truncate_to_token_limit
from agents.base_agent import BaseAgent

@pytest.mark.performance
class TestMemoryOptimization:
    """Performance tests for memory optimization."""
    
    @pytest.fixture
    def sample_long_text(self):
        """Fixture to create a sample long text for testing."""
        # Generate a text with approximately 8000 tokens (about 32KB)
        return " ".join(["word" for _ in range(40000)])
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = BaseAgent(
            name="Test Agent",
            expertise=["Testing"],
            personality_traits=["efficient"],
            model="gpt-4o"
        )
        return agent
    
    @pytest.fixture
    def memory_tracking(self):
        """Setup and teardown for memory tracking."""
        # Start tracking memory allocations
        tracemalloc.start()
        process = psutil.Process(os.getpid())
        # Force garbage collection to get a clean starting point
        gc.collect()
        # Get starting values
        start_snapshot = tracemalloc.take_snapshot()
        start_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        yield {
            "process": process,
            "start_memory": start_memory,
            "start_snapshot": start_snapshot
        }
        
        # Clean up
        tracemalloc.stop()
    
    def test_memory_usage_token_counting(self, sample_long_text, memory_tracking):
        """Test memory usage during token counting operations."""
        # Measure memory before operation
        before_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        
        # Perform token counting operation repeatedly to get a measurable impact
        for _ in range(100):
            token_count = get_token_count(sample_long_text)
            
        # Measure memory after operation
        after_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        memory_increase = after_memory - before_memory
        
        # Take memory snapshot for detailed analysis
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.compare_to(memory_tracking["start_snapshot"], 'lineno')
        
        # Log memory statistics
        print(f"Memory before: {before_memory:.2f} MB")
        print(f"Memory after: {after_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print("Top memory allocations:")
        for stat in top_stats[:3]:  # Show top 3 allocations
            print(f"{stat}")
        
        # Memory usage should be reasonable - typically under 10MB for this operation
        # This is a very conservative threshold for this small test
        assert memory_increase < 20, f"Memory increase of {memory_increase:.2f} MB exceeds threshold"
    
    def test_memory_cleanup_after_truncation(self, sample_long_text, memory_tracking):
        """Test that memory is properly cleaned up after text truncation."""
        # Measure memory before operation
        before_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        
        # Perform text truncation operation
        for _ in range(50):
            truncated_text = truncate_to_token_limit(sample_long_text, 1000)
        
        # Force garbage collection to clean up any unreferenced objects
        gc.collect()
        
        # Measure memory after operation and cleanup
        after_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        memory_increase = after_memory - before_memory
        
        # Log memory statistics
        print(f"Memory before: {before_memory:.2f} MB")
        print(f"Memory after: {after_memory:.2f} MB")
        print(f"Memory increase after GC: {memory_increase:.2f} MB")
        
        # Should be minimal memory increase after GC if cleanup is proper
        assert memory_increase < 5, f"Memory not properly cleaned up. Increase: {memory_increase:.2f} MB"
    
    @patch('inference.query_model.query_model')
    def test_agent_memory_usage(self, mock_query_model, mock_agent, memory_tracking):
        """Test memory usage patterns during agent interactions."""
        # Configure mock
        mock_query_model.return_value = "Model response to the query"
        
        # Track memory before operations
        before_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        
        # Generate a series of prompts of increasing size
        for i in range(1, 11):
            # Each prompt is larger than the previous
            prompt = f"This is prompt number {i}. " * (i * 100)
            
            # Call agent's get_response
            result = mock_agent.get_response(prompt)
            
            # Measure memory after each iteration
            current_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
            print(f"Memory after iteration {i}: {current_memory:.2f} MB (+{current_memory - before_memory:.2f} MB)")
            
            # Memory usage should grow sublinearly with prompt size due to efficient handling
            # For this test, we're just looking for runaway memory growth
            if i > 1:
                assert current_memory < before_memory * 2, f"Memory usage growing too fast: {current_memory:.2f} MB"
        
        # Final memory after all operations
        after_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        memory_increase = after_memory - before_memory
        
        # Force garbage collection
        gc.collect()
        final_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        memory_after_gc = final_memory - before_memory
        
        # Log memory statistics
        print(f"Memory before: {before_memory:.2f} MB")
        print(f"Memory after all operations: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
        print(f"Memory after GC: {final_memory:.2f} MB (+{memory_after_gc:.2f} MB)")
        
        # Check that memory is properly cleaned up
        assert memory_after_gc < memory_increase * 0.5, "Memory not properly cleaned up after agent operations"
    
    def test_memory_efficiency_comparison(self, sample_long_text, memory_tracking):
        """Compare memory efficiency of different text handling approaches."""
        # Approach 1: Copy the entire text multiple times (inefficient)
        before_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        inefficient_copies = []
        for _ in range(10):
            inefficient_copies.append(sample_long_text + " ")
        inefficient_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024 - before_memory
        del inefficient_copies
        gc.collect()
        
        # Approach 2: Use slices and references (efficient)
        before_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024
        efficient_refs = []
        for i in range(10):
            # Just store references to slices
            start_pos = 0
            end_pos = len(sample_long_text) - i * 1000
            efficient_refs.append(sample_long_text[start_pos:end_pos])
        efficient_memory = memory_tracking["process"].memory_info().rss / 1024 / 1024 - before_memory
        
        # Log the comparison
        print(f"Inefficient memory usage: {inefficient_memory:.2f} MB")
        print(f"Efficient memory usage: {efficient_memory:.2f} MB")
        print(f"Memory efficiency ratio: {inefficient_memory/efficient_memory:.2f}x")
        
        # The efficient approach should use significantly less memory
        assert efficient_memory < inefficient_memory, "Efficient approach is not saving memory"