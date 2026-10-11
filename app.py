import math
import secrets
from sqlite3 import IntegrityError

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session)

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
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    total_games = games.game_count()
    page_count = math.ceil(total_games / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_games = games.get_games(page, page_size)
    return render_template("index.html", page=page, page_count=page_count, games=all_games)

@app.errorhandler(404)
def page_not_found():
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden():
    return render_template("403.html"), 403

@app.route("/user/<int:user_id>")
@app.route("/user/<int:user_id>/<int:page>")
def show_user(user_id, page=1):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    page_size = 10
    total_games = users.get_games_count(user_id)
    total_reviews = users.get_reviews_count(user_id)

    games_page_count = math.ceil(total_games / page_size)
    games_page_count = max(games_page_count, 1)

    review_page = request.args.get("review_page", 1, type=int)
    reviews_page_count = math.ceil(total_reviews / page_size)
    reviews_page_count = max(reviews_page_count, 1)

    if page < 1:
        return redirect(f"/user/{user_id}/1?review_page={review_page}")
    if page > games_page_count:
        return redirect(f"/user/{user_id}/{games_page_count}?review_page={review_page}")

    if review_page < 1:
        return redirect(f"/user/{user_id}/{page}?review_page=1")
    if review_page > reviews_page_count:
        return redirect(f"/user/{user_id}/{page}?review_page={reviews_page_count}")

    all_games = users.get_games(user_id, page, page_size)
    user_reviews = users.get_reviews(user_id, review_page, page_size)
    return render_template("show_user.html",
                           user=user,
                           games=all_games,
                           total_games=total_games,
                           reviews=user_reviews,
                           total_reviews=total_reviews,
                           page=page,
                           page_count=games_page_count,
                           review_page=review_page,
                           review_page_count=reviews_page_count)

@app.route("/find_game")
def find_game():
    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)

    if query:
        page_size = 10
        total_count = games.find_games_count(query)
        page_count = math.ceil(total_count / page_size)
        page_count = max(page_count, 1)

        if page < 1:
            return redirect(f"/find_game?query={query}&page=1")
        if page > page_count:
            return redirect(f"/find_game?query={query}&page={page_count}")

        results = games.find_games(query, page, page_size)
    else:
        page = 1
        page_count = 1
        results = []

    return render_template("find_game.html",
                           query=query,
                           results=results,
                           page=page,
                           page_count=page_count)

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
