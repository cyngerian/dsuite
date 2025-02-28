#!/usr/bin/env python3
"""
Script to update PROJECT_STATUS.md with recent changes and current state.
"""
from datetime import datetime
import sys
from typing import List, Optional


def read_status_file() -> List[str]:
    """
    Read the current PROJECT_STATUS.md file.
    
    Returns:
        List[str]: Lines from the status file
    """
    try:
        with open('PROJECT_STATUS.md', 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        print("Error: PROJECT_STATUS.md not found")
        sys.exit(1)


def find_section_bounds(lines: List[str], section_name: str) -> tuple[int, Optional[int]]:
    """
    Find the start and end lines of a section in the status file.
    
    Args:
        lines: List of file lines
        section_name: Name of the section to find
    
    Returns:
        tuple[int, Optional[int]]: Start and end line numbers
    """
    start = -1
    end = None
    
    for i, line in enumerate(lines):
        if line.strip() == f"## {section_name}":
            start = i
        elif start != -1 and line.startswith("##"):
            end = i
            break
    
    return start, end


def update_recent_changes(lines: List[str], new_change: str) -> List[str]:
    """
    Update the Recent Changes section with a new change.
    
    Args:
        lines: Current file lines
        new_change: New change to add
    
    Returns:
        List[str]: Updated file lines
    """
    start, end = find_section_bounds(lines, "Recent Changes (last 5 interactions)")
    if start == -1:
        print("Error: Could not find Recent Changes section")
        return lines
    
    # Extract current changes
    changes = []
    i = start + 1
    while i < len(lines) and i != end and lines[i].strip():
        if lines[i].strip().startswith(str(len(changes) + 1) + '.'):
            changes.append(lines[i].strip()[3:].strip())
        i += 1
    
    # Add new change and keep only last 5
    changes.insert(0, new_change)
    changes = changes[:5]
    
    # Create updated lines
    updated_lines = lines[:start + 1]
    updated_lines.extend(f"{i+1}. {change}\n" for i, change in enumerate(changes))
    updated_lines.append("\n")
    updated_lines.extend(lines[end:] if end else lines[i+1:])
    
    return updated_lines


def update_timestamp(lines: List[str]) -> List[str]:
    """
    Update the Last Updated timestamp.
    
    Args:
        lines: Current file lines
    
    Returns:
        List[str]: Updated file lines
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start, _ = find_section_bounds(lines, "Last Updated")
    
    if start != -1:
        lines[start + 1] = f"{timestamp}\n"
    
    return lines


def update_status(new_change: str) -> None:
    """
    Update PROJECT_STATUS.md with a new change.
    
    Args:
        new_change: Description of the new change
    """
    lines = read_status_file()
    lines = update_recent_changes(lines, new_change)
    lines = update_timestamp(lines)
    
    with open('PROJECT_STATUS.md', 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_status.py 'Description of change'")
        sys.exit(1)
    
    update_status(sys.argv[1]) 