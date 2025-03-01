"""Tests for schema normalization module."""

from typing import Any, Dict, List, Set, Tuple

import pytest

from .normalize import (
    analyze_and_normalize_schema,
    generate_migration_sql,
    generate_table_definitions,
    identify_entities,
    suggest_relationships,
)


@pytest.fixture
def sample_schema() -> Dict[str, Set[str]]:
    """Sample schema for testing."""
    return {
        "game": {"object"},
        "game.id": {"str"},
        "game.date": {"str"},
        "game.teams": {"object"},
        "game.teams.home": {"object"},
        "game.teams.home.id": {"int"},
        "game.teams.home.name": {"str"},
        "game.teams.home.players": {"array"},
        "game.teams.home.players[]": {"object"},
        "game.teams.home.players[].id": {"int"},
        "game.teams.home.players[].name": {"str"},
        "game.teams.home.players[].position": {"str"},
        "game.teams.away": {"object"},
        "game.teams.away.id": {"int"},
        "game.teams.away.name": {"str"},
        "game.teams.away.players": {"array"},
        "game.teams.away.players[]": {"object"},
        "game.teams.away.players[].id": {"int"},
        "game.teams.away.players[].name": {"str"},
        "game.teams.away.players[].position": {"str"},
    }


def test_identify_entities(sample_schema: Dict[str, Set[str]]) -> None:
    """Test entity identification from schema."""
    entities = identify_entities(sample_schema)

    # Check that we got the expected entities
    entity_names = [name for name, _ in entities]
    assert "root" in entity_names
    assert "teams" in entity_names
    assert "players" in entity_names

    # Check fields in players entity
    players_fields = next(fields for name, fields in entities if name == "players")
    assert "id" in players_fields
    assert "name" in players_fields
    assert "position" in players_fields

    # Check fields in teams entity
    teams_fields = next(fields for name, fields in entities if name == "teams")
    assert "id" in teams_fields
    assert "name" in teams_fields


def test_suggest_relationships(sample_schema: Dict[str, Set[str]]) -> None:
    """Test relationship suggestion between entities."""
    entities = identify_entities(sample_schema)
    relationships = suggest_relationships(entities)

    # Convert to set of tuples for easier testing
    rel_set = {(f, t, r) for f, t, r in relationships}

    # Check for expected relationships
    assert ("teams", "players", "one_to_many") in rel_set


def test_generate_table_definitions() -> None:
    """Test generation of table definitions."""
    entities: List[Tuple[str, Dict[str, str]]] = [
        ("teams", {"id": "INTEGER", "name": "VARCHAR"}),
        ("players", {"id": "INTEGER", "name": "VARCHAR", "position": "VARCHAR"}),
    ]
    relationships = [("teams", "players", "one_to_many")]

    tables = generate_table_definitions(entities, relationships)

    # Check teams table
    assert "teams" in tables
    assert "id" in tables["teams"]["fields"]
    assert "name" in tables["teams"]["fields"]

    # Check players table
    assert "players" in tables
    assert "teams_id" in tables["players"]["fields"]  # Foreign key added
    assert len(tables["players"]["foreign_keys"]) == 1


def test_generate_migration_sql() -> None:
    """Test generating SQL migration statements."""
    table_definitions: Dict[str, Dict[str, Any]] = {
        "teams": {
            "fields": {"id": "SERIAL", "name": "VARCHAR"},
            "primary_key": "id",
            "foreign_keys": [],
            "indexes": ["id"],
        }
    }

    sql = generate_migration_sql(table_definitions)

    # Check for key SQL components
    assert "CREATE TABLE teams" in sql
    assert "id SERIAL PRIMARY KEY" in sql
    assert "name VARCHAR" in sql


def test_analyze_and_normalize_schema(sample_schema: Dict[str, Set[str]]) -> None:
    """Test complete schema analysis and normalization."""
    entities, sql = analyze_and_normalize_schema(sample_schema)

    # Check entities were created
    entity_names = [name for name, _ in entities]
    assert "root" in entity_names
    assert "teams" in entity_names
    assert "players" in entity_names

    # Check SQL was generated
    assert "CREATE TABLE" in sql
    assert "FOREIGN KEY" in sql
    assert "CREATE INDEX" in sql
