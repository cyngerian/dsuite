from .reference import reference_schema
from .team_player import team_player_schema
from .game_play import game_play_schema
from .play_detail import play_detail_schema

core_schema = {
    "REFERENCE": reference_schema,
    "TEAM_PLAYER": team_player_schema,
    "GAME_PLAY": game_play_schema,
    "PLAY_DETAIL": play_detail_schema
}

__all__ = [
    'reference_schema',
    'team_player_schema',
    'game_play_schema',
    'play_detail_schema',
    'core_schema'
]
