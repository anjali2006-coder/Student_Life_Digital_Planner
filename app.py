#backend
#web framework = flask
from flask import Flask, render_template, request, redirect, session
#sqlite3 for database
import sqlite3

app = Flask(__name__)
app.secret_key = "studentplannersecret"

#function for db connection
def get_db():
    conn = sqlite3.connect("planner.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

#users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE,
              password TEXT)
    """)
#tasks TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              title TEXT,
              deadline TEXT, 
              status TEXT
              )
    """)

#for notes
    c.execute("""
    CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            content TEXT
            )
    """)
#for exams
    c.execute("""
    CREATE TABLE IF NOT EXISTS exams(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              subject TEXT,
              exam_date TEXT,
              description TEXT)
    """)
    conn.commit()
    conn.close()

init_db()
#API FOR user registeration or sign_IN
@app.route("/register", method=["GET","POST"])
def register():

   if register.method =='POST':
       username = request.form["usrename"]
       password = request.form["password"]
       conn = get_db()
       #new user
       conn.execute(
           "INSERT INTO users(username, password) VALUES(?,?)",(username, password)
       )

       conn.commit()
       conn.close()

        #login to enter
       return redirect("/login")
   return render_template("register.html")

#api name = login method =get/post
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username =? AND password =?",(username,password)
        ).fetchall()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/")
    return render_template("login.html")

#api name logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#user dashboard
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    conn = get_db()

    total_tasks  = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id=?",(user_id,)
    ).fetchall()[0]

    notes = conn.execute(
        "SELECT COUNT(*) FROM notes WHERE user_id=?",(user_id,)
    ).fetchall()[0]

    exams = conn.execute(
        "SELECT COUNT(*) FROM exams WHER user_id=?",(user_id,)
    ).fetchall()[0]

    return render_template(
        "dashboard.html",
        total_taks = total_tasks,
        notes = notes,
        exams = exams
    )
#see and create or add task
@app.route("/tasks")
def tasks():
    if "user_id" not in session:
        return redirect("/login")
    
    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM WHERE user_id=?",(session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("tasks.html",tasks=tasks)
# add/create tasks  method = post
@app.route("/add_tasks", methods=["POST"])
def add_task():

    title = request.form["title"]
    deadline = request.form["deadline"]

    conn = get_db()

    conn.execute(
        "INSERT INTO tasks(user_id, deadline, status) VALUES(?,?,?,?)",(session["user_id"],title,deadline,"Pending")
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")