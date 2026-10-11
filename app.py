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
    token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")
    if not token or token != session_token:
        abort(403)

@app.route("/")
def index():
    all_games = games.get_games()
    return render_template("index.html", games=all_games)

@app.errorhandler(404)
def page_not_found():
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden():
    return render_template("403.html"), 403

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    all_games = users.get_games(user_id)
    user_reviews = users.get_reviews(user_id)
    return render_template("show_user.html",
                           user=user, games=all_games, reviews=user_reviews)

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
    classes = games.get_classes(game_id)
    reviews = games.get_reviews(game_id)
    return render_template("show_game.html", game=game, classes=classes, reviews=reviews)

@app.route("/new_game", methods=["GET", "POST"])
def new_game():
    require_login()
    all_classes = games.get_all_classes()

    if request.method == "POST":
        check_csrf()
        game = games.GameData.from_form(request.form)
        errors = game.validate()

        if errors:
            for error in errors:
                flash(error)
            return render_template("new_game.html", game=game, classes=all_classes), 400

        classes = games.parse_classes(request.form.getlist("classes"), all_classes)
        game_id = games.add_game(game, session["user_id"], classes)
        return redirect(f"/game/{game_id}")

    return render_template("new_game.html", game=None, classes=all_classes)

@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()
    check_csrf()

    game_id = request.form.get("game_id")
    game = games.get_game(game_id)

    errors = []

    if not game:
        flash("Unexpected error, game not found.")
        return redirect("/")

    try:
        rating = int(request.form.get("rating", 0))
        if not 1 <= rating <= 5:
            errors.append("Rating must be between 1 and 5.")
    except (ValueError, TypeError):
        errors.append("Invalid rating.")

    description = request.form.get("description", "").strip()
    if len(description) > 1000:
        errors.append("Description must be 1000 characters or less.")

    if errors:
        for error in errors:
            flash(error)
        return redirect(f"/game/{game_id}")

    user_id = session["user_id"]
    games.add_review(game_id, user_id, rating, description)

    return redirect(f"/game/{game_id}")

@app.route("/edit_game/<int:game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    require_login()
    game = games.get_game(game_id)

    if not game:
        abort(404)
    if game["user_id"] != session["user_id"]:
        abort(403)

    all_classes = games.get_all_classes()
    game_classes = {entry["title"]: entry["value"] for entry in games.get_classes(game_id)}

    if request.method == "POST":
        check_csrf()

        game_data = games.GameData.from_form(request.form)
        game_data.id = game_id
        errors = game_data.validate()

        if errors:
            for error in errors:
                flash(error)
            return render_template("edit_game.html", game=game_data,
                                   classes=game_classes, all_classes=all_classes), 400

        classes = games.parse_classes(request.form.getlist("classes"), all_classes)
        games.update_game(game_id, game_data, classes)
        return redirect(f"/game/{game_id}")

    return render_template("edit_game.html",
                           game=game, classes=game_classes, all_classes=all_classes)

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

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password1 = request.form.get("password1", "")
        password2 = request.form.get("password2", "")

        errors = []
        if not 3 <= len(username) <= 30:
            errors.append("Username must be between 3 and 30 characters.")
        if len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password1 != password2:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error)
            return render_template("register.html"), 400

        try:
            user_id = users.create_user(username, password1)
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        except IntegrityError:
            flash("Username is already in use.")
            return render_template("register.html"), 400

    return render_template("register.html")

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
