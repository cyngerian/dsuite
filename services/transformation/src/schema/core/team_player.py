"""Team and player schema definitions."""

from typing import Any, Dict

team_player_schema: Dict[str, Dict[str, Any]] = {
    "teams": {
        "description": "Team information",
        "columns": {
            "team_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100) NOT NULL",
            "city": "VARCHAR(100) NOT NULL",
            "abbreviation": "VARCHAR(3) NOT NULL",
            "league": "VARCHAR(2) NOT NULL",
            "division": "VARCHAR(10) NOT NULL",
        },
        "indexes": ["name", "abbreviation"],
    },
    "players": {
        "description": "Player information",
        "columns": {
            "player_id": "INTEGER PRIMARY KEY",
            "first_name": "VARCHAR(50) NOT NULL",
            "last_name": "VARCHAR(50) NOT NULL",
            "number": "INTEGER",
            "position": "VARCHAR(2) NOT NULL",
            "team_id": "INTEGER REFERENCES teams(team_id)",
        },
        "indexes": ["last_name", "team_id"],
    },
}
