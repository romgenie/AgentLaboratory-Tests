import pytest
import sys
import os
import time
import gc
import psutil
import tracemalloc
import socket
import random
import threading
from unittest.mock import patch, MagicMock, Mock
from contextlib import contextmanager

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.base_agent import BaseAgent
from inference.query_model import query_model
from ai_lab_repo import AgentLabRepository
from utils.token_utils import count_tokens as get_token_count, truncate_to_token_limit

"""
Long-Running Stability Tests

This module provides test cases for validating the system's stability during 
extended operation. Tests verify memory usage patterns, extended agent interaction
stability, resource utilization, network failure recovery, and token optimization
over time.
"""

# Simulation settings for long-running tests
EXTENDED_INTERACTION_COUNT = 100
EXTENDED_TEST_DURATION = 5  # seconds for each test phase (shortened for test runtime, would be much longer in production)
NETWORK_FAILURE_PROBABILITY = 0.05  # 5% chance of network failure during tests

@contextmanager
def network_instability_simulation():
    """Context manager that simulates random network failures during operation."""
    original_socket_connect = socket.socket.connect
    
    def unstable_connect(self, *args, **kwargs):
        # Randomly fail with a certain probability
        if random.random() < NETWORK_FAILURE_PROBABILITY:
            raise ConnectionError("Simulated network failure")
        return original_socket_connect(self, *args, **kwargs)
    
    # Replace socket.connect with our unstable version
    socket.socket.connect = unstable_connect
    try:
        yield
    finally:
        # Restore original socket.connect
        socket.socket.connect = original_socket_connect

@pytest.mark.performance
class TestLongRunningStability:
    """
    Tests for long-running stability of the Agent Laboratory system.
    
    These tests verify the system's behavior during extended operations,
    focusing on memory management, resource utilization, and recovery
    from failure conditions.
    """
    
    @pytest.fixture
    def memory_tracking(self):
        """Set up and tear down for memory tracking."""
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
    
    @pytest.fixture
    def mock_lab_repository(self):
        """Create a mock AgentLabRepository instance."""
        with patch('ai_lab_repo.AgentLabRepository._initialize_system'):
            repo = AgentLabRepository(
                api_key="test_key",
                llm_backend="gpt-4o",
                research_topic="Test topic",
                research_dir="test_dir",
                verbose=False
            )
            return repo
    
    @pytest.fixture
    def agent_team(self):
        """Create a team of agents for testing."""
        return {
            "professor": BaseAgent(
                name="Dr. Smith",
                expertise=["Machine Learning", "NLP"],
                personality_traits=["methodical", "analytical"],
                model="gpt-4o"
            ),
            "phd_student": BaseAgent(
                name="Jane Doe", 
                expertise=["Deep Learning", "Computer Vision"],
                personality_traits=["creative", "curious"],
                model="gpt-4o"
            ),
            "engineer": BaseAgent(
                name="Alex Lee",
                expertise=["Software Engineering", "System Design"],
                personality_traits=["practical", "detail-oriented"],
                model="gpt-4o"
            )
        }
    
    def test_memory_leak_detection(self, memory_tracking):
        """
        Test for memory leaks during long-running operations.
        
        This test performs a series of operations that mimic typical system usage
        and monitors memory growth patterns to detect potential leaks.
        """
        # Initial memory snapshot
        memory_snapshots = []
        memory_snapshots.append(memory_tracking["process"].memory_info().rss / 1024 / 1024)
        
        # Simulate long-running operation with many agents and interactions
        with patch('inference.query_model.query_model', return_value="Mocked model response"):
            agents = []
            # Create multiple agents
            for i in range(10):
                agent = BaseAgent(
                    name=f"Agent {i}",
                    expertise=["Testing"],
                    personality_traits=["stable"],
                    model="gpt-4o"
                )
                agents.append(agent)
                
            # Simulate many interactions
            for _ in range(EXTENDED_INTERACTION_COUNT):
                for agent in agents:
                    # Generate a random prompt
                    prompt = f"Test prompt with some random content: {random.random()}"
                    # Get response from agent
                    response = agent.get_response(prompt)
                    # Add to memory
                    agent.add_to_memory(prompt, response)
                
                # Take memory snapshot every 10 interactions
                if _ % 10 == 0:
                    gc.collect()  # Collect garbage to measure actual retained memory
                    memory_snapshots.append(memory_tracking["process"].memory_info().rss / 1024 / 1024)
                    print(f"Memory after {_} interactions: {memory_snapshots[-1]:.2f} MB")
        
        # Final memory cleanup and snapshot
        for agent in agents:
            agent.memory.clear()
        gc.collect()
        memory_snapshots.append(memory_tracking["process"].memory_info().rss / 1024 / 1024)
        
        # Analyze memory growth pattern
        memory_growth = [memory_snapshots[i+1] - memory_snapshots[i] for i in range(len(memory_snapshots)-1)]
        avg_growth = sum(memory_growth) / len(memory_growth)
        
        # Log memory analysis
        print(f"Initial memory: {memory_snapshots[0]:.2f} MB")
        print(f"Final memory: {memory_snapshots[-1]:.2f} MB")
        print(f"Memory snapshots: {memory_snapshots}")
        print(f"Average memory growth per interval: {avg_growth:.2f} MB")
        
        # Test that memory growth isn't accelerating (which would indicate a leak)
        # Compare first half growth to second half growth
        half_point = len(memory_growth) // 2
        first_half_growth = sum(memory_growth[:half_point]) / half_point if half_point > 0 else 0
        second_half_growth = sum(memory_growth[half_point:]) / (len(memory_growth) - half_point) if half_point < len(memory_growth) else 0
        
        print(f"First half average growth: {first_half_growth:.2f} MB")
        print(f"Second half average growth: {second_half_growth:.2f} MB")
        
        # Memory growth should not accelerate for stable systems
        assert second_half_growth <= first_half_growth * 1.5, "Memory growth is accelerating, possible memory leak"
        
        # Final memory should be within reasonable bounds
        final_growth = memory_snapshots[-1] - memory_snapshots[0]
        assert final_growth < 100, f"Memory grew too much during test: {final_growth:.2f} MB"
    
    @patch('inference.query_model.query_model')
    def test_extended_agent_interactions(self, mock_query_model, agent_team, memory_tracking):
        """
        Test system stability during extended agent interactions.
        
        Simulates 100+ interactions between agents and verifies that the system
        remains responsive and stable throughout.
        """
        mock_query_model.return_value = "Detailed response from the model"
        
        # Track interaction performance metrics
        response_times = []
        memory_usage = []
        
        # Simulate extended conversations between agents
        for i in range(EXTENDED_INTERACTION_COUNT):
            # Choose random agents for interaction
            agent1, agent2 = random.sample(list(agent_team.values()), 2)
            
            # Create a prompt with increasing complexity
            prompt = f"Discussion point {i}: What do you think about the application of transformer models in {random.choice(['healthcare', 'finance', 'education', 'robotics', 'climate science'])}? " * (i % 5 + 1)
            
            # Measure response time
            start_time = time.time()
            response1 = agent1.get_response(prompt)
            agent1.add_to_memory(prompt, response1)
            
            # Second agent responds to first agent
            prompt2 = f"Responding to {agent1.name}'s comment: {response1[:50]}..."
            response2 = agent2.get_response(prompt2)
            agent2.add_to_memory(prompt2, response2)
            
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            # Measure memory after each 10 interactions
            if i % 10 == 0:
                memory_usage.append(memory_tracking["process"].memory_info().rss / 1024 / 1024)
                print(f"Interaction {i}, Memory: {memory_usage[-1]:.2f} MB, Response time: {response_times[-1]:.4f}s")
            
            # Verify agent memory integrity
            assert len(agent1.memory) == i + 1, f"Agent memory inconsistency: {len(agent1.memory)} vs expected {i+1}"
            
            # Simulate periodic garbage collection
            if i % 25 == 0 and i > 0:
                gc.collect()
        
        # Analyze response times
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Analyze memory usage
        initial_memory = memory_usage[0]
        final_memory = memory_usage[-1]
        memory_growth = final_memory - initial_memory
        
        # Print analysis
        print(f"Average response time: {avg_response_time:.4f}s")
        print(f"Max response time: {max_response_time:.4f}s")
        print(f"Min response time: {min_response_time:.4f}s")
        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory growth: {memory_growth:.2f} MB")
        
        # Assertions for stability
        # 1. Response times should not have extreme outliers
        assert max_response_time < avg_response_time * 5, "Response time has extreme outliers"
        
        # 2. Memory should not grow unbounded
        assert memory_growth < initial_memory * 2, "Memory growth is too high"
        
        # 3. Check agent memory integrity at the end
        for agent_name, agent in agent_team.items():
            # Verify that memories are not corrupted
            for memory_item in agent.memory:
                assert "prompt" in memory_item, f"Agent {agent_name} has corrupted memory"
                assert "response" in memory_item, f"Agent {agent_name} has corrupted memory"
    
    def test_resource_utilization_tracking(self, mock_lab_repository):
        """
        Test the tracking of system resource utilization over time.
        
        Monitors CPU, memory, and disk usage during system operation and
        verifies that resource utilization patterns are stable.
        """
        # Initialize performance monitoring
        process = psutil.Process(os.getpid())
        cpu_usage = []
        memory_usage = []
        disk_io_before = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
        
        # Patch key methods that would be called during research
        with patch.object(mock_lab_repository, 'literature_review', return_value={"status": "completed"}), \
             patch.object(mock_lab_repository, 'plan_formulation', return_value={"status": "completed"}), \
             patch.object(mock_lab_repository, 'running_experiments', return_value={"status": "completed"}), \
             patch.object(mock_lab_repository, 'report_writing', return_value={"status": "completed"}):
            
            # Track resource usage while running simulated workload
            start_time = time.time()
            end_time = start_time + EXTENDED_TEST_DURATION
            
            # Run periodic measurements during the test duration
            while time.time() < end_time:
                # Simulate system activity
                for _ in range(5):  # Do some work each iteration
                    mock_lab_repository.literature_review()
                    mock_lab_repository.plan_formulation()
                
                # Capture resource metrics
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                cpu_usage.append(cpu_percent)
                memory_usage.append(memory_info.rss / 1024 / 1024)  # Convert to MB
                
                # Short sleep to prevent tight loop
                time.sleep(0.2)
        
        # Get final disk I/O stats
        disk_io_after = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
        
        # Analyze resource utilization
        avg_cpu = sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0
        max_cpu = max(cpu_usage) if cpu_usage else 0
        avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
        max_memory = max(memory_usage) if memory_usage else 0
        
        # Calculate disk I/O
        disk_read = disk_io_after.read_bytes - disk_io_before.read_bytes if disk_io_before and disk_io_after else 0
        disk_write = disk_io_after.write_bytes - disk_io_before.write_bytes if disk_io_before and disk_io_after else 0
        
        # Print resource utilization summary
        print(f"Average CPU usage: {avg_cpu:.2f}%")
        print(f"Peak CPU usage: {max_cpu:.2f}%")
        print(f"Average memory usage: {avg_memory:.2f} MB")
        print(f"Peak memory usage: {max_memory:.2f} MB")
        print(f"Disk read: {disk_read / 1024 / 1024:.2f} MB")
        print(f"Disk write: {disk_write / 1024 / 1024:.2f} MB")
        
        # Check for resource usage spikes
        cpu_std_dev = (sum((x - avg_cpu) ** 2 for x in cpu_usage) / len(cpu_usage)) ** 0.5 if cpu_usage else 0
        memory_std_dev = (sum((x - avg_memory) ** 2 for x in memory_usage) / len(memory_usage)) ** 0.5 if memory_usage else 0
        
        print(f"CPU usage standard deviation: {cpu_std_dev:.2f}%")
        print(f"Memory usage standard deviation: {memory_std_dev:.2f} MB")
        
        # Assertions for stable resource utilization
        assert max_cpu < 95, f"CPU usage too high: {max_cpu:.2f}%"
        assert memory_std_dev < avg_memory * 0.2, f"Memory usage has high variability: {memory_std_dev:.2f} MB"
    
    @patch('inference.query_model.query_model')
    def test_recovery_from_network_interruptions(self, mock_query_model, agent_team):
        """
        Test the system's ability to recover from network interruptions.
        
        Simulates random network failures during API calls and verifies that
        the system can gracefully recover and continue operation.
        """
        # Setup network failure simulation
        network_failures = 0
        successful_queries = 0
        failed_queries = 0
        
        # Configure the mock to occasionally fail
        def mock_api_with_failures(*args, **kwargs):
            nonlocal network_failures
            if random.random() < NETWORK_FAILURE_PROBABILITY:
                network_failures += 1
                raise ConnectionError("Simulated network failure")
            return "Response after potentially recovering from network issues"
        
        mock_query_model.side_effect = mock_api_with_failures
        
        # Setup retry and tracking mechanisms
        max_retries = 3
        retry_delay = 0.1  # seconds
        
        def query_with_retry(agent, prompt, max_attempts=max_retries):
            nonlocal successful_queries, failed_queries
            attempts = 0
            while attempts < max_attempts:
                try:
                    attempts += 1
                    response = agent.get_response(prompt)
                    successful_queries += 1
                    return response
                except ConnectionError:
                    if attempts >= max_attempts:
                        failed_queries += 1
                        raise
                    time.sleep(retry_delay * attempts)  # Exponential backoff
            return None
        
        # Run test with simulated interruptions
        results = []
        start_time = time.time()
        
        # Create multiple threads to simulate concurrent API calls
        threads = []
        thread_results = {}
        
        for i in range(EXTENDED_INTERACTION_COUNT):
            def worker(idx, agent_name):
                thread_results[idx] = {"success": False, "retries": 0}
                agent = agent_team[agent_name]
                prompt = f"Thread {idx} testing network resilience"
                
                try:
                    response = query_with_retry(agent, prompt)
                    thread_results[idx]["success"] = True
                    thread_results[idx]["response"] = response
                except Exception as e:
                    thread_results[idx]["error"] = str(e)
                
                thread_results[idx]["agent"] = agent_name
            
            # Choose a random agent for this thread
            agent_name = random.choice(list(agent_team.keys()))
            thread = threading.Thread(target=worker, args=(i, agent_name))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Calculate success rate and statistics
        total_time = time.time() - start_time
        success_count = sum(1 for result in thread_results.values() if result["success"])
        failure_count = EXTENDED_INTERACTION_COUNT - success_count
        success_rate = success_count / EXTENDED_INTERACTION_COUNT * 100
        
        # Print results
        print(f"Total API calls: {successful_queries + failed_queries}")
        print(f"Successful API calls: {successful_queries}")
        print(f"Failed API calls: {failed_queries}")
        print(f"Network failures triggered: {network_failures}")
        print(f"Thread success rate: {success_rate:.2f}%")
        print(f"Total test time: {total_time:.2f} seconds")
        
        # Assertions for recovery capabilities
        assert success_rate > 90, f"Success rate too low: {success_rate:.2f}%"
        assert successful_queries > 0, "No successful API calls were made"
        
        # Verify that we had some network failures to recover from
        assert network_failures > 0, "No network failures were simulated, test is inconclusive"
    
    @patch('inference.query_model.query_model')
    def test_long_term_token_usage_optimization(self, mock_query_model):
        """
        Test token usage optimization over long-running operations.
        
        Verifies that token usage remains efficient over time and doesn't degrade
        with extended system operation.
        """
        # Setup token usage tracking
        token_usage_tracking = {
            "prompt_tokens": [],
            "completion_tokens": [],
            "total_tokens": [],
            "optimized_tokens": []
        }
        
        # Mock token counting
        original_get_token_count = get_token_count
        
        def mock_token_count(text):
            # Simplified token counting for testing
            return len(text.split())
        
        # Define a function that simulates optimized prompts
        def create_optimized_prompt(original_prompt, history_length):
            # Simulate prompt optimization techniques
            # 1. Truncate history if too long
            if history_length > 10:
                history_summary = f"[Summary of previous {history_length} messages]"
                return f"{history_summary}\n\nCurrent request: {original_prompt}"
            return original_prompt
        
        # Prepare test data - increasingly complex prompts
        test_prompts = []
        for i in range(EXTENDED_INTERACTION_COUNT):
            complexity = min(1 + (i // 10), 5)  # Gradually increase complexity
            prompt = f"Research question {i}: " + "How do transformer models scale with increasing parameter counts? " * complexity
            test_prompts.append(prompt)
        
        # Configure the mock response with token metadata
        def mock_response_with_tokens(*args, **kwargs):
            prompt = args[1] if len(args) > 1 else kwargs.get('prompt', '')
            prompt_tokens = mock_token_count(prompt)
            
            # Generate a response with length proportional to prompt
            response = f"Response with approximately {prompt_tokens // 2} tokens."
            completion_tokens = mock_token_count(response)
            
            # Track token usage
            token_usage_tracking["prompt_tokens"].append(prompt_tokens)
            token_usage_tracking["completion_tokens"].append(completion_tokens)
            token_usage_tracking["total_tokens"].append(prompt_tokens + completion_tokens)
            
            # Also track what optimized tokens would be
            optimized_prompt = create_optimized_prompt(prompt, len(token_usage_tracking["prompt_tokens"]))
            optimized_tokens = mock_token_count(optimized_prompt)
            token_usage_tracking["optimized_tokens"].append(optimized_tokens)
            
            return response
        
        mock_query_model.side_effect = mock_response_with_tokens
        
        # Run the long-term token usage test
        with patch('utils.token_utils.get_token_count', side_effect=mock_token_count):
            # Process each prompt and track token usage
            for i, prompt in enumerate(test_prompts):
                # Get response
                response = query_model(
                    model_str="gpt-4o",
                    prompt=prompt,
                    system_prompt="You are a research assistant."
                )
                
                # Every 10 iterations, print current token usage statistics
                if i % 10 == 0 and i > 0:
                    avg_tokens = sum(token_usage_tracking["total_tokens"][-10:]) / 10
                    avg_optimized = sum(token_usage_tracking["optimized_tokens"][-10:]) / 10
                    savings = (1 - avg_optimized / avg_tokens) * 100 if avg_tokens > 0 else 0
                    print(f"Iteration {i}, Avg tokens: {avg_tokens:.1f}, Optimized: {avg_optimized:.1f}, Savings: {savings:.1f}%")
        
        # Analyze token usage patterns
        total_tokens = sum(token_usage_tracking["total_tokens"])
        total_optimized = sum(token_usage_tracking["optimized_tokens"])
        overall_savings = (1 - total_optimized / total_tokens) * 100 if total_tokens > 0 else 0
        
        # Break down token usage into time segments to check for efficiency over time
        segment_size = EXTENDED_INTERACTION_COUNT // 4
        segments = []
        for i in range(0, EXTENDED_INTERACTION_COUNT, segment_size):
            segment_tokens = sum(token_usage_tracking["total_tokens"][i:i+segment_size])
            segment_optimized = sum(token_usage_tracking["optimized_tokens"][i:i+segment_size])
            segment_savings = (1 - segment_optimized / segment_tokens) * 100 if segment_tokens > 0 else 0
            segments.append({
                "segment": i // segment_size + 1,
                "tokens": segment_tokens,
                "optimized": segment_optimized,
                "savings": segment_savings
            })
        
        # Print token usage analysis
        print(f"Total tokens used: {total_tokens}")
        print(f"Total optimized tokens: {total_optimized}")
        print(f"Overall token savings: {overall_savings:.2f}%")
        print("Token usage by segment:")
        for segment in segments:
            print(f"  Segment {segment['segment']}: {segment['tokens']} tokens, {segment['savings']:.2f}% savings")
        
        # Assertions for token optimization
        assert overall_savings > 0, "No token savings achieved through optimization"
        
        # Check if optimization improves or maintains efficiency over time
        later_segments_avg = sum(s["savings"] for s in segments[len(segments)//2:]) / (len(segments) - len(segments)//2)
        earlier_segments_avg = sum(s["savings"] for s in segments[:len(segments)//2]) / (len(segments)//2) if len(segments) > 1 else 0
        
        print(f"Early segments average savings: {earlier_segments_avg:.2f}%")
        print(f"Later segments average savings: {later_segments_avg:.2f}%")
        
        # Token optimization should either improve or not significantly degrade over time
        assert later_segments_avg >= earlier_segments_avg * 0.8, "Token optimization efficiency degraded significantly over time"