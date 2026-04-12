#backend
#web framework = flask
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
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

@app.route('/')
def landing():
    return render_template("landing_page.html")

#API FOR user registeration or sign_IN
@app.route("/register", methods=["GET","POST"])
def register():

   if request.method =='POST':
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = get_db()
       #new user
        try:
            conn.execute(
                "INSERT INTO users(username, password) VALUES(?,?)",(username, password)
            )
            conn.commit()
        except:
           return "Username already exists!....."
        finally:
            conn.close()

        #login to enter
        return redirect("/login")
   return render_template("register.html")

#api name = login method =get/post
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        # Check user exists AND password matches hash
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/")
        else:
            return "Invalid credentials"

    return render_template("login.html")

#api name logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#user dashboard
@app.route("/home")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    conn = get_db()

    total_tasks  = conn.execute(
        "SELECT COUNT(*) as count FROM tasks WHERE user_id=?",(user_id,)
    ).fetchone()["count"]

    notes = conn.execute(
        "SELECT COUNT(*) as count FROM notes WHERE user_id=?",(user_id,)
    ).fetchone()["count"]

    exams = conn.execute(
        "SELECT COUNT(*) as count FROM exams WHERE user_id=?",(user_id,)
    ).fetchone()["count"]

    conn.close()

    return render_template(
        "dashboard.html",
        total_tasks = total_tasks,
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
        "SELECT * FROM tasks WHERE user_id=?",(session["user_id"],)
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
        "INSERT INTO tasks(user_id, title, deadline, status) VALUES(?,?,?,?)",(session["user_id"],title,deadline,"Pending")
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")
# notes api
@app.route('/notes')
def notes():
    if "user_id" not in session:
        return redirect('/login')
    
    conn = get_db()
    notes = conn.execute(
        "SELECT* FROM notes where user_id=?", (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("notes.html",notes=notes)

@app.route('/add_note', methods=["POST"])
def add_note():
    subject = request.form["subject"]
    content = request.form["content"]

    conn=get_db()
    conn.execute(
        "INSERT INTO notes(user_id, subject, content) VALUES(?, ?, ?)",
        (session["user_id"], subject, content)
    )
    conn.commit()
    conn.close()
    return redirect('/notes')

@app.route('/exams')
def exams():
    if "user_id" not in session:
        return redirect('/login')
    
    conn = get_db()
    exams = conn.execute(
        "SELECT * FROM exams WHERE user_id=?",(session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("exams.html", exams=exams)

@app.route('/add_exam', methods=["POST"])
def add_exam():
    subject = request.form["subject"]
    exam_date = request.form["exam"]
    description = request.form["description"]

    conn= get_db()
    conn.execute(
        "INSERT INTO exams(user_id, subject, exam_date, description) VALUES(?, ?, ?, ?)",(session["user_id"], subject, exam_date, description)
    )
    conn.commit()
    conn.close()

    return redirect("/exams")

if __name__ == "__main__":
    app.run(debug=True)