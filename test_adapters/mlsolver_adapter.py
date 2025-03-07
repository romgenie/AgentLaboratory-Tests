#!/usr/bin/env python3
"""
Adapter for MLSolver module.

This module provides an adapter implementation for the MLSolver module
to facilitate testing without modifying the original code.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
from unittest.mock import MagicMock

class CommandAdapter:
    """Base class adapter for Command implementations."""
    
    def __init__(self, cmd_type="OTHER"):
        self.cmd_type = cmd_type
    
    def docstring(self) -> str:
        """Return the documentation string for the command."""
        return f"Test documentation for {self.cmd_type} command"
    
    def execute_command(self, *args) -> Any:
        """Execute the command with the given arguments."""
        return f"Executed {self.cmd_type} command with args: {args}"
    
    def matches_command(self, cmd_str) -> bool:
        """Check if the command string matches this command type."""
        return self.cmd_type in cmd_str
    
    def parse_command(self, *args) -> Tuple:
        """Parse the command string into arguments for execution."""
        return True, args


class ReplaceAdapter(CommandAdapter):
    """Adapter for Replace command implementation."""
    
    def __init__(self):
        super().__init__(cmd_type="CODE-replace")
    
    def docstring(self) -> str:
        return (
            "============= REWRITE CODE EDITING TOOL =============\n"
            "You also have access to a code replacing tool. \n"
            "This tool allows you to entirely re-write/replace all of the current code and erase all existing code.\n"
            "You can use this tool via the following command: ```REPLACE\n<code here>\n```"
        )
    
    def execute_command(self, *args) -> str:
        args = args[0]
        return args[0]
    
    def matches_command(self, cmd_str) -> bool:
        return "```REPLACE" in cmd_str
    
    def parse_command(self, *args) -> Tuple:
        cmd_str, dataset_code = args[0], args[1]
        # Extract content between ```REPLACE and ``` markers
        start_marker = "```REPLACE"
        end_marker = "```"
        start_idx = cmd_str.find(start_marker) + len(start_marker)
        end_idx = cmd_str.rfind(end_marker)
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return False, (None, "Invalid REPLACE command format",)
        
        new_code = cmd_str[start_idx:end_idx].strip()
        code_ret = f"Test execution output for: {new_code[:20]}..."
        
        # For testing purposes, simulate error if code contains "error"
        if "error" in new_code.lower():
            return False, (None, "[CODE EXECUTION ERROR] Test error in code",)
        
        return True, (new_code.split("\n"), code_ret)


class EditAdapter(CommandAdapter):
    """Adapter for Edit command implementation."""
    
    def __init__(self):
        super().__init__(cmd_type="CODE-edit")
    
    def docstring(self) -> str:
        return (
            "============= CODE EDITING TOOL =============\n"
            "You also have access to a code editing tool. \n"
            "This tool allows you to replace lines indexed n through m (n:m) of the current code with as many lines of new code as you want to add. \n"
            "You can edit code using the following command: ```EDIT N M\n<new lines to replace old lines>\n```"
        )
    
    def execute_command(self, *args) -> Tuple:
        args = args[0]
        try:
            current_code = args[2].copy()  # Make a copy to avoid modifying the original
            start_line, end_line = args[0], args[1]
            new_lines = args[3]
            
            # For testing purposes, simulate error if code contains "error"
            if any("error" in line.lower() for line in new_lines):
                return False, None, "[CODE EXECUTION ERROR] Test error in edited code"
            
            # Replace the specified lines
            if 0 <= start_line <= len(current_code) and 0 <= end_line < len(current_code):
                del current_code[start_line:end_line+1]
                current_code[start_line:start_line] = new_lines
            
            return True, current_code, f"Edit successful, replaced lines {start_line}-{end_line}"
        except Exception as e:
            return False, None, str(e)
    
    def matches_command(self, cmd_str) -> bool:
        return "```EDIT" in cmd_str
    
    def parse_command(self, *args) -> Tuple:
        cmd_str, codelines, dataset_code = args[0], args[1], args[2]
        
        try:
            # Extract content between ```EDIT and ``` markers
            start_marker = "```EDIT"
            end_marker = "```"
            start_idx = cmd_str.find(start_marker) + len(start_marker)
            end_idx = cmd_str.rfind(end_marker)
            
            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return False, (None, None, None, None, None)
            
            content = cmd_str[start_idx:end_idx].strip().split("\n")
            if not content:
                return False, (None, None, None, None, None)
                
            # Parse line numbers
            line_nums = content[0].strip().split()
            if len(line_nums) != 2:
                return False, (None, None, None, None, None)
                
            start_line, end_line = int(line_nums[0]), int(line_nums[1])
            
            # Get the new code
            new_lines = content[1:] if len(content) > 1 else []
            
            return True, (start_line, end_line, codelines, new_lines, dataset_code)
        except Exception as e:
            return False, (None, None, None, None, None)


class MLESolverAdapter:
    """Adapter for MLESolver class."""
    
    def __init__(self, dataset_code, openai_api_key=None, notes=None, max_steps=10, 
                 insights=None, plan=None, llm_str=None):
        """Initialize the MLESolver adapter with test configuration."""
        if notes is None: 
            self.notes = []
        else: 
            self.notes = notes
        
        self.dataset_code = dataset_code
        
        if plan is None: 
            self.plan = ""
        else: 
            self.plan = plan
            
        self.llm_str = llm_str
        self.verbose = False
        self.max_codes = 2
        self.st_hist_len = 2
        self.min_gen_trials = 2
        self.code_lines = []
        self.st_history = []
        self.insights = insights
        self.code_reflect = ""
        self.max_steps = max_steps
        self.prev_code_ret = ""
        self.should_execute_code = True
        self.openai_api_key = openai_api_key
        self.commands = [ReplaceAdapter(), EditAdapter()]
    
    def system_prompt(self, commands=True):
        """Generate a system prompt for testing."""
        return (
            f"[TEST SYSTEM PROMPT]\n"
            f"Role: ML Engineer\n"
            f"Plan: {self.plan}\n"
            f"Insights: {self.insights}\n"
            f"Notes: {self.notes}\n"
            f"Commands: {self.command_descriptions() if commands else 'None'}"
        )
    
    def role_description(self):
        """Return role description for testing."""
        return "You are an expert machine learning engineer working at a top university."
    
    def phase_prompt(self):
        """Return phase prompt for testing."""
        return "You are an ML engineer and you will be writing the code for a research project."
    
    def generate_dataset_descr_prompt(self):
        """Generate dataset description prompt for testing."""
        return f"Dataset code: {self.dataset_code[:50]}..."
    
    def command_descriptions(self):
        """Return command descriptions for testing."""
        return "\n".join([cmd.docstring() for cmd in self.commands])
    
    def process_command(self, cmd_str):
        """Process a command string for testing."""
        for cmd in self.commands:
            if cmd.matches_command(cmd_str):
                if isinstance(cmd, ReplaceAdapter):
                    success, result = cmd.parse_command(cmd_str, self.dataset_code)
                    if success:
                        code_lines, code_ret = result
                        self.code_lines = code_lines
                        self.prev_code_ret = code_ret
                        return cmd_str, code_lines, code_ret, True, 0.85
                    else:
                        return cmd_str, self.code_lines, result[1], False, 0.0
                        
                elif isinstance(cmd, EditAdapter):
                    success, args = cmd.parse_command(cmd_str, self.code_lines, self.dataset_code)
                    if success:
                        success, new_code, msg = cmd.execute_command(args)
                        if success:
                            self.code_lines = new_code
                            self.prev_code_ret = msg
                            return cmd_str, new_code, msg, True, 0.80
                        else:
                            return cmd_str, self.code_lines, msg, False, 0.0
                    else:
                        return cmd_str, self.code_lines, "Invalid command format", False, 0.0
        
        return cmd_str, self.code_lines, "Unknown command", False, 0.0


def get_score(outlined_plan, code, code_return, llm_str=None, attempts=3, openai_api_key=None):
    """Mock implementation of get_score for testing."""
    # Simulate scoring based on code content
    score = 0.85
    
    # Lower score for code with potential issues
    if "error" in code.lower() or "bug" in code.lower():
        score = 0.6
    
    # Higher score for code that mentions the plan elements
    if outlined_plan and any(keyword in code.lower() for keyword in outlined_plan.lower().split()):
        score += 0.1
        
    # Cap score at 1.0
    score = min(score, 1.0)
    
    return score, f"The performance of your submission is: {score}", score > 0.7


def code_repair(code, error, ctype, llm_str=None, openai_api_key=None):
    """Mock implementation of code_repair for testing."""
    if ctype == "replace":
        return "def repaired_function():\n    return 'Fixed code'"
    elif ctype == "edit":
        return "```EDIT 1 2\ndef fixed_function():\n    return 'Fixed code'\n```"
    return code


def execute_code(code_str):
    """Mock implementation of execute_code for testing."""
    if "error" in code_str.lower() or "raise" in code_str.lower():
        return "[CODE EXECUTION ERROR] Test error in code execution"
    return "Code executed successfully with result: 42"


def extract_prompt(text, word):
    """Mock implementation of extract_prompt for testing."""
    start_marker = f"```{word}"
    end_marker = "```"
    
    start_idx = text.find(start_marker) + len(start_marker)
    end_idx = text.rfind(end_marker)
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        return text
        
    return text[start_idx:end_idx].strip()


# Export adapter classes and functions to replace originals
Command = CommandAdapter
Replace = ReplaceAdapter
Edit = EditAdapter
MLESolver = MLESolverAdapter