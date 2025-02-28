# Schema definitions for reference tables
# TODO: Move relevant schema here

from typing import Dict
from ..models.column import Column, Columns, Index
from ..models.table_type import TableType

reference_schema: Dict = {
    "leagues": {
        "description": "MLB leagues (American and National)",
        "type": TableType.REFERENCE,
        "columns": {
            "id": Columns.ID,
            "name": Columns.varchar(100, nullable=False),
            "abbreviation": Columns.varchar(10),
            "active": Columns.ACTIVE,
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["name"], name="idx_leagues_name")
        ]
    },
    "divisions": {
        "description": "MLB divisions (East, Central, West)",
        "type": TableType.REFERENCE,
        "columns": {
            "id": Columns.ID,
            "league_id": Columns.foreign_key("leagues", nullable=False),
            "name": Columns.varchar(100, nullable=False),
            "abbreviation": Columns.varchar(10),
            "active": Columns.ACTIVE,
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["league_id"], name="idx_divisions_league"),
            Index(["name"], name="idx_divisions_name")
        ]
    },
    "venues": {
        "description": "MLB ballparks and stadiums",
        "type": TableType.REFERENCE,
        "columns": {
            "id": Column("INTEGER", nullable=False, primary_key=True),
            "name": Columns.varchar(100, nullable=False),
            "city": Columns.varchar(100),
            "state": Columns.varchar(50),
            "country": Columns.varchar(50),
            "latitude": Columns.decimal(9, 6),
            "longitude": Columns.decimal(9, 6),
            "altitude": Column("INTEGER"),
            "timezone": Columns.varchar(50),
            "capacity": Column("INTEGER"),
            "surface_type": Columns.varchar(50),
            "roof_type": Columns.varchar(50),
            "created_at": Columns.CREATED_AT,
            "updated_at": Columns.UPDATED_AT
        },
        "indices": [
            Index(["name"], name="idx_venues_name"),
            Index(["city", "state", "country"], name="idx_venues_location")
        ]
    }
}
