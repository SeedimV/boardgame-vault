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

        def _to_int(value, default=0):
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
        errors = []
        if not self.title:
            errors.append("Title is required.")
        elif len(self.title) > 50:
            errors.append("Title must be 50 characters or less.")

        if not self.description:
            errors.append("Description is required.")
        elif len(self.description) > 1000:
            errors.append("Description must be 1000 characters or less.")

        if not 1 <= self.year <= 2100:
            errors.append("Given year is not valid.")

        if not 1 <= self.min_player_count <= 100:
            errors.append("Minimum players must be between 1 and 100.")

        if not 1 <= self.max_player_count <= 100:
            errors.append("Maximum players must be between 1 and 100.")

        if 1 <= self.min_player_count <= 100 and 1 <= self.max_player_count <= 100:
            if self.min_player_count > self.max_player_count:
                errors.append("Minimum players cannot exceed maximum players.")

        if not 1 <= self.playtime <= 10000:
            errors.append("Given playtime is not valid.")

        return errors

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes.setdefault(title, []).append(value)

    return classes

def parse_classes(entries, all_classes=None):
    if all_classes is None:
        all_classes = get_all_classes()
    selected = []
    for entry in entries:
        if not entry or ":" not in entry:
            continue
        title, value = entry.split(":", 1)
        if title in all_classes and value in all_classes[title]:
            selected.append((title, value))
    return selected

def add_game(game, user_id, classes):
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

    game_id = db.last_insert_id()

    sql = "INSERT INTO game_classes (game_id, title, value) VALUES (?, ? ,?)"
    for class_title, class_value in classes:
        db.execute(sql, [game_id, class_title, class_value])

    return game_id

def add_review(game_id, user_id, rating, description):
    sql = """INSERT INTO reviews (game_id, user_id, rating, description)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [game_id, user_id, rating, description])

def get_reviews(game_id):
    sql = """SELECT r.rating, r.description, u.id user_id, u.username
            FROM reviews r, users u
            WHERE r.game_id = ? AND r.user_id = u.id
            ORDER BY r.id DESC"""
    return db.query(sql, [game_id])

def get_classes(game_id):
    sql = "SELECT title, value FROM game_classes WHERE game_id = ?"
    return db.query(sql, [game_id])

def game_count():
    sql = "SELECT COUNT(*) FROM games"
    return db.query(sql)[0][0]

def get_games(page=1, page_size=10):
    sql = "SELECT id, title FROM games ORDER BY id DESC LIMIT ? OFFSET ?"
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

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

def update_game(game_id, game, classes):
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

    sql = "DELETE FROM game_classes WHERE game_id = ?"
    db.execute(sql, [game_id])

    sql = "INSERT INTO game_classes (game_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [game_id, class_title, class_value])

def remove_game(game_id):
    sql = "DELETE FROM games WHERE id = ?"
    db.execute(sql, [game_id])

def find_games_count(query):
    sql = """SELECT COUNT(*)
            FROM games
            WHERE title LIKE ? OR description LIKE ?"""
    like = f"%{query}%"
    return db.query(sql, [like, like])[0][0]

def find_games(query, page=1, page_size=10):
    sql = """SELECT id, title
            FROM games
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?"""
    like = f"%{query}%"
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [like, like, limit, offset])
