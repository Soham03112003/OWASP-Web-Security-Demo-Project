
import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from flask import Flask, request, render_template, redirect, session
import sqlite3
import bcrypt
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = "owasp-insecure-key"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db():
    return sqlite3.connect("database.db")
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS xss_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment TEXT
)
""")

conn.commit()
conn.close()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            msg = "Invalid Credentials"

    # ✅ ALWAYS return something
    return render_template("login.html", msg=msg)

# ---------------- CSRF VULNERABLE ----------------
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        new_password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (new_password, session["user"])
        )
        conn.commit()

        return "Password Changed (CSRF Vulnerable)"

    return """
    <h3>Change Password</h3>
    <form method="POST">
        <input type="password" name="password">
        <button type="submit">Change</button>
    </form>
    """

# ---------------- CSRF PROTECTED ----------------
@app.route("/secure-change-password", methods=["GET", "POST"])
def secure_change_password():
    if "user" not in session:
        return redirect("/login")

    if request.method == "GET":
        token = secrets.token_hex(16)
        session["csrf_token"] = token

        return f"""
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{token}">
            <input type="password" name="password">
            <button type="submit">Change</button>
        </form>
        """

    if request.form.get("csrf_token") != session.get("csrf_token"):
        return "CSRF Attack Detected!"

    return "Password Changed Securely"



        # ✅ SECURE QUERY (Parameterized)
    cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
    user = cursor.fetchone()

    if user:
            session["user"] = username
            return redirect("/dashboard")
    else:
            msg = "Invalid Credentials"

    return render_template("login.html", msg=msg)

# ---------------- DASHBOARD (BROKEN AUTH FIXED) ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- XSS VULNERABLE ----------------
@app.route("/xss", methods=["GET", "POST"])
def xss_demo():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        comment = request.form.get("comment")
        cursor.execute(
            "INSERT INTO xss_comments (comment) VALUES (?)",
            (comment,)
        )
        conn.commit()

    cursor.execute("SELECT comment FROM xss_comments")
    comments = cursor.fetchall()

    conn.close()
    return render_template("xss.html", comments=comments)


# ---------------- PASSWORD HASHING (SECURE EXAMPLE) ----------------
@app.route("/secure-register", methods=["POST"])
def secure_register():
    username = request.form["username"]
    password = request.form["password"]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed)
    )
    conn.commit()

    return "User Registered Securely"

if __name__ == "__main__":
    app.run(debug=True)


