import pytest
import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import from adapter instead of directly
from test_adapters.arxiv_adapter import search_arxiv, mock_search_arxiv, ArXivEngine

class TestArxivSearch:
    """Test suite for ArXiv search functionality."""
    
    def test_search_arxiv_returns_list(self):
        """Test that search_arxiv returns a list of results."""
        results = search_arxiv("machine learning")
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_search_arxiv_max_results(self):
        """Test that search_arxiv respects max_results parameter."""
        max_results = 1
        results = search_arxiv("neural networks", max_results=max_results)
        assert len(results) <= max_results
    
    def test_search_arxiv_result_structure(self):
        """Test that search_arxiv results have the expected structure."""
        results = search_arxiv("deep learning")
        
        for paper in results:
            assert isinstance(paper, dict)
            assert 'id' in paper
            assert 'title' in paper
            assert 'authors' in paper
            assert 'summary' in paper
            assert 'published' in paper
            
            assert isinstance(paper['id'], str)
            assert isinstance(paper['title'], str)
            assert isinstance(paper['authors'], list)
            assert isinstance(paper['summary'], str)
            assert isinstance(paper['published'], str)
    
    def test_mock_search_arxiv_filter(self):
        """Test that mock_search_arxiv correctly filters results by query."""
        # Search for neural networks
        results_neural = mock_search_arxiv("neural networks")
        assert any("neural" in paper['title'].lower() for paper in results_neural)
        
        # Search for reinforcement learning
        results_rl = mock_search_arxiv("reinforcement")
        assert any("reinforcement" in paper['title'].lower() for paper in results_rl)
        
    def test_arxiv_engine_class(self):
        """Test the ArXivEngine class functionality."""
        engine = ArXivEngine()
        
        # Test search method
        results = engine.search("graph neural")
        assert isinstance(results, list)
        assert any("graph neural" in paper['title'].lower() for paper in results)
        
        # Test full paper retrieval
        paper_id = "2201.12345"
        paper_text = engine.retrieve_full_paper_text(paper_id)
        assert isinstance(paper_text, str)
        assert "machine learning" in paper_text.lower()
        
        # Test retrieval of non-existent paper
        invalid_id = "1234.56789"
        not_found_text = engine.retrieve_full_paper_text(invalid_id)
        assert invalid_id in not_found_text
        assert "not found" in not_found_text.lower()