"""Game and play schema definitions."""

from typing import Any, Dict

game_play_schema: Dict[str, Dict[str, Any]] = {
    "games": {
        "description": "Baseball game information",
        "columns": {
            "game_id": "INTEGER PRIMARY KEY",
            "game_date": "DATE NOT NULL",
            "home_team_id": "INTEGER REFERENCES teams(team_id)",
            "away_team_id": "INTEGER REFERENCES teams(team_id)",
            "venue_id": "INTEGER REFERENCES venues(venue_id)",
            "game_type": "VARCHAR(1) NOT NULL",
            "status": "VARCHAR(20) NOT NULL",
            "start_time": "TIMESTAMP",
            "end_time": "TIMESTAMP",
            "attendance": "INTEGER",
            "weather": "VARCHAR(100)",
            "wind": "VARCHAR(50)",
        },
        "indexes": ["game_date", "home_team_id", "away_team_id"],
    },
    "plays": {
        "description": "Individual play events in games",
        "columns": {
            "play_id": "INTEGER PRIMARY KEY",
            "game_id": "INTEGER REFERENCES games(game_id)",
            "inning": "INTEGER NOT NULL",
            "top_inning": "BOOLEAN NOT NULL",
            "batter_id": "INTEGER REFERENCES players(player_id)",
            "pitcher_id": "INTEGER REFERENCES players(player_id)",
            "play_type": "VARCHAR(50) NOT NULL",
            "event": "VARCHAR(100) NOT NULL",
            "description": "TEXT",
            "runs_scored": "INTEGER",
            "outs_recorded": "INTEGER",
            "rbi": "INTEGER",
            "is_hit": "BOOLEAN",
            "is_error": "BOOLEAN",
        },
        "indexes": ["game_id", "inning", "batter_id", "pitcher_id"],
    },
}
