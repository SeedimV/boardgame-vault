import db


def add_game(title, description, year, min_player_count, max_player_count, playtime, user_id):
    sql = """INSERT INTO games (title, description, year, min_player_count, max_player_count, playtime, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, year, min_player_count, max_player_count, playtime, user_id])
