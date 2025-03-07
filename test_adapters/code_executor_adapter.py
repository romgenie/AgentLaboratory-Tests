#!/usr/bin/env python3
"""
Adapter for Code Executor tool.

This module provides an adapter implementation for the code executor tool
to facilitate testing without modifying the original code.
"""

from typing import Dict, List, Optional, Any, Union
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
import matplotlib.pyplot as plt
import base64

class CodeExecutorAdapter:
    """Adapter for the Code Executor tool."""
    
    @staticmethod
    def execute_code(code: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute Python code in a controlled environment and return results.
        
        Args:
            code (str): The Python code to execute
            timeout (int): Maximum execution time in seconds
            
        Returns:
            dict: Dictionary containing execution results:
                - output: Captured stdout output
                - error: Error message if execution failed, None otherwise
                - figures: List of base64-encoded figures if any were generated
        """
        # Capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Reset matplotlib figures
        plt.close('all')
        
        # Initialize result
        result = {
            'output': '',
            'error': None,
            'figures': []
        }
        
        # Execute the code
        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Execute code with timeout handling
                exec(code, {'plt': plt})
                
            # Capture output
            result['output'] = stdout_buffer.getvalue()
            
            # Capture figures if any were created
            if plt.get_fignums():
                for i in plt.get_fignums():
                    figure = plt.figure(i)
                    buf = io.BytesIO()
                    figure.savefig(buf, format='png')
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    result['figures'].append(img_str)
                
        except Exception as e:
            # Capture the error
            result['error'] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
        # Include stderr output in the error if present
        stderr_output = stderr_buffer.getvalue()
        if stderr_output and not result['error']:
            result['error'] = stderr_output
            
        return result

# Export the adapter method to replace the original
execute_code = CodeExecutorAdapter.execute_code