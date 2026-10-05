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

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    
    games = users.get_games(user_id)
    return render_template("show_user.html", user=user, games=games)

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

        if not game.validate():
            flash("Please fill all required fields correctly.")
            return render_template("new_game.html", game=game, classes=all_classes), 400
        
        classes = games.parse_classes(request.form.getlist("classes"), all_classes)
        game_id = games.add_game(game, session["user_id"], classes)
        return redirect(f"/game/{game_id}")

    return render_template("new_game.html", game=None, classes=all_classes)

@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()
    check_csrf()

    rating = request.form["rating"]
    description = request.form["description"]
    game_id = request.form["game_id"]
    game = games.get_game(game_id)

    if not game:
            abort(404)

    try:
        rating = int(request.form.get("rating", 0))
    except (ValueError, TypeError):
        abort(400)

    if not (1 <= rating <= 5):
        abort(400)

    description = request.form.get("description", "").strip()
    if len(description) > 1000:
        abort(400)

    user_id = session["user_id"]
    games.add_review(game_id, user_id, rating, description)

    return redirect(f"/game/{game_id}")

@app.route("/edit_game/<int:game_id>")
def edit_game(game_id):
    require_login()
    game = games.get_game(game_id)
    if not game:
        abort(404)
    if session["user_id"] != game["user_id"]:
        abort(403)

    all_classes = games.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in games.get_classes(game_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_game.html", game=game, classes=classes, all_classes=all_classes)

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

    all_classes = games.get_all_classes()
    classes = games.parse_classes(request.form.getlist("classes"), all_classes)

    games.update_game(game_id, game, classes)
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
