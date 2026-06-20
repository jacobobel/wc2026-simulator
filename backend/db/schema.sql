CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(10),
    confederation VARCHAR(20),
    fifa_ranking INTEGER,
    group_name VARCHAR(5),
    crest_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    home_score INTEGER,
    away_score INTEGER,
    stage VARCHAR(50),
    group_name VARCHAR(5),
    match_date TIMESTAMP,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qualifier_results (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    confederation VARCHAR(20),
    played INTEGER,
    won INTEGER,
    drawn INTEGER,
    lost INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    points INTEGER,
    avg_opponent_fifa_ranking REAL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_ratings (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) UNIQUE,
    attack_strength REAL,
    defense_weakness REAL,
    form_score REAL,
    schedule_difficulty REAL,
    composite_rating REAL,
    avg_goals_scored REAL,
    avg_goals_conceded REAL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS simulation_results (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    simulations_run INTEGER,
    win_pct REAL,
    final_pct REAL,
    semi_pct REAL,
    quarter_pct REAL,
    r16_pct REAL,
    r32_pct REAL,
    group_exit_pct REAL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expected_matchups (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    stage VARCHAR(20),
    opponent_id INTEGER REFERENCES teams(id),
    probability REAL,
    simulations_run INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50),
    status VARCHAR(20),
    records_updated INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);