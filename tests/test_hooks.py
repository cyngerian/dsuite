"""Test module for demonstrating pre-commit hooks functionality."""

from typing import Any


def process_game_data(game_id: str, stats: dict[str, Any]) -> dict[str, Any]:
    """Process game statistics data.

    Args:
        game_id: Unique identifier for the game.
        stats: Dictionary containing game statistics.

    Returns:
        Processed game statistics with additional data.
    """
    result: list[int] = []

    for i in range(10):
        result.append(i)

    return {"game_id": game_id, "stats": stats, "data": result}


class GameProcessor:
    """Process game data with proper type annotations."""

    def __init__(self) -> None:
        """Initialize the GameProcessor."""
        self.data: dict[str, Any] = {}

    def process(self, data: dict[str, Any]) -> None:
        """Process the game data.

        Args:
            data: Dictionary containing game data to process.
        """
        self.data = data
