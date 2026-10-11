import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM game_classes")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM games")
db.execute("DELETE FROM users")

USER_COUNT = 1000
GAME_COUNT = 10 ** 5
REVIEW_COUNT = 10 ** 6

for i in range(1, USER_COUNT + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)])

for i in range(1, GAME_COUNT + 1):
    db.execute("""INSERT INTO games (title, description, year, min_player_count,
                                     max_player_count, playtime, user_id)
                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
               ["game" + str(i), "description" + str(i), 2020, 2, 4, 60,
                random.randint(1, USER_COUNT)])

for i in range(1, REVIEW_COUNT + 1):
    user_id = random.randint(1, USER_COUNT)
    game_id = random.randint(1, GAME_COUNT)
    db.execute("""INSERT INTO reviews (game_id, user_id, rating, description)
                  VALUES (?, ?, ?, ?)""",
               [game_id, user_id, random.randint(1, 5), "review" + str(i)])

db.commit()
db.close()
