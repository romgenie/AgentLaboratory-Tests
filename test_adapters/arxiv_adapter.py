"""
ArXiv search adapter for tests.

This module provides adapter functions for the arxiv_search functionality
that tests expect, without modifying the original code.
"""

import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the original function
from agents_tools.arxiv_search import search_arxiv

# Create mock implementation for testing without API calls
def mock_search_arxiv(query, max_results=5):
    """
    Mock implementation of search_arxiv that doesn't require API access.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results
        
    Returns:
        list: List of paper data with predefined test results
    """
    # Extended test data with more varied results
    test_data = [
        {
            'id': '2201.12345',
            'title': 'Advanced Methods in Machine Learning',
            'authors': ['John Smith', 'Jane Doe'],
            'summary': 'This paper presents advanced methods in machine learning.',
            'published': '2022-01-15'
        },
        {
            'id': '2202.54321',
            'title': 'Neural Networks for Time Series Analysis',
            'authors': ['Alice Johnson', 'Bob Williams'],
            'summary': 'This paper explores neural network approaches for time series analysis.',
            'published': '2022-02-20'
        },
        {
            'id': '2203.98765',
            'title': 'Transformer Architectures in Computer Vision',
            'authors': ['Michael Brown', 'Sarah Miller', 'David Chen'],
            'summary': 'This paper investigates the application of transformer architectures to computer vision tasks.',
            'published': '2022-03-10'
        },
        {
            'id': '2204.24680',
            'title': 'Reinforcement Learning for Robotics',
            'authors': ['Emily Wilson', 'Robert Taylor'],
            'summary': 'This paper presents reinforcement learning methods applied to robotic control systems.',
            'published': '2022-04-05'
        },
        {
            'id': '2205.13579',
            'title': 'Graph Neural Networks for Knowledge Representation',
            'authors': ['Thomas Lee', 'Jennifer Garcia', 'Kevin Wang'],
            'summary': 'This paper examines how graph neural networks can be used for complex knowledge representation tasks.',
            'published': '2022-05-22'
        }
    ]
    
    # Filter results based on query (simple substring match for demonstration)
    if query:
        filtered_results = [
            paper for paper in test_data 
            if query.lower() in paper['title'].lower() or 
               query.lower() in paper['summary'].lower()
        ]
    else:
        filtered_results = test_data
    
    # Return up to max_results
    return filtered_results[:max_results]

class ArXivEngine:
    """
    Mock ArXiv engine that simulates API access for testing.
    """
    
    def __init__(self):
        """Initialize the ArXiv engine."""
        self.papers = {
            '2201.12345': 'This is the full text of the first paper about machine learning methods.',
            '2202.54321': 'This is the full text of the second paper about neural networks and time series.',
            '2203.98765': 'This is the full text of the third paper about transformer architectures in computer vision.',
            '2204.24680': 'This is the full text of the fourth paper about reinforcement learning in robotics.',
            '2205.13579': 'This is the full text of the fifth paper about graph neural networks and knowledge representation.'
        }
    
    def retrieve_full_paper_text(self, arxiv_id):
        """
        Retrieve the full text of a paper by its arXiv ID.
        
        Args:
            arxiv_id (str): arXiv ID of the paper
            
        Returns:
            str: Full text of the paper
        """
        return self.papers.get(arxiv_id, f"Paper with ID {arxiv_id} not found")
    
    def search(self, query, max_results=5):
        """
        Search for papers on arXiv.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            list: List of paper data
        """
        return mock_search_arxiv(query, max_results)

# Export the functions and classes
__all__ = ['search_arxiv', 'mock_search_arxiv', 'ArXivEngine']