from dataclasses import dataclass

import db


@dataclass
class GameData:
    title: str
    description: str
    year: int
    min_player_count: int
    max_player_count: int
    playtime: int

    @classmethod
    def from_form(cls, form):

        def _to_int(value, default = 0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        return cls(
            title=form.get("title", "").strip(),
            description=form.get("description", "").strip(),
            year=_to_int(form.get("year")),
            min_player_count=_to_int(form.get("min_player_count")),
            max_player_count=_to_int(form.get("max_player_count")),
            playtime=_to_int(form.get("playtime"))
        )

    def validate(self):
        return all([
            self.title and len(self.title) <= 50,
            self.description and len(self.description) <= 1000,
            self.year,
            self.min_player_count >=1,
            self.max_player_count,
            self.min_player_count <= self.max_player_count,
            self.playtime >= 1,
        ])

def add_game(game, user_id):
    sql = """INSERT INTO games
            (title, description, year, min_player_count, max_player_count, playtime, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(
        sql,
        [
            game.title,
            game.description,
            game.year,
            game.min_player_count,
            game.max_player_count,
            game.playtime,
            user_id,
        ]
    )

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
    result = db.query(sql, [game_id])
    return result[0] if result else None

def update_game(game_id, game):
    sql = """UPDATE games SET title = ?,
                description = ?,
                year = ?,
                min_player_count = ?,
                max_player_count = ?,
                playtime = ?
            WHERE id = ?"""

    db.execute(
        sql,
        [
            game.title,
            game.description,
            game.year,
            game.min_player_count,
            game.max_player_count,
            game.playtime,
            game_id,
        ]
    )

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
