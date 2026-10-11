# Board Game Vault

Board Game Vault is a web application for board game enthusiasts to catalog games, discover new titles, and share reviews and ratings.

---

## Core Functionalities

 * User Accounts: Users can create an account and log in/out.
 * Game Management: Users can add new board games with details (title, year, player count, playtime, description), as well as edit and delete their own entries.
 * Classifications & Tags:
   * Users can select one or more categories/genres for a game (e.g., strategy, family, party, card game).
   * Users can set the complexity/weight of the game (e.g., light, medium, heavy).
 * Reviews & Ratings: Users can write a review and give a numerical rating (1–5) for any board game.
 * Search & Filter: Users can search for games by title.
 * User Profiles & Statistics: Users have profile pages displaying their added games, written reviews, and statistics (such as total games added and total ratings given).

## Application Installation
Install `Flask`:
```sh
$ pip install flask
```

Create the database tables and initialize database:
```sh
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Run the application:
```sh
$ flask run
```

## Testing with Large Amounts of Data

The `seed.py` file creates a large amount of test data in the database: 1,000 users, 100,000 games, and 1,000,000 reviews. The test data can be created like this:

```sh
$ rm -f database.db
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
$ python3 seed.py
```

The application's performance was tested with this amount of data by measuring page loading times. The three numbers for each result are the durations of three consecutive measurements in seconds:

| Page                       | Load Time             |
|----------------------------|-----------------------|
| Front page (10 games page) | 0.006 / 0.001 / 0.001 |
| Game page                  | 0.004 / 0.001 / 0.001 |
| Search ("game100")         | 0.019 / 0.016 / 0.015 |
| User profile               | 0.004 / 0.001 / 0.001 |

All pages load quickly. The significance of the database indices was also examined by temporarily removing the indices `idx_games_user_id`, `idx_reviews_game_id`, and `idx_reviews_user_id` and repeating the measurements:

| Page                       | Load Time without Indices |
|----------------------------|---------------------------|
| Front page (10 games page) | 0.003 / 0.003 / 0.002     |
| Game page                  | 0.032 / 0.030 / 0.030     |
| Search ("game100")         | 0.016 / 0.016 / 0.016     |
| User profile               | 0.033 / 0.033 / 0.033     |

The indices significantly speed up the game page and user profile page (by approximately 30x), because finding the reviews for a game or user requires querying the reviews table by `game_id` or `user_id`. In the case of keyword search, the search query can also match the game description, requiring SQL to scan through all games; in this case, an index on title cannot speed up substring search. In any case, the search is fast with 100,000 games.

Handling large amounts of data is further facilitated by pagination on the front page, search results, and user profile page, which retrieves only 10 items per page at a time.

