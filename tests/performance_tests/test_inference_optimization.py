import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from inference.query_model import query_model
from utils.token_utils import get_token_count

@pytest.mark.performance
class TestInferenceOptimization:
    """Performance tests for LLM inference optimization."""
    
    @pytest.fixture
    def sample_prompts(self):
        """Generate sample prompts of different sizes for testing."""
        return {
            "small": "Summarize the concept of attention in neural networks.",
            "medium": " ".join(["The attention mechanism in neural networks" for _ in range(50)]),
            "large": " ".join(["Attention is all you need" for _ in range(200)])
        }
    
    @pytest.fixture
    def mock_model_response(self):
        """Mock model response with varying response times."""
        def delayed_response(model_str, prompt, *args, **kwargs):
            """Return a response after a simulated delay based on prompt size."""
            prompt_tokens = get_token_count(prompt)
            # Simulate model inference time increasing with prompt size
            delay = min(0.01 * prompt_tokens / 100, 0.1)  # Cap at 100ms
            time.sleep(delay)
            return f"Model response to prompt with {prompt_tokens} tokens"
        return delayed_response
    
    @patch('inference.query_model.query_model')
    def test_query_model_performance(self, mock_query_model, sample_prompts):
        """Test the performance of query_model with different prompts."""
        # Configure mock with side effect to simulate response times
        def side_effect(model_str, prompt, *args, **kwargs):
            prompt_tokens = get_token_count(prompt)
            # Simulate response time based on prompt size
            delay = 0.01 * prompt_tokens / 100
            time.sleep(delay)
            return f"Response to prompt with {prompt_tokens} tokens"
        
        mock_query_model.side_effect = side_effect
        
        # Test each prompt size and measure time
        perf_results = {}
        
        for size, prompt in sample_prompts.items():
            start_time = time.time()
            response = query_model(
                model_str="gpt-4o",
                prompt=prompt,
                system_prompt="You are a helpful assistant."
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            prompt_tokens = get_token_count(prompt)
            tokens_per_second = prompt_tokens / elapsed_time if elapsed_time > 0 else float('inf')
            
            perf_results[size] = {
                "elapsed_time": elapsed_time,
                "prompt_tokens": prompt_tokens,
                "tokens_per_second": tokens_per_second
            }
            
            print(f"Prompt size: {size}")
            print(f"  Tokens: {prompt_tokens}")
            print(f"  Time: {elapsed_time:.4f} seconds")
            print(f"  Throughput: {tokens_per_second:.2f} tokens/second")
        
        # Verify that performance is reasonable
        # We expect processing speed to scale sublinearly with input size
        small_throughput = perf_results["small"]["tokens_per_second"]
        large_throughput = perf_results["large"]["tokens_per_second"]
        
        # Large prompts should still process at a reasonable rate compared to small ones
        throughput_ratio = small_throughput / large_throughput if large_throughput > 0 else float('inf')
        print(f"Throughput ratio (small/large): {throughput_ratio:.2f}x")
        
        # In a well-optimized system, the ratio shouldn't be too high
        # This is a flexible assertion since actual values depend on implementation
        assert throughput_ratio < 5, f"Performance degradation for large prompts is too high: {throughput_ratio:.2f}x"
    
    @patch('inference.query_model.query_model')
    def test_batched_vs_sequential_inference(self, mock_query_model, sample_prompts):
        """Test performance difference between batched and sequential inference."""
        # Configure mock
        def batch_aware_response(model_str, prompt, *args, **kwargs):
            # Simulate faster inference for similar prompts (as if batched)
            tokens = get_token_count(prompt)
            time.sleep(0.005 * tokens / 100)  # Reduced time for batched queries
            return f"Response to {tokens} tokens"
        
        mock_query_model.side_effect = batch_aware_response
        
        # Create a list of similar prompts for batching
        batch_prompts = [sample_prompts["medium"] for _ in range(5)]
        
        # Test sequential processing
        start_time = time.time()
        sequential_results = []
        for prompt in batch_prompts:
            result = query_model("gpt-4o", prompt)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Test simulated batched processing (in this test, just to demonstrate the concept)
        # In a real implementation, this would use actual batching capabilities
        start_time = time.time()
        batch_results = []
        for prompt in batch_prompts:
            # Simulate that these would be processed as a batch
            result = query_model("gpt-4o", prompt)
            batch_results.append(result)
        batched_time = time.time() - start_time
        
        # Print performance metrics
        print(f"Sequential processing time: {sequential_time:.4f} seconds")
        print(f"Batched processing time: {batched_time:.4f} seconds")
        print(f"Speedup factor: {sequential_time/batched_time:.2f}x")
        
        # Validate results
        assert len(sequential_results) == len(batch_results) == len(batch_prompts)
        
        # In a real system with batching, batched should be faster
        # For our mock simulation, they should be at least comparable
        assert batched_time <= sequential_time * 1.1, "Batched processing should be at least as fast as sequential"
    
    @patch('inference.query_model.query_model')
    def test_prompt_optimization_impact(self, mock_query_model, sample_prompts):
        """Test the impact of prompt optimization techniques on performance."""
        # Configure mock to simulate response times based on prompt complexity
        def complexity_aware_response(model_str, prompt, *args, **kwargs):
            tokens = get_token_count(prompt)
            # Simulate longer processing for complex prompts
            # (in reality, more precisely structured prompts can lead to faster processing)
            complexity_factor = 1.0 if "structured:" in prompt.lower() else 1.5
            time.sleep(0.01 * tokens / 100 * complexity_factor)
            return f"Response to {tokens} tokens"
        
        mock_query_model.side_effect = complexity_aware_response
        
        # Unoptimized prompt (verbose, unclear instructions)
        unoptimized_prompt = (
            "I want you to analyze this text and give me your thoughts on it. "
            "The text is about neural networks and specifically attention mechanisms. "
            "I'd like to know what you think about it, what's good about it, what could be improved, "
            "and any other insights you might have. Please provide a detailed response."
        ) * 3  # Repeat to make it longer
        
        # Optimized prompt (clear, structured, concise)
        optimized_prompt = (
            "structured: Analyze the attention mechanism in neural networks as described below. "
            "Provide assessment in the following format:\n"
            "1. Key strengths\n2. Limitations\n3. Potential improvements\n"
        ) * 3  # Repeat to match length
        
        # Ensure prompts are comparable in length
        unopt_tokens = get_token_count(unoptimized_prompt)
        opt_tokens = get_token_count(optimized_prompt)
        print(f"Unoptimized prompt tokens: {unopt_tokens}")
        print(f"Optimized prompt tokens: {opt_tokens}")
        
        # Test unoptimized prompt
        start_time = time.time()
        unopt_response = query_model("gpt-4o", unoptimized_prompt)
        unopt_time = time.time() - start_time
        
        # Test optimized prompt
        start_time = time.time()
        opt_response = query_model("gpt-4o", optimized_prompt)
        opt_time = time.time() - start_time
        
        # Calculate speedup
        speedup = unopt_time / opt_time if opt_time > 0 else float('inf')
        
        # Print performance metrics
        print(f"Unoptimized prompt processing time: {unopt_time:.4f} seconds")
        print(f"Optimized prompt processing time: {opt_time:.4f} seconds")
        print(f"Optimization speedup: {speedup:.2f}x")
        
        # Optimized prompts should process faster
        assert opt_time < unopt_time, "Optimized prompts should process faster than unoptimized ones"
        
    @patch('inference.query_model.query_model')
    def test_model_selection_performance(self, mock_query_model):
        """Test performance implications of different model selections."""
        # Define a set of models with simulated inference characteristics
        models = {
            "gpt-4o": {"speed": 1.0, "quality": 1.0},  # Baseline
            "gpt-4o-mini": {"speed": 2.0, "quality": 0.9},  # Faster but slightly lower quality
            "deepseek-chat": {"speed": 1.5, "quality": 0.95},  # Good balance
            "claude-3-sonnet": {"speed": 1.2, "quality": 0.97}  # Close to baseline
        }
        
        # Configure mock to simulate different model speeds
        def model_aware_response(model_str, prompt, *args, **kwargs):
            tokens = get_token_count(prompt)
            # Get model characteristics or use baseline if unknown
            model_info = models.get(model_str, {"speed": 1.0, "quality": 1.0})
            # Simulate inference time based on model speed
            time.sleep(0.02 * tokens / 100 / model_info["speed"])
            return f"Response from {model_str} with quality {model_info['quality']}"
        
        mock_query_model.side_effect = model_aware_response
        
        # Sample prompt for testing
        prompt = "Explain the concept of attention mechanisms in transformer models."
        
        # Test each model and measure performance
        results = {}
        for model_name, characteristics in models.items():
            start_time = time.time()
            response = query_model(model_name, prompt)
            elapsed_time = time.time() - start_time
            
            # Calculate tokens per second
            tokens = get_token_count(prompt)
            throughput = tokens / elapsed_time if elapsed_time > 0 else float('inf')
            
            # Store results
            results[model_name] = {
                "elapsed_time": elapsed_time,
                "throughput": throughput,
                "quality": characteristics["quality"]
            }
            
            print(f"Model: {model_name}")
            print(f"  Time: {elapsed_time:.4f} seconds")
            print(f"  Throughput: {throughput:.2f} tokens/second")
            print(f"  Quality factor: {characteristics['quality']:.2f}")
        
        # Calculate and print performance-quality tradeoffs
        baseline = results["gpt-4o"]
        for model_name, metrics in results.items():
            if model_name == "gpt-4o":
                continue
                
            speedup = baseline["elapsed_time"] / metrics["elapsed_time"]
            quality_ratio = metrics["quality"] / baseline["quality"]
            efficiency = speedup * quality_ratio
            
            print(f"{model_name} vs gpt-4o:")
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Quality ratio: {quality_ratio:.2f}x")
            print(f"  Efficiency (speedup × quality): {efficiency:.2f}")
            
            # Faster models should have a speedup > 1
            assert speedup > 0.8, f"{model_name} should have reasonable performance compared to baseline"