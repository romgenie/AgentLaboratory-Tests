import pytest
import os
import sys

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Pytest configuration for Agent Laboratory tests
def pytest_configure(config):
    """Configure pytest for Agent Laboratory."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "performance: mark a test as a performance test")
    config.addinivalue_line("markers", "slow: mark a test as slow running")

# Common fixtures
@pytest.fixture
def sample_research_topic():
    """Provide a sample research topic for testing."""
    return "Machine learning for climate change prediction"

@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "sk-test-key-12345"