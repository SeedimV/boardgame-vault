CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    year INTEGER,
    min_player_count INTEGER,
    max_player_count INTEGER,
    playtime INTEGER,
    user_id INTEGER REFERENCES users
);