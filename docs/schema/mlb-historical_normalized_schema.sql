--
-- Table: players_player
-- Source: gameData.players.player
--
CREATE TABLE players_player (
    id SERIAL PRIMARY KEY,
    active BOOLEAN,
    birth_city VARCHAR(255),
    birth_country VARCHAR(255),
    birth_date VARCHAR(255),
    birth_state_province VARCHAR(255),
    boxscore_name VARCHAR(255),
    current_age INTEGER,
    draft_year INTEGER,
    first_last_name VARCHAR(255),
    first_name VARCHAR(255),
    full_f_m_l_name VARCHAR(255),
    full_l_f_m_name VARCHAR(255),
    full_name VARCHAR(255),
    gender VARCHAR(255),
    height VARCHAR(255),
    id INTEGER,
    init_last_name VARCHAR(255),
    is_player BOOLEAN,
    is_verified BOOLEAN,
    last_first_name VARCHAR(255),
    last_init_name VARCHAR(255),
    last_name VARCHAR(255),
    last_played_date VARCHAR(255),
    link VARCHAR(255),
    middle_name VARCHAR(255),
    mlb_debut_date VARCHAR(255),
    name_first_last VARCHAR(255),
    name_slug VARCHAR(255),
    nick_name VARCHAR(255),
    primary_number VARCHAR(255),
    strike_zone_bottom NUMERIC(10,2),
    strike_zone_top NUMERIC(10,2),
    use_last_name VARCHAR(255),
    use_name VARCHAR(255),
    weight INTEGER
);

COMMENT ON TABLE players_player IS 'Generated from gameData.players.player';

CREATE INDEX idx_players_player_id ON players_player(id);

--
-- Table: teams_team
-- Source: gameData.teams.away
--
CREATE TABLE teams_team (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    active BOOLEAN,
    all_star_status VARCHAR(255),
    club_name VARCHAR(255),
    file_code VARCHAR(255),
    first_year_of_play VARCHAR(255),
    franchise_name VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    location_name VARCHAR(255),
    name VARCHAR(255),
    season INTEGER,
    short_name VARCHAR(255),
    team_code VARCHAR(255),
    team_name VARCHAR(255)
);

COMMENT ON TABLE teams_team IS 'Generated from gameData.teams.away';

CREATE INDEX idx_teams_team_id ON teams_team(id);
CREATE INDEX idx_teams_team_name ON teams_team(name);
CREATE INDEX idx_teams_team_season ON teams_team(season);

--
-- Table: away_venue
-- Source: gameData.teams.away.springLeague
--
CREATE TABLE away_venue (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE away_venue IS 'Generated from gameData.teams.away.springLeague';

CREATE INDEX idx_away_venue_id ON away_venue(id);
CREATE INDEX idx_away_venue_name ON away_venue(name);

--
-- Table: home_venue
-- Source: gameData.teams.home.springLeague
--
CREATE TABLE home_venue (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE home_venue IS 'Generated from gameData.teams.home.springLeague';

CREATE INDEX idx_home_venue_id ON home_venue(id);
CREATE INDEX idx_home_venue_name ON home_venue(name);

--
-- Table: game_data_venue
-- Source: gameData.venue
--
CREATE TABLE game_data_venue (
    id SERIAL PRIMARY KEY,
    active BOOLEAN,
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255),
    season VARCHAR(255)
);

COMMENT ON TABLE game_data_venue IS 'Generated from gameData.venue';

CREATE INDEX idx_game_data_venue_id ON game_data_venue(id);
CREATE INDEX idx_game_data_venue_name ON game_data_venue(name);
CREATE INDEX idx_game_data_venue_season ON game_data_venue(season);

--
-- Table: away_items_venue
-- Source: liveData.plays.playsByInning[].hits.away[].team
--
CREATE TABLE away_items_venue (
    id SERIAL PRIMARY KEY,
    all_star_status VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE away_items_venue IS 'Generated from liveData.plays.playsByInning[].hits.away[].team';

CREATE INDEX idx_away_items_venue_id ON away_items_venue(id);
CREATE INDEX idx_away_items_venue_name ON away_items_venue(name);

--
-- Table: team_venue
-- Source: liveData.plays.playsByInning[].hits.away[].team.springLeague
--
CREATE TABLE team_venue (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE team_venue IS 'Generated from liveData.plays.playsByInning[].hits.away[].team.springLeague';

CREATE INDEX idx_team_venue_id ON team_venue(id);
CREATE INDEX idx_team_venue_name ON team_venue(name);

--
-- Table: home_items_venue
-- Source: liveData.plays.playsByInning[].hits.home[].team
--
CREATE TABLE home_items_venue (
    id SERIAL PRIMARY KEY,
    all_star_status VARCHAR(255),
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE home_items_venue IS 'Generated from liveData.plays.playsByInning[].hits.home[].team';

CREATE INDEX idx_home_items_venue_id ON home_items_venue(id);
CREATE INDEX idx_home_items_venue_name ON home_items_venue(name);

--
-- Table: defense_venue
-- Source: liveData.linescore.defense.team
--
CREATE TABLE defense_venue (
    id SERIAL PRIMARY KEY,
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE defense_venue IS 'Generated from liveData.linescore.defense.team';

CREATE INDEX idx_defense_venue_id ON defense_venue(id);
CREATE INDEX idx_defense_venue_name ON defense_venue(name);

--
-- Table: offense_venue
-- Source: liveData.linescore.offense.team
--
CREATE TABLE offense_venue (
    id SERIAL PRIMARY KEY,
    id INTEGER,
    link VARCHAR(255),
    name VARCHAR(255)
);

COMMENT ON TABLE offense_venue IS 'Generated from liveData.linescore.offense.team';

CREATE INDEX idx_offense_venue_id ON offense_venue(id);
CREATE INDEX idx_offense_venue_name ON offense_venue(name);

--
-- Table: player_position
-- Source: gameData.players.player.primaryPosition
--
CREATE TABLE player_position (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    code VARCHAR(255),
    name VARCHAR(255),
    type VARCHAR(255)
);

COMMENT ON TABLE player_position IS 'Generated from gameData.players.player.primaryPosition';

CREATE INDEX idx_player_position_name ON player_position(name);
CREATE INDEX idx_player_position_type ON player_position(type);

--
-- Table: credits_items_position
-- Source: liveData.plays.allPlays[].runners[].credits[].position
--
CREATE TABLE credits_items_position (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    code VARCHAR(255),
    name VARCHAR(255),
    type VARCHAR(255)
);

COMMENT ON TABLE credits_items_position IS 'Generated from liveData.plays.allPlays[].runners[].credits[].position';

CREATE INDEX idx_credits_items_position_name ON credits_items_position(name);
CREATE INDEX idx_credits_items_position_type ON credits_items_position(type);

--
-- Table: away_stats
-- Source: liveData.boxscore.teams.away.teamStats
--
CREATE TABLE away_stats (
    id SERIAL PRIMARY KEY,
    batting JSONB,
    fielding JSONB,
    pitching JSONB
);

COMMENT ON TABLE away_stats IS 'Generated from liveData.boxscore.teams.away.teamStats';

--
-- Table: player_stats
-- Source: liveData.boxscore.teams.away.players.player.stats
--
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    batting JSONB,
    fielding JSONB,
    pitching JSONB
);

COMMENT ON TABLE player_stats IS 'Generated from liveData.boxscore.teams.away.players.player.stats';

--
-- Table: home_stats
-- Source: liveData.boxscore.teams.home.teamStats
--
CREATE TABLE home_stats (
    id SERIAL PRIMARY KEY,
    batting JSONB,
    fielding JSONB,
    pitching JSONB
);

COMMENT ON TABLE home_stats IS 'Generated from liveData.boxscore.teams.home.teamStats';

--
-- Table: plays_all_plays_items
-- Source: liveData.plays.allPlays
--
CREATE TABLE plays_all_plays_items (
    id SERIAL PRIMARY KEY,
    about JSONB,
    action_index JSONB,
    action_index_array INTEGER,
    at_bat_index INTEGER,
    count JSONB,
    matchup JSONB,
    pitch_index JSONB,
    pitch_index_array INTEGER,
    play_end_time VARCHAR(255),
    play_events JSONB,
    result JSONB,
    runner_index JSONB,
    runner_index_array INTEGER,
    runners JSONB
);

COMMENT ON TABLE plays_all_plays_items IS 'Generated from liveData.plays.allPlays';

--
-- Table: all_plays_items_runners_items
-- Source: liveData.plays.allPlays[].runners
--
CREATE TABLE all_plays_items_runners_items (
    id SERIAL PRIMARY KEY,
    credits JSONB,
    details JSONB,
    movement JSONB
);

COMMENT ON TABLE all_plays_items_runners_items IS 'Generated from liveData.plays.allPlays[].runners';

--
-- Table: runners_items_credits_items
-- Source: liveData.plays.allPlays[].runners[].credits
--
CREATE TABLE runners_items_credits_items (
    id SERIAL PRIMARY KEY,
    credit VARCHAR(255),
    player JSONB,
    position JSONB
);

COMMENT ON TABLE runners_items_credits_items IS 'Generated from liveData.plays.allPlays[].runners[].credits';

--
-- Table: all_plays_items_play_events_items
-- Source: liveData.plays.allPlays[].playEvents
--
CREATE TABLE all_plays_items_play_events_items (
    id SERIAL PRIMARY KEY,
    count JSONB,
    details JSONB,
    end_time VARCHAR(255),
    index INTEGER,
    is_pitch BOOLEAN,
    player JSONB,
    start_time VARCHAR(255),
    type VARCHAR(255)
);

COMMENT ON TABLE all_plays_items_play_events_items IS 'Generated from liveData.plays.allPlays[].playEvents';

CREATE INDEX idx_all_plays_items_play_events_items_type ON all_plays_items_play_events_items(type);

--
-- Table: current_play_runners_items
-- Source: liveData.plays.currentPlay.runners
--
CREATE TABLE current_play_runners_items (
    id SERIAL PRIMARY KEY,
    credits JSONB,
    details JSONB,
    movement JSONB
);

COMMENT ON TABLE current_play_runners_items IS 'Generated from liveData.plays.currentPlay.runners';

--
-- Table: current_play_play_events_items
-- Source: liveData.plays.currentPlay.playEvents
--
CREATE TABLE current_play_play_events_items (
    id SERIAL PRIMARY KEY,
    count JSONB,
    details JSONB,
    end_time VARCHAR(255),
    index INTEGER,
    is_pitch BOOLEAN,
    pitch_data JSONB,
    pitch_number INTEGER,
    play_id VARCHAR(255),
    start_time VARCHAR(255),
    type VARCHAR(255)
);

COMMENT ON TABLE current_play_play_events_items IS 'Generated from liveData.plays.currentPlay.playEvents';

CREATE INDEX idx_current_play_play_events_items_type ON current_play_play_events_items(type);

--
-- Table: plays_plays_by_inning_items
-- Source: liveData.plays.playsByInning
--
CREATE TABLE plays_plays_by_inning_items (
    id SERIAL PRIMARY KEY,
    bottom JSONB,
    bottom_array INTEGER,
    end_index INTEGER,
    hits JSONB,
    start_index INTEGER,
    top JSONB,
    top_array INTEGER
);

COMMENT ON TABLE plays_plays_by_inning_items IS 'Generated from liveData.plays.playsByInning';

--
-- Table: hits_away_items
-- Source: liveData.plays.playsByInning[].hits.away
--
CREATE TABLE hits_away_items (
    id SERIAL PRIMARY KEY,
    batter JSONB,
    coordinates JSONB,
    description VARCHAR(255),
    inning INTEGER,
    pitcher JSONB,
    team JSONB,
    type VARCHAR(255)
);

COMMENT ON TABLE hits_away_items IS 'Generated from liveData.plays.playsByInning[].hits.away';

CREATE INDEX idx_hits_away_items_type ON hits_away_items(type);

--
-- Table: hits_home_items
-- Source: liveData.plays.playsByInning[].hits.home
--
CREATE TABLE hits_home_items (
    id SERIAL PRIMARY KEY,
    batter JSONB,
    coordinates JSONB,
    description VARCHAR(255),
    inning INTEGER,
    pitcher JSONB,
    team JSONB,
    type VARCHAR(255)
);

COMMENT ON TABLE hits_home_items IS 'Generated from liveData.plays.playsByInning[].hits.home';

CREATE INDEX idx_hits_home_items_type ON hits_home_items(type);

--
-- Table: linescore_innings_items
-- Source: liveData.linescore.innings
--
CREATE TABLE linescore_innings_items (
    id SERIAL PRIMARY KEY,
    away JSONB,
    home JSONB,
    num INTEGER,
    ordinal_num VARCHAR(255)
);

COMMENT ON TABLE linescore_innings_items IS 'Generated from liveData.linescore.innings';

--
-- Table: away_info_items
-- Source: liveData.boxscore.teams.away.info
--
CREATE TABLE away_info_items (
    id SERIAL PRIMARY KEY,
    field_list JSONB,
    title VARCHAR(255)
);

COMMENT ON TABLE away_info_items IS 'Generated from liveData.boxscore.teams.away.info';

--
-- Table: info_items_field_list_items
-- Source: liveData.boxscore.teams.away.info[].fieldList
--
CREATE TABLE info_items_field_list_items (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255),
    value VARCHAR(255)
);

COMMENT ON TABLE info_items_field_list_items IS 'Generated from liveData.boxscore.teams.away.info[].fieldList';

--
-- Table: away_note_items
-- Source: liveData.boxscore.teams.away.note
--
CREATE TABLE away_note_items (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255),
    value VARCHAR(255)
);

COMMENT ON TABLE away_note_items IS 'Generated from liveData.boxscore.teams.away.note';

--
-- Table: player_all_positions_items
-- Source: liveData.boxscore.teams.home.players.player.allPositions
--
CREATE TABLE player_all_positions_items (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(255),
    code VARCHAR(255),
    name VARCHAR(255),
    type VARCHAR(255)
);

COMMENT ON TABLE player_all_positions_items IS 'Generated from liveData.boxscore.teams.home.players.player.allPositions';

CREATE INDEX idx_player_all_positions_items_name ON player_all_positions_items(name);
CREATE INDEX idx_player_all_positions_items_type ON player_all_positions_items(type);

--
-- Table: home_info_items
-- Source: liveData.boxscore.teams.home.info
--
CREATE TABLE home_info_items (
    id SERIAL PRIMARY KEY,
    field_list JSONB,
    title VARCHAR(255)
);

COMMENT ON TABLE home_info_items IS 'Generated from liveData.boxscore.teams.home.info';

--
-- Table: home_note_items
-- Source: liveData.boxscore.teams.home.note
--
CREATE TABLE home_note_items (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255),
    value VARCHAR(255)
);

COMMENT ON TABLE home_note_items IS 'Generated from liveData.boxscore.teams.home.note';

--
-- Table: boxscore_officials_items
-- Source: liveData.boxscore.officials
--
CREATE TABLE boxscore_officials_items (
    id SERIAL PRIMARY KEY,
    official JSONB,
    official_type VARCHAR(255)
);

COMMENT ON TABLE boxscore_officials_items IS 'Generated from liveData.boxscore.officials';

--
-- Table: boxscore_info_items
-- Source: liveData.boxscore.info
--
CREATE TABLE boxscore_info_items (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255),
    value VARCHAR(255)
);

COMMENT ON TABLE boxscore_info_items IS 'Generated from liveData.boxscore.info';

--
-- Table: boxscore_top_performers_items
-- Source: liveData.boxscore.topPerformers
--
CREATE TABLE boxscore_top_performers_items (
    id SERIAL PRIMARY KEY,
    game_score INTEGER,
    pitching_game_score INTEGER,
    player JSONB,
    type VARCHAR(255)
);

COMMENT ON TABLE boxscore_top_performers_items IS 'Generated from liveData.boxscore.topPerformers';

CREATE INDEX idx_boxscore_top_performers_items_type ON boxscore_top_performers_items(type);


--
-- Foreign Key Constraints
--
ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_players_player
    FOREIGN KEY (play_id)
    REFERENCES players_player (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_position
    FOREIGN KEY (play_id)
    REFERENCES player_position (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_stats
    FOREIGN KEY (play_id)
    REFERENCES player_stats (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_plays_all_plays_items
    FOREIGN KEY (play_id)
    REFERENCES plays_all_plays_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_all_plays_items_runners_items
    FOREIGN KEY (play_id)
    REFERENCES all_plays_items_runners_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_all_plays_items_play_events_items
    FOREIGN KEY (play_id)
    REFERENCES all_plays_items_play_events_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_current_play_runners_items
    FOREIGN KEY (play_id)
    REFERENCES current_play_runners_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_plays_plays_by_inning_items
    FOREIGN KEY (play_id)
    REFERENCES plays_plays_by_inning_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_all_positions_items
    FOREIGN KEY (play_id)
    REFERENCES player_all_positions_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_all_positions_items
    FOREIGN KEY (play_id)
    REFERENCES player_all_positions_items (id);

ALTER TABLE current_play_play_events_items
    ADD CONSTRAINT fk_current_play_play_events_items_player_all_positions_items
    FOREIGN KEY (play_id)
    REFERENCES player_all_positions_items (id);
