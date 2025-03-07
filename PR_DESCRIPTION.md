## Add test framework for AgentLaboratory

This PR introduces a comprehensive test framework designed for the current file structure of AgentLaboratory, including:

- Unit tests for core functionality (extract_json, BaseAgent, simple validations)
- Integration tests for agent collaboration
- Test adapters that maintain separation between test and production code
- Test fixtures and configuration for reusability
- Test runner to simplify test execution

All included tests pass successfully and provide a foundation for continued testing as the project evolves.