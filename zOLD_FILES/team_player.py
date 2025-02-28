# Schema definitions for team_player tables
# TODO: Move relevant schema here

from typing import Dict
from models.column import Column, Columns, Index
from models.table_type import TableType

team_player_schema: Dict = {
    "teams": {
        "description": "MLB teams and their affiliations",
        "type": TableType.ENTITY,
        "columns": {
            "id": Columns.ID,
            "name": Columns.varchar(100, nullable=False),
            "team_code": Columns.varchar(10, nullable=False),
            "venue_id": Columns.foreign_key("venues"),
            "league_id": Columns.foreign_key("leagues"),
            "division_id": Columns.foreign_key("divisions"),
            "city": Columns.varchar(100),
            "franchise_name": Columns.varchar(100),
            "active": Columns.ACTIVE,
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["team_code"], name="idx_teams_code"),
            Index(["name"], name="idx_teams_name"),
            Index(["venue_id"], name="idx_teams_venue"),
            Index(["league_id"], name="idx_teams_league"),
            Index(["division_id"], name="idx_teams_division")
        ]
    },
    "players": {
        "description": "MLB players and their basic information",
        "type": TableType.ENTITY,
        "columns": {
            "id": Columns.ID,
            "full_name": Columns.varchar(100, nullable=False),
            "first_name": Columns.varchar(50),
            "last_name": Columns.varchar(50),
            "primary_number": Columns.varchar(10),
            "birth_date": Column("DATE"),
            "current_team_id": Columns.foreign_key("teams"),
            "position_code": Columns.varchar(10),
            "position_name": Columns.varchar(50),
            "status": Columns.varchar(20),
            "bat_side": Column("CHAR(1)"),
            "pitch_hand": Column("CHAR(1)"),
            "active": Columns.ACTIVE,
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["full_name"], name="idx_players_name"),
            Index(["current_team_id"], name="idx_players_team"),
            Index(["position_code"], name="idx_players_position"),
            Index(["status"], name="idx_players_status")
        ]
    }
}
