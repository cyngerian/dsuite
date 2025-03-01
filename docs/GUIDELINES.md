# Baseball Statistics Tracking System - Development Guidelines

## Project Rules
```json
{
    "rules": [
        "You are helping develop a baseball statistics tracking system (STS) using Docker, Python, R, MinIO, and PostgreSQL.",
        "Always include type hints in Python code.",
        "Follow PEP 8 style guidelines for Python code.",
        "Include detailed docstrings for all functions and classes.",
        "Use async/await for API calls and I/O operations where appropriate.",
        "Implement proper error handling and logging.",
        "Write unit tests for all new functionality.",
        "Use environment variables for configuration where appropriate.",
        "Follow the principle of separation of concerns.",
        "Include comments explaining complex logic.",
        "Use meaningful variable and function names.",
        "Implement proper input validation.",
        "Follow REST API best practices for endpoints.",
        "Use proper SQL query optimization techniques.",
        "Document all API endpoints and their parameters.",
        "Follow security best practices, especially for database and API access.",
        "Use proper version control practices with meaningful commit messages.",
        "Implement proper logging and monitoring.",
        "Follow Docker best practices and optimize container builds.",
        "Write idiomatic R code following tidyverse principles for the Shiny app.",
        "Always check Eastern time using 'TZ='America/New_York' date' before adding timestamps to documentation, especially PROJECT_STATUS.md",
        "Design all components with message bus integration in mind:",
        "  - Plan for event-driven architecture from the start",
        "  - Define clear event schemas for all data changes",
        "  - Implement proper event versioning",
        "  - Consider message replay requirements",
        "  - Plan for eventual consistency",
        "  - Document event flows and schemas",
        "  - Implement proper error handling for events",
        "  - Consider event ordering and idempotency",
        "  - Plan for event schema evolution",
        "Create daily implementation plan files:",
        "  - Create file PLAN_[yyyy-MM-dd].md in docs/implementation/ for each implementation day",
        "  - Include detailed milestones and testing plans",
        "  - Document success criteria and risk mitigation",
        "  - Track progress with morning and evening reviews",
        "  - Update implementation status in PROJECT_STATUS.md",
        "  - Cross-reference implementation plans in documentation"
    ]
}
```

## Command Running Rules
1. ALWAYS run commands in the chat using the run_terminal_cmd tool
2. ALWAYS show the command output in the chat
3. For sequential commands that should be run together, use && between commands
4. For commands that need separate verification or produce important output, use individual code blocks
5. Label each command block with a number and brief description
6. Use bash syntax highlighting for command blocks
7. Format command examples as:

1. Description of first command set:
```bash
command1 && \
command2 && \
command3
```

2. Description of separate command:
```bash
command4
```

## Project Status Updates
After every 5 responses, update PROJECT_STATUS.md with:
1. Recent changes (last 5 interactions)
2. Current state of the project
3. Next immediate steps
4. Known issues
5. Last updated timestamp (in Eastern Time)

Format PROJECT_STATUS.md in markdown with clear sections and always add new updates at the top of the file, preserving the history.

## Environment Information
```json
{
    "OS": "win32 10.0.22631",
    "Workspace": "vscode-remote://ssh-remote%2Bdingersuite/home/airbaggie/dsuite",
    "Shell": "/bin/bash"
}
```
