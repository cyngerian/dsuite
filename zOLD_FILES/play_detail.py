# Schema definitions for play_detail tables
# TODO: Move relevant schema here

from typing import Dict
from models.column import Column, Columns, Index
from models.table_type import TableType

play_detail_schema: Dict = {
    "play_events": {
        "description": "Detailed events within each play",
        "type": TableType.EVENT,
        "columns": {
            "event_id": Columns.ID,
            "play_id": Columns.foreign_key("plays", nullable=False),
            "event_index": Column("INTEGER"),
            "type": Columns.varchar(50),
            "is_pitch": Column("BOOLEAN"),
            "is_substitution": Column("BOOLEAN"),
            "details_description": Column("TEXT"),
            "details_event": Columns.varchar(100),
            "details_eventType": Columns.varchar(50),
            "details_isScoringPlay": Column("BOOLEAN"),
            "details_isOut": Column("BOOLEAN"),
            "details_isInPlay": Column("BOOLEAN"),
            "details_isBall": Column("BOOLEAN"),
            "details_isStrike": Column("BOOLEAN"),
            "start_time": Column("TIMESTAMP"),
            "end_time": Column("TIMESTAMP"),
            "batting_order": Column("INTEGER"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["play_id"], name="idx_events_play"),
            Index(["type"], name="idx_events_type"),
            Index(["details_isScoringPlay"], name="idx_events_scoring")
        ]
    },
    "pitch_data": {
        "description": "Detailed pitch tracking data",
        "type": TableType.EVENT,
        "columns": {
            "pitch_id": Columns.ID,
            "event_id": Columns.foreign_key("play_events", nullable=False),
            "start_speed": Columns.decimal(6, 2),
            "end_speed": Columns.decimal(6, 2),
            "zone": Column("INTEGER"),
            "type_confidence": Columns.decimal(6, 3),
            "plate_time": Columns.decimal(6, 3),
            "extension": Columns.decimal(6, 3),
            "strike_zone_top": Columns.decimal(6, 3),
            "strike_zone_bottom": Columns.decimal(6, 3),
            "coordinates_x": Columns.decimal(8, 3),
            "coordinates_y": Columns.decimal(8, 3),
            "coordinates_pX": Columns.decimal(8, 3),
            "coordinates_pZ": Columns.decimal(8, 3),
            "coordinates_pfxX": Columns.decimal(8, 3),
            "coordinates_pfxZ": Columns.decimal(8, 3),
            "coordinates_vX0": Columns.decimal(8, 3),
            "coordinates_vY0": Columns.decimal(8, 3),
            "coordinates_vZ0": Columns.decimal(8, 3),
            "coordinates_aX": Columns.decimal(8, 3),
            "coordinates_aY": Columns.decimal(8, 3),
            "coordinates_aZ": Columns.decimal(8, 3),
            "breaks_spinRate": Column("INTEGER"),
            "breaks_spinDirection": Columns.decimal(8, 3),
            "breaks_breakAngle": Columns.decimal(8, 3),
            "breaks_breakLength": Columns.decimal(8, 3),
            "breaks_breakY": Columns.decimal(8, 3),
            "breaks_breakVertical": Columns.decimal(8, 3),
            "breaks_breakHorizontal": Columns.decimal(8, 3),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["event_id"], name="idx_pitch_event"),
            Index(["start_speed"], name="idx_pitch_speed"),
            Index(["zone"], name="idx_pitch_zone"),
            Index(["breaks_spinRate"], name="idx_pitch_spin")
        ]
    },
    "hit_data": {
        "description": "Hit data and outcomes",
        "type": TableType.EVENT,
        "columns": {
            "hit_id": Columns.ID,
            "event_id": Columns.foreign_key("play_events", nullable=False),
            "launch_speed": Columns.decimal(5, 2),
            "launch_angle": Columns.decimal(5, 2),
            "total_distance": Column("INTEGER"),
            "trajectory": Columns.varchar(50),
            "hardness": Columns.varchar(50),
            "location": Columns.varchar(50),
            "coordinates_x": Columns.decimal(6, 3),
            "coordinates_y": Columns.decimal(6, 3),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["event_id"], name="idx_hit_event"),
            Index(["launch_speed", "launch_angle"], name="idx_hit_launch"),
            Index(["total_distance"], name="idx_hit_distance")
        ]
    },
    "runners": {
        "description": "Runner movements and outcomes",
        "type": TableType.EVENT,
        "columns": {
            "runner_id": Columns.ID,
            "play_id": Columns.foreign_key("plays", nullable=False),
            "player_id": Columns.foreign_key("players", nullable=False),
            "start_base": Columns.varchar(10),
            "end_base": Columns.varchar(10),
            "is_out": Column("BOOLEAN"),
            "out_number": Column("INTEGER"),
            "is_scoring_event": Column("BOOLEAN"),
            "rbi": Column("BOOLEAN"),
            "earned": Column("BOOLEAN"),
            "team_unearned": Column("BOOLEAN"),
            "play_index": Column("INTEGER"),
            "movement_reason": Columns.varchar(100),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["play_id"], name="idx_runners_play"),
            Index(["player_id"], name="idx_runners_player"),
            Index(["is_scoring_event"], name="idx_runners_scoring"),
            Index(["start_base", "end_base"], name="idx_runners_bases")
        ]
    },
    "reviews": {
        "description": "Review and challenge information",
        "type": TableType.EVENT,
        "columns": {
            "review_id": Columns.ID,
            "play_id": Columns.foreign_key("plays", nullable=False),
            "challenge_team_id": Columns.foreign_key("teams"),
            "in_progress": Column("BOOLEAN"),
            "review_type": Columns.varchar(50),
            "review_result": Columns.varchar(50),
            "review_description": Column("TEXT"),
            "review_start_time": Column("TIMESTAMP"),
            "review_end_time": Column("TIMESTAMP"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["play_id"], name="idx_reviews_play"),
            Index(["challenge_team_id"], name="idx_reviews_team"),
            Index(["review_type"], name="idx_reviews_type"),
            Index(["review_result"], name="idx_reviews_result")
        ]
    }
}
