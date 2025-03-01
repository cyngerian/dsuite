"""Test module for game file analysis."""

import os
from typing import Any, Dict, List, Set, TypeVar
from unittest.mock import Mock, patch

import pytest

from scripts.schema_analysis import (
    SchemaAnalyzer,
    analyze_game_files,
    extract_field_types,
    get_field_type,
)

T = TypeVar("T")

# Fix type hints for MinIO configuration
MINIO_CONFIG: dict[str, str] = {
    "endpoint": str(os.getenv("MINIO_ENDPOINT", "localhost:9000")),
    "access_key": str(os.getenv("MINIO_ACCESS_KEY", "minioadmin")),
    "secret_key": str(os.getenv("MINIO_SECRET_KEY", "minioadmin")),
}


@pytest.fixture
def sample_game_data() -> Dict[str, Any]:
    """Sample game data for testing."""
    return {
        "game": {
            "id": "12345",
            "date": "2024-03-19",
            "status": "Final",
            "teams": {
                "home": {
                    "name": "Yankees",
                    "score": 5,
                    "players": [
                        {"id": "1", "name": "Player 1"},
                        {"id": "2", "name": "Player 2"},
                    ],
                },
                "away": {
                    "name": "Red Sox",
                    "score": 3,
                    "players": [
                        {"id": "3", "name": "Player 3"},
                        {"id": "4", "name": "Player 4"},
                    ],
                },
            },
        }
    }


def test_analyze_json_structure(sample_game_data: Dict[str, Any]) -> None:
    """Test JSON structure analysis."""
    analyzer = SchemaAnalyzer()
    schema = analyzer.analyze_json_structure(sample_game_data)

    # Check top-level structure
    assert "game" in schema
    assert schema["game"] == {"object"}

    # Check nested fields
    assert "game.id" in schema
    assert schema["game.id"] == {"str"}

    # Check array handling
    assert "game.teams.home.players" in schema
    assert schema["game.teams.home.players"] == {"array"}

    # Check array item structure
    assert "game.teams.home.players[].id" in schema
    assert schema["game.teams.home.players[].id"] == {"str"}


def test_merge_schemas() -> None:
    """Test schema merging."""
    analyzer = SchemaAnalyzer()

    schema1: Dict[str, Set[str]] = {"field1": {"str"}, "field2": {"int"}}

    schema2: Dict[str, Set[str]] = {
        "field1": {"str"},
        "field2": {"float"},
        "field3": {"bool"},
    }

    merged = analyzer.merge_schemas([schema1, schema2])

    assert merged["field1"] == {"str"}
    assert merged["field2"] == {"int", "float"}
    assert merged["field3"] == {"bool"}


@patch("scripts.schema_analysis.analyze_game_files.Minio")
def test_get_sample_files(mock_minio_class: Mock) -> None:
    """Test sample file retrieval."""
    # Create mock objects
    mock_obj1 = Mock()
    mock_obj1.object_name = "game1.json"
    mock_obj2 = Mock()
    mock_obj2.object_name = "game2.json"

    # Create mock client instance
    mock_client = Mock()
    mock_client.list_objects.return_value = [mock_obj1, mock_obj2]

    # Make the mock class return our mock client
    mock_minio_class.return_value = mock_client

    analyzer = SchemaAnalyzer()
    files = analyzer.get_sample_files("test-bucket")

    # Verify the mock was called correctly
    mock_client.list_objects.assert_called_once_with("test-bucket")

    # Verify results
    assert len(files) == 2
    assert files == ["game1.json", "game2.json"]


@pytest.mark.asyncio
async def test_analyze_game_files() -> None:
    """Test analyzing game files."""
    result = await analyze_game_files("test_data/")
    # Check if result is a dictionary without using isinstance
    assert type(result) is dict
    assert "games" in result
    assert "plays" in result


def test_get_field_type() -> None:
    """Test getting field type from value."""
    test_cases: List[Dict[str, Any]] = [
        {"value": 1, "expected": "INTEGER"},
        {"value": 1.0, "expected": "FLOAT"},
        {"value": "test", "expected": "VARCHAR"},
        {"value": True, "expected": "BOOLEAN"},
        {"value": None, "expected": "NULL"},
        {"value": [], "expected": "ARRAY"},
        {"value": {}, "expected": "JSONB"},
    ]

    for case in test_cases:
        assert get_field_type(case["value"]) == case["expected"]


def test_extract_field_types() -> None:
    """Test extracting field types from data."""
    test_data: List[Dict[str, Any]] = [
        {"id": 1, "name": "Test", "active": True},
        {"id": 2, "name": "Test 2", "score": 10.5},
    ]

    result = extract_field_types(test_data)
    # Check if result is a dictionary without using isinstance
    assert type(result) is dict
    assert result["id"] == "INTEGER"
    assert result["name"] == "VARCHAR"
    assert result["active"] == "BOOLEAN"
    assert result["score"] == "FLOAT"
