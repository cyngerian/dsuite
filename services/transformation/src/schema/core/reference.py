"""Reference data schema definitions."""

from typing import Any, Dict

from ..models.column import Index
from ..models.table_type import TableType

reference_schema: Dict[str, Dict[str, Any]] = {
    "leagues": {
        "description": "Baseball leagues",
        "type": TableType.REFERENCE,
        "columns": {
            "league_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(50) NOT NULL",
            "abbreviation": "VARCHAR(5) NOT NULL",
        },
        "indices": [
            Index(["name"], name="idx_leagues_name"),
            Index(["abbreviation"], name="idx_leagues_abbreviation"),
        ],
    },
    "divisions": {
        "description": "League divisions",
        "type": TableType.REFERENCE,
        "columns": {
            "division_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(50) NOT NULL",
            "abbreviation": "VARCHAR(5) NOT NULL",
            "league_id": "INTEGER REFERENCES leagues(league_id)",
        },
        "indices": [
            Index(["name"], name="idx_divisions_name"),
            Index(["league_id"], name="idx_divisions_league"),
        ],
    },
    "venues": {
        "description": "Baseball venues and stadiums",
        "type": TableType.REFERENCE,
        "columns": {
            "venue_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100) NOT NULL",
            "city": "VARCHAR(100) NOT NULL",
            "state": "VARCHAR(2)",
            "country": "VARCHAR(50) NOT NULL",
            "capacity": "INTEGER",
            "surface": "VARCHAR(50)",
            "roof_type": "VARCHAR(20)",
        },
        "indices": [
            Index(["name"], name="idx_venues_name"),
            Index(["city"], name="idx_venues_city"),
        ],
    },
}
