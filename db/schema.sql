CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS seasons (
    season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER NOT NULL REFERENCES seasons(season_id),
    match_date TEXT NOT NULL,
    kickoff_time TEXT,
    home_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    away_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    result TEXT NOT NULL,
    home_goals_ht INTEGER,
    away_goals_ht INTEGER,
    result_ht TEXT,
    referee TEXT
);

CREATE TABLE IF NOT EXISTS match_stats (
    match_id INTEGER PRIMARY KEY REFERENCES matches(match_id),
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    home_corners INTEGER,
    away_corners INTEGER,
    home_fouls INTEGER,
    away_fouls INTEGER,
    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,
    home_red_cards INTEGER,
    away_red_cards INTEGER
);

CREATE TABLE IF NOT EXISTS match_odds (
    match_id INTEGER PRIMARY KEY REFERENCES matches(match_id),
    avg_home_odds REAL,
    avg_draw_odds REAL,
    avg_away_odds REAL,
    max_home_odds REAL,
    max_draw_odds REAL,
    max_away_odds REAL
);

CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season_id);
CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);