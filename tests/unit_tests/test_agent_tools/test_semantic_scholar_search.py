import pytest
import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import from the adapter instead of the original module
from test_adapters.semantic_scholar_adapter import (
    search_semantic_scholar, 
    mock_search_semantic_scholar, 
    SemanticScholarEngine
)

class TestSemanticScholarSearch:
    """Test suite for Semantic Scholar search functionality."""
    
    def test_search_semantic_scholar_returns_list(self):
        """Test that search_semantic_scholar returns a list of results."""
        results = search_semantic_scholar("deep learning")
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_search_semantic_scholar_max_results(self):
        """Test that search_semantic_scholar respects max_results parameter."""
        max_results = 1
        results = search_semantic_scholar("transformers", max_results=max_results)
        assert len(results) <= max_results
    
    def test_search_semantic_scholar_result_structure(self):
        """Test that search_semantic_scholar results have the expected structure."""
        results = search_semantic_scholar("computer vision")
        
        for paper in results:
            assert isinstance(paper, dict)
            assert 'paperId' in paper
            assert 'title' in paper
            assert 'authors' in paper
            assert 'abstract' in paper
            assert 'year' in paper
            assert 'citationCount' in paper
            
            assert isinstance(paper['paperId'], str)
            assert isinstance(paper['title'], str)
            assert isinstance(paper['authors'], list)
            assert isinstance(paper['abstract'], str)
            assert isinstance(paper['year'], int)
            assert isinstance(paper['citationCount'], int)
            
            # Check author structure
            for author in paper['authors']:
                assert isinstance(author, dict)
                assert 'name' in author
    
    def test_mock_search_semantic_scholar(self):
        """Test the mock implementation of search_semantic_scholar."""
        results = mock_search_semantic_scholar("neural networks")
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Test filtering by query
        results = mock_search_semantic_scholar("reinforcement")
        assert len(results) > 0
        for paper in results:
            assert "reinforcement" in paper['title'].lower() or "reinforcement" in paper['abstract'].lower()
    
    def test_semantic_scholar_engine(self):
        """Test the SemanticScholarEngine class."""
        engine = SemanticScholarEngine()
        
        # Test search
        results = engine.search("graph neural")
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Test paper retrieval
        paper_id = results[0]['paperId']
        paper_details = engine.retrieve_paper_details(paper_id)
        assert isinstance(paper_details, dict)
        assert 'paperId' in paper_details
        assert 'fullText' in paper_details
        
        # Test invalid paper ID
        invalid_result = engine.retrieve_paper_details("invalid_id")
        assert 'error' in invalid_result