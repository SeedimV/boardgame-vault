from sqlite3 import IntegrityError

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_game")
def new_game():
    return render_template("new_game.html")

@app.route("/create_game", methods=["POST"])
def create_game():
    title = request.form["title"]
    description = request.form["description"]
    year = request.form["year"]
    min_player_count = request.form["min_player_count"]
    max_player_count = request.form["max_player_count"]
    playtime = request.form["playtime"]
    user_id = session["user_id"]

    sql = """INSERT INTO games (title, description, year, min_player_count, max_player_count, playtime, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, year, min_player_count, max_player_count, playtime, user_id])

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "ERROR: Passwords does not match"
    
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except IntegrityError:
        return "ERROR: username is already in use"

    return "Account registered"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    query = db.query(sql, [username])[0]
    user_id = query["id"]

    if not query or not check_password_hash(query[1], password):
        return "ERROR: wrong username or password"

    session["user_id"] = user_id
    session["username"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")