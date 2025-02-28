<custom_instructions>
{
    "rules": [
        "You are helping develop a baseball statistics tracking system (STS) using Docker, Python, R, MinIO, and PostgreSQL.",
        ... (your existing rules)
    ]
}
</custom_instructions>

<command_instructions>
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
</command_instructions>

<environment>
OS: win32 10.0.22631
Workspace: vscode-remote://ssh-remote%2Bdingersuite/home/airbaggie/dsuite
Shell: /bin/bash
</environment>
