import db


def add_game(title, description, year, min_player_count, max_player_count, playtime, user_id):
    sql = """INSERT INTO games (title, description, year, min_player_count, max_player_count, playtime, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, year, min_player_count, max_player_count, playtime, user_id])

def get_games():
    sql = "SELECT id, title FROM games ORDER BY id DESC"
    return db.query(sql, [])

def get_game(item_id):
    sql = """SELECT g.title,
                    g.description,
                    g.year,
                    g.min_player_count,
                    g.max_player_count,
                    g.playtime,
                    u.username
            FROM games g, users u
            WHERE g.user_id = u.id AND
                g.id = ?"""

    return db.query(sql, [item_id])[0]
