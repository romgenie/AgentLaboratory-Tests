import pytest
from unittest.mock import MagicMock, patch

# Example mock implementations
class MockLLMResponse:
    """Mock LLM API response."""
    def __init__(self, content="Sample response content"):
        self.content = content
        self.model = "mock-model"
        self.usage = {"prompt_tokens": 10, "completion_tokens": 20}

class MockArxivPaper:
    """Mock arXiv paper data."""
    def __init__(self, title="Sample Paper", authors=None, summary="Sample summary"):
        self.title = title
        self.authors = authors or ["Author One", "Author Two"]
        self.summary = summary
        self.pdf_url = "https://arxiv.org/pdf/0000.00000.pdf"

# Mock fixtures for use in tests
@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response object."""
    return MockLLMResponse()

@pytest.fixture
def mock_arxiv_data():
    """Create mock arXiv search results."""
    return [MockArxivPaper(f"Paper {i}", summary=f"Summary {i}") for i in range(3)]

# Example test using mocks
def test_mock_response_format():
    """Test that mock response has the expected format."""
    response = MockLLMResponse("Test content")
    assert response.content == "Test content"
    assert hasattr(response, "usage")