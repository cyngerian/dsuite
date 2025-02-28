# Schema definitions for game_play tables
# TODO: Move relevant schema here

from typing import Dict
from ..models.column import Column, Columns, Index
from ..models.table_type import TableType

game_play_schema: Dict = {
    "games": {
        "description": "MLB games and their basic information",
        "type": TableType.EVENT,
        "columns": {
            "id": Columns.ID,
            "game_date": Column("DATE", nullable=False),
            "game_type": Columns.varchar(10),
            "season": Column("INTEGER"),
            "home_team_id": Columns.foreign_key("teams", nullable=False),
            "away_team_id": Columns.foreign_key("teams", nullable=False),
            "venue_id": Columns.foreign_key("venues"),
            "status": Columns.varchar(50),
            "start_time": Column("TIMESTAMP"),
            "end_time": Column("TIMESTAMP"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["game_date"], name="idx_games_date"),
            Index(["home_team_id", "away_team_id"], name="idx_games_teams"),
            Index(["season"], name="idx_games_season"),
            Index(["venue_id"], name="idx_games_venue")
        ]
    },
    "plays": {
        "description": "Individual plays within MLB games",
        "type": TableType.EVENT,
        "columns": {
            "play_id": Columns.ID,
            "game_id": Columns.foreign_key("games", nullable=False),
            "about_atBatIndex": Column("INTEGER"),
            "about_inning": Column("INTEGER"),
            "about_isTopInning": Column("BOOLEAN"),
            "about_hasOut": Column("BOOLEAN"),
            "about_isScoringPlay": Column("BOOLEAN"),
            "about_isComplete": Column("BOOLEAN"),
            "about_hasReview": Column("BOOLEAN"),
            "about_startTime": Column("TIMESTAMP"),
            "about_endTime": Column("TIMESTAMP"),
            "result_type": Columns.varchar(50),
            "result_event": Columns.varchar(100),
            "result_eventType": Columns.varchar(50),
            "result_description": Column("TEXT"),
            "result_rbi": Column("INTEGER"),
            "result_awayScore": Column("INTEGER"),
            "result_homeScore": Column("INTEGER"),
            "result_isOut": Column("BOOLEAN"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["game_id"], name="idx_plays_game"),
            Index(["about_inning", "about_isTopInning"], name="idx_plays_inning"),
            Index(["about_isScoringPlay"], name="idx_plays_scoring"),
            Index(["about_hasReview"], name="idx_plays_review")
        ]
    }
}
