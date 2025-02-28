# Schema definitions for play_detail tables
# TODO: Move relevant schema here

from typing import Dict
from ..models.column import Column, Columns, Index
from ..models.table_type import TableType

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
            "count_balls": Column("INTEGER"),  # Current count - balls
            "count_strikes": Column("INTEGER"),  # Current count - strikes
            "count_outs": Column("INTEGER"),  # Current outs in inning
            "game_score_away": Column("INTEGER"),  # Game score at time of event
            "game_score_home": Column("INTEGER"),  # Game score at time of event
            "start_time": Column("TIMESTAMP"),
            "end_time": Column("TIMESTAMP"),
            "batting_order": Column("INTEGER"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["play_id"], name="idx_events_play"),
            Index(["type"], name="idx_events_type"),
            Index(["details_isScoringPlay"], name="idx_events_scoring"),
            Index(["count_balls", "count_strikes"], name="idx_events_count")
        ]
    },
    "pitch_data": {
        "description": "Detailed pitch tracking data",
        "type": TableType.EVENT,
        "columns": {
            "pitch_id": Columns.ID,
            "event_id": Columns.foreign_key("play_events", nullable=False),
            "pitch_type": Columns.varchar(50),  # Classification (FB, CB, etc.)
            "pitch_sequence": Column("INTEGER"),  # Order in at-bat
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
            "pitch_call": Columns.varchar(50),  # Called strike, ball, in play, etc.
            "catcher_signal": Columns.varchar(50),  # Catcher's called pitch type
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["event_id"], name="idx_pitch_event"),
            Index(["start_speed"], name="idx_pitch_speed"),
            Index(["zone"], name="idx_pitch_zone"),
            Index(["breaks_spinRate"], name="idx_pitch_spin"),
            Index(["pitch_type"], name="idx_pitch_type"),
            Index(["pitch_sequence"], name="idx_pitch_sequence")
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
            "fielded_by": Columns.foreign_key("players"),  # Player who fielded the ball
            "hit_type": Columns.varchar(50),  # Ground ball, line drive, fly ball, etc.
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["event_id"], name="idx_hit_event"),
            Index(["launch_speed", "launch_angle"], name="idx_hit_launch"),
            Index(["total_distance"], name="idx_hit_distance"),
            Index(["fielded_by"], name="idx_hit_fielder"),
            Index(["hit_type"], name="idx_hit_type")
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
    "at_bat_context": {
        "description": "Contextual information for each at-bat",
        "type": TableType.EVENT,
        "columns": {
            "context_id": Columns.ID,
            "play_id": Columns.foreign_key("plays", nullable=False),
            "pitcher_id": Columns.foreign_key("players", nullable=False),
            "batter_id": Columns.foreign_key("players", nullable=False),
            "catcher_id": Columns.foreign_key("players", nullable=False),
            "inning": Column("INTEGER"),
            "inning_half": Columns.varchar(10),  # top/bottom
            "pitcher_throws": Column("CHAR(1)"),  # L/R
            "batter_side": Column("CHAR(1)"),  # L/R
            "pitcher_pitch_count": Column("INTEGER"),  # Total pitches thrown in game
            "pitcher_strikes_thrown": Column("INTEGER"),
            "pitcher_balls_thrown": Column("INTEGER"),
            "previous_matchups_abs": Column("INTEGER"),  # Career matchups
            "previous_matchups_hits": Column("INTEGER"),
            "previous_matchups_strikeouts": Column("INTEGER"),
            "previous_matchups_walks": Column("INTEGER"),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["play_id"], name="idx_context_play"),
            Index(["pitcher_id"], name="idx_context_pitcher"),
            Index(["batter_id"], name="idx_context_batter"),
            Index(["inning", "inning_half"], name="idx_context_inning")
        ]
    },
    "game_conditions": {
        "description": "Environmental conditions during the game",
        "type": TableType.EVENT,
        "columns": {
            "condition_id": Columns.ID,
            "game_id": Columns.foreign_key("games", nullable=False),
            "temperature": Columns.decimal(4, 1),
            "wind_speed": Columns.decimal(4, 1),
            "wind_direction": Columns.varchar(50),
            "pressure": Columns.decimal(6, 2),
            "humidity": Columns.decimal(4, 1),
            "precipitation_type": Columns.varchar(50),
            "field_condition": Columns.varchar(50),
            "sky_condition": Columns.varchar(50),
            "created_at": Columns.CREATED_AT
        },
        "indices": [
            Index(["game_id"], name="idx_conditions_game"),
            Index(["temperature"], name="idx_conditions_temp"),
            Index(["wind_speed"], name="idx_conditions_wind")
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
