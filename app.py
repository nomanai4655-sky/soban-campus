import os
import sqlite3
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "soban-campus-secret-key-2026")

# Environment & SQLite DB path resolution
IS_VERCEL = os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV")
if IS_VERCEL:
    DB_PATH = "/tmp/soban_campus.db"
    UPLOAD_FOLDER = "/tmp/uploads"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "soban_campus.db")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

# Admin credentials (overridable via environment variables)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "soban123")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Admissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            class_applying TEXT NOT NULL,
            phone TEXT NOT NULL,
            prev_school TEXT,
            address TEXT,
            certificate_path TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Contact Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Ensure tables are created when app starts
with app.app_context():
    init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("auth"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- CONTEXT PROCESSOR ----------------
@app.context_processor
def inject_global_vars():
    return {
        "school_name": "The Educators (Soban Campus)",
        "school_phone": "0300-7331807",
        "school_address": "Ahmad Cottage, Opp. Best Way CNG, Raja Pur Stop, Khanewal Road, Multan",
        "principal": "Mam Fozia Mughees",
        "director": "Maqbool Ahmad"
    }


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    events = [
        {"title": "Annual Parent-Teacher Meeting", "date": "2026-04-15", "desc": "Discussion on academic progress and student development."},
        {"title": "Science & Computer Exhibition", "date": "2026-05-10", "desc": "Students from Class 1 to 10 display working models and projects."},
        {"title": "Matric Preparation Workshop", "date": "2026-06-01", "desc": "Special exam preparation and conceptual review for Board exams."}
    ]
    return render_template("index.html", events=events)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/academics")
def academics():
    return render_template("academics.html")


@app.route("/admissions", methods=["GET", "POST"])
def admissions():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        father_name = request.form.get("father_name", "").strip()
        class_applying = request.form.get("class_applying", "").strip()
        phone = request.form.get("phone", "").strip()
        prev_school = request.form.get("prev_school", "").strip()
        address = request.form.get("address", "").strip()

        if not student_name or not father_name or not class_applying or not phone:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("admissions"))

        file = request.files.get("certificate")
        filename_saved = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_saved = f"{phone}_{filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_saved))

        db = get_db()
        db.execute("""
            INSERT INTO admissions (student_name, father_name, class_applying, phone, prev_school, address, certificate_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_name, father_name, class_applying, phone, prev_school, address, filename_saved))
        db.commit()

        flash(f"Admission application submitted successfully for {student_name}! Use your phone number ({phone}) on our status checker page to track application progress.", "success")
        return redirect(url_for("admissions"))

    return render_template("admissions.html")


@app.route("/status", methods=["GET", "POST"])
def status():
    record = None
    searched = False
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        searched = True
        if phone:
            db = get_db()
            record = db.execute("SELECT * FROM admissions WHERE phone = ? ORDER BY id DESC LIMIT 1", (phone,)).fetchone()

    return render_template("status.html", record=record, searched=searched)


@app.route("/timetable")
def timetable():
    return render_template("timetable.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if name and phone and subject and message:
            db = get_db()
            db.execute("INSERT INTO contacts (name, phone, subject, message) VALUES (?, ?, ?, ?)",
                       (name, phone, subject, message))
            db.commit()
            flash("Your message has been sent successfully! Our administration will contact you via phone/WhatsApp.", "success")
            return redirect(url_for("contact"))
        else:
            flash("Please fill in all fields before submitting.", "danger")

    return render_template("contact.html")


@app.route("/news")
def news():
    news_items = [
        {"title": "Admissions Open for New Session", "date": "March 2026", "desc": "Admissions from Class 1 to Matric (Class 10) are now open. Visit campus or apply online."},
        {"title": "High Matriculation Result Announced", "date": "February 2026", "desc": "Our Matric students achieved a outstanding 96% pass rate with top grades in board examinations."},
        {"title": "Updated Science & Chemistry Lab", "date": "January 2026", "desc": "New apparatus and practical equipment added for enhanced conceptual science experimentations."}
    ]
    return render_template("news.html", news_items=news_items)


@app.route("/events")
def events():
    events_list = [
        {"title": "Annual Parent-Teacher Meeting", "date": "April 15, 2026", "desc": "Interactive session between parents and staff regarding student performance."},
        {"title": "Science & Computer Exhibition", "date": "May 10, 2026", "desc": "Exhibition showcasing models, software tools, and scientific demonstrations built by students."},
        {"title": "Matric Preparation Workshop", "date": "June 01, 2026", "desc": "Comprehensive strategy and paper-solving techniques session for Class 9 and 10 students."}
    ]
    return render_template("events.html", events_list=events_list)


@app.route("/auth", methods=["GET", "POST"])
def auth():
    action = request.form.get("action")
    
    if request.method == "POST":
        db = get_db()
        
        # --- LOGIN ACTION ---
        if action == "login":
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            remember = request.form.get("remember")

            user = db.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
            if user and check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["fullname"]
                session["user_phone"] = user["phone"]
                session.permanent = True if remember else False
                flash(f"Welcome back, {user['fullname']}!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid phone number or password. Please try again.", "danger")

        # --- SIGNUP ACTION ---
        elif action == "signup":
            fullname = request.form.get("fullname", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")

            if not fullname or not phone or not password:
                flash("All fields are required for signup.", "danger")
                return redirect(url_for("auth"))

            existing = db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
            if existing:
                flash("Phone number already registered. Please login instead.", "warning")
            else:
                hashed_pw = generate_password_hash(password)
                cursor = db.cursor()
                cursor.execute("INSERT INTO users (fullname, phone, password) VALUES (?, ?, ?)",
                               (fullname, phone, hashed_pw))
                db.commit()
                
                # Auto-login after signup
                new_user_id = cursor.lastrowid
                session["user_id"] = new_user_id
                session["user_name"] = fullname
                session["user_phone"] = phone
                session.permanent = True
                
                flash("Account created successfully! You are now logged in.", "success")
                return redirect(url_for("dashboard"))

        # --- ADMIN LOGIN ACTION ---
        elif action == "admin_login":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session["is_admin"] = True
                session["admin_user"] = username
                flash("Admin authentication successful.", "success")
                return redirect(url_for("admin"))
            else:
                flash("Invalid Admin credentials.", "danger")

    return render_template("auth.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_name=session.get("user_name"), user_phone=session.get("user_phone"))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    db = get_db()

    if request.method == "POST":
        action = request.form.get("admin_action")
        if action == "update_status":
            app_id = request.form.get("app_id")
            new_status = request.form.get("new_status")
            db.execute("UPDATE admissions SET status = ? WHERE id = ?", (new_status, app_id))
            db.commit()
            flash(f"Application #{app_id} status updated to '{new_status}'.", "success")
            return redirect(url_for("admin"))

    admissions_list = db.execute("SELECT * FROM admissions ORDER BY id DESC").fetchall()
    users_list = db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    contacts_list = db.execute("SELECT * FROM contacts ORDER BY id DESC").fetchall()

    return render_template("admin.html", admissions=admissions_list, users=users_list, contacts=contacts_list)


if __name__ == "__main__":
    app.run(debug=True)
