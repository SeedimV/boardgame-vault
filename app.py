import secrets
from sqlite3 import IntegrityError

from flask import Flask, abort, flash, redirect, render_template, request, session

import config
import games
import users

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_games = games.get_games()
    return render_template("index.html", games=all_games)

@app.route("/find_game")
def find_game():
    query = request.args.get("query")
    if query:
        results = games.find_games(query)
    else:
        query = ""
        results = []
    return render_template("find_game.html", query=query, results=results)

@app.route("/game/<int:game_id>")
def show_game(game_id):
    game = games.get_game(game_id)
    if not game:
        abort(404)
    return render_template("show_game.html", game=game)

@app.route("/new_game")
def new_game():
    require_login()
    return render_template("new_game.html")

@app.route("/create_game", methods=["POST"])
def create_game():
    require_login()
    check_csrf()

    game = games.GameData.from_form(request.form)
    user_id = session["user_id"]

    if not game.validate():
        abort(403)

    games.add_game(game, user_id)
    return redirect("/")

@app.route("/edit_game/<int:game_id>")
def edit_game(game_id):
    require_login()
    game = games.get_game(game_id)
    if not game:
        abort(404)
    if session["user_id"] != game["user_id"]:
        abort(403)

    return render_template("edit_game.html", game=game)

@app.route("/update_game", methods=["POST"])
def update_game():
    require_login()
    check_csrf()

    game_id = request.form["game_id"]
    game_record = games.get_game(game_id)

    if not game_record:
        abort(404)
    if game_record["user_id"] != session["user_id"]:
        abort(403)

    game = games.GameData.from_form(request.form)

    if not game.validate():
        abort(403)

    games.update_game(game_id, game)
    return redirect(f"/game/{game_id}")

@app.route("/remove_game/<int:game_id>", methods=["GET", "POST"])
def remove_game(game_id):
    require_login()

    game = games.get_game(game_id)

    if not game:
        abort(404)
    if game["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_game.html", game=game)

    check_csrf()

    if "remove" in request.form:
        games.remove_game(game_id)
        return redirect("/")
    return redirect(f"/game/{game_id}")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not 3 <= len(username) <= 30:
        flash("ERROR: Username must be between 3 and 30 characters")
        return redirect("/register")

    if len(password1) < 8:
        flash("ERROR: Password must be at least 8 characters long.")
        return redirect("/register")

    if password1 != password2:
        flash("ERROR: Passwords do not match")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except IntegrityError:
        flash("ERROR: username is already in use")
        return redirect("/register")

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user_id = users.check_login(username, password)
    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    flash("ERROR: wrong username or password")
    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
