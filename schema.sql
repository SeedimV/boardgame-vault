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

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    game_id INTEGER REFERENCES games ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    rating INTEGER,
    description TEXT
);

CREATE TABLE classes(
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE game_classes (
    id INTEGER PRIMARY KEY,
    game_id INTEGER REFERENCES games ON DELETE CASCADE,
    title TEXT,
    value TEXT
);
