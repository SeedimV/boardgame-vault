import db


def add_game(title, description, year, min_player_count, max_player_count, playtime, user_id):
    sql = """INSERT INTO games (title, description, year, min_player_count, max_player_count, playtime, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, year, min_player_count, max_player_count, playtime, user_id])

def get_games():
    sql = "SELECT id, title FROM games ORDER BY id DESC"
    return db.query(sql, [])

def get_game(game_id):
    sql = """SELECT g.id,
                    g.title,
                    g.description,
                    g.year,
                    g.min_player_count,
                    g.max_player_count,
                    g.playtime,
                    u.id user_id,
                    u.username
            FROM games g, users u
            WHERE g.user_id = u.id AND
                g.id = ?"""

    return db.query(sql, [game_id])[0]

def update_game(game_id, title, description, year, min_player_count, max_player_count, playtime):
    sql = """UPDATE games SET title = ?,
                description = ?,
                year = ?,
                min_player_count = ?,
                max_player_count = ?,
                playtime = ?
            WHERE id = ?"""

    db.execute(sql, [title, description, year, min_player_count, max_player_count, playtime, game_id])    

def remove_game(game_id):
    sql = "DELETE FROM games WHERE id = ?"
    db.execute(sql, [game_id])

def find_games(query):
    sql = """SELECT id, title
            FROM games
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY id DESC"""
    like = f"%{query}%"
    return db.query(sql, [like, like])
