"""
Semantic Scholar search adapter for tests.

This module provides adapter functions for the semantic_scholar_search functionality
that tests expect, without modifying the original code.
"""

import sys
import os

# Add project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the original function
from agents_tools.semantic_scholar_search import search_semantic_scholar

# Create mock implementation for testing without API calls
def mock_search_semantic_scholar(query, max_results=5):
    """
    Mock implementation of search_semantic_scholar that doesn't require API access.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results
        
    Returns:
        list: List of paper data with predefined test results
    """
    # Extended test data with more varied results
    test_data = [
        {
            'paperId': 'abc123',
            'title': 'Deep Learning in Natural Language Processing',
            'authors': [{'name': 'John Smith'}, {'name': 'Jane Doe'}],
            'abstract': 'This paper explores deep learning approaches in NLP.',
            'year': 2021,
            'citationCount': 150
        },
        {
            'paperId': 'def456',
            'title': 'Transformers for Computer Vision',
            'authors': [{'name': 'Alice Johnson'}, {'name': 'Bob Williams'}],
            'abstract': 'This paper applies transformer architectures to computer vision tasks.',
            'year': 2022,
            'citationCount': 75
        },
        {
            'paperId': 'ghi789',
            'title': 'Reinforcement Learning in Robotics',
            'authors': [{'name': 'Michael Brown'}, {'name': 'Sarah Miller'}],
            'abstract': 'This paper discusses applications of reinforcement learning to robotic systems.',
            'year': 2023,
            'citationCount': 42
        },
        {
            'paperId': 'jkl012',
            'title': 'Graph Neural Networks for Knowledge Graphs',
            'authors': [{'name': 'Emily Wilson'}, {'name': 'David Chen'}, {'name': 'Robert Taylor'}],
            'abstract': 'This paper presents novel approaches for knowledge representation using graph neural networks.',
            'year': 2022,
            'citationCount': 94
        },
        {
            'paperId': 'mno345',
            'title': 'Advances in Few-Shot Learning',
            'authors': [{'name': 'Thomas Lee'}, {'name': 'Jennifer Garcia'}],
            'abstract': 'This paper surveys recent advances in few-shot learning techniques.',
            'year': 2023,
            'citationCount': 63
        }
    ]
    
    # Filter results based on query (simple substring match for demonstration)
    if query:
        filtered_results = [
            paper for paper in test_data 
            if query.lower() in paper['title'].lower() or 
               query.lower() in paper['abstract'].lower()
        ]
    else:
        filtered_results = test_data
    
    # Return up to max_results
    return filtered_results[:max_results]

class SemanticScholarEngine:
    """
    Mock Semantic Scholar engine that simulates API access for testing.
    """
    
    def __init__(self):
        """Initialize the Semantic Scholar engine."""
        self.papers = {
            'abc123': 'This is the full text of the paper about deep learning in NLP.',
            'def456': 'This is the full text of the paper about transformers for computer vision.',
            'ghi789': 'This is the full text of the paper about reinforcement learning in robotics.',
            'jkl012': 'This is the full text of the paper about graph neural networks for knowledge graphs.',
            'mno345': 'This is the full text of the paper about advances in few-shot learning.'
        }
        self.citations = {
            'abc123': [
                {'paperId': 'ref123', 'title': 'Earlier Work on NLP', 'year': 2019},
                {'paperId': 'ref456', 'title': 'Foundations of Deep Learning', 'year': 2018}
            ],
            'def456': [
                {'paperId': 'ref789', 'title': 'Vision Transformers', 'year': 2021},
                {'paperId': 'ref012', 'title': 'Attention Mechanisms', 'year': 2020}
            ]
        }
    
    def retrieve_paper_details(self, paper_id):
        """
        Retrieve the full details of a paper by its ID.
        
        Args:
            paper_id (str): ID of the paper
            
        Returns:
            dict: Full details of the paper
        """
        if paper_id in self.papers:
            # Find the paper in the test data
            test_data = mock_search_semantic_scholar("", max_results=10)
            for paper in test_data:
                if paper['paperId'] == paper_id:
                    return {
                        **paper,
                        'fullText': self.papers[paper_id],
                        'references': self.citations.get(paper_id, [])
                    }
        
        return {'error': f"Paper with ID {paper_id} not found"}
    
    def search(self, query, max_results=5):
        """
        Search for papers on Semantic Scholar.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            list: List of paper data
        """
        return mock_search_semantic_scholar(query, max_results)

# Export the functions and classes
__all__ = ['search_semantic_scholar', 'mock_search_semantic_scholar', 'SemanticScholarEngine']