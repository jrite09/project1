import os
import sys
from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.secret_key = "7^XH!_]yGVL9]NRO#1_C_d6lve[g1]"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    # if the user is already logged in, redirect them to the search page
    if session.get('active_user') != None:
        return redirect(url_for('search'))
    return render_template("register.html")

@app.route("/registered", methods=["POST"])
def registered():
    # when the user presses submit, retrieve information from the form and store it in 'user' and 'userpass'
    user = request.form.get("username")
    userPass = request.form.get("password")
    try:
        db.execute("INSERT INTO users (username, password) VALUES (:user, :userPass)", {"user": user, "userPass": userPass})
        db.commit()
    except exc.IntegrityError:
        return render_template("error.html", message="An account with that username already exists")
    
    return render_template("registered.html")

@app.route("/login")
def login():
    # if the user is already logged in, redirect them to the search page
    if session.get('active_user') != None:
        return redirect(url_for('search'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    # if the user isn't logged in to an account, show them the appropriate error page
    if session.get('active_user') == None:
        return render_template("error.html", message="You are not logged in to an account")
    session.pop('active_user', None)
    flash('You were logged out.')
    return redirect(url_for("index"))

@app.route("/verify", methods=["GET", "POST"])
def verify():
    # if user did not get here by way of submitting login form, redirect to login page
    if request.method == "GET":
       return redirect(url_for("login"))

    # import username and password from login form
    user = request.form.get("username")
    userPass = request.form.get("password")

    # check if username + password exists in database
    if db.execute("SELECT * FROM users WHERE username = :user AND password = :password", { "user": user, "password": userPass }).rowcount == 0:
        return render_template("error.html", message="Invalid Username or Password")
    
    # remember which user has logged in
    session['active_user'] = user

    return redirect(url_for("search"))

@app.route("/search")
def search():
    # if the user is not logged in, redirect them to the login page
    if session.get('active_user') == None:
        return redirect(url_for("login"))
    return render_template("search.html")

@app.route("/searching", methods=['POST'])
def searching():
    # import the user query value from the form
    query = request.form.get("query")

    # wrap the query in '%' for easier SQL searching
    searchQuery = '%' + query + '%'

    # check how many results the query returns
    results = db.execute("SELECT id FROM books WHERE isbn LIKE :query OR author LIKE :query OR title LIKE :query", { "query": searchQuery })
    resultsCount = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR author LIKE :query OR title LIKE :query", { "query": searchQuery }).rowcount

    # display variations of results page depending on how many results there are
    if resultsCount == 1:
        return render_template("error.html", message="Not yet implemented")
    elif resultsCount > 1:
        return render_template("results.html", results=results, resultsCount=resultsCount)
    else:
        return render_template("error.html", message="Sorry, there are no matching books in the database")
    
@app.route("/api/<int:isbn>")
def isbn():
    return render_template("error.html", message="Not yet implemented")