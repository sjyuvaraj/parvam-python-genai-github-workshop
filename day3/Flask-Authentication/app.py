import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret_key"

DATABASE = os.path.join(app.root_path, "users.db")

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,14}$")
PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    db.close()


def validate_password(password: str) -> bool:
    return bool(PASSWORD_REGEX.match(password))


def password_validation_messages(password: str) -> list[str]:
    errors = []
    if len(password) < 8 or len(password) > 14:
        errors.append("Password must be between 8 and 14 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must include at least one number.")
    if not re.search(r"[^\w\s]", password):
        errors.append("Password must include at least one special character.")
    return errors


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_REGEX.match(phone))


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = {"name": "", "email": "", "phone": ""}
    if request.method == "POST":
        form["name"] = request.form.get("name", "").strip()
        form["email"] = request.form.get("email", "").strip().lower()
        form["phone"] = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not form["name"] or not form["email"] or not form["phone"] or not password or not confirm_password:
            flash("All fields are required. Please complete the form.", "danger")
            return render_template("signup.html", form=form)

        if not validate_email(form["email"]):
            flash("Enter a valid email address.", "danger")
            return render_template("signup.html", form=form)

        if not validate_phone(form["phone"]):
            flash("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.", "danger")
            return render_template("signup.html", form=form)

        if password != confirm_password:
            flash("Password and confirmation do not match.", "danger")
            return render_template("signup.html", form=form)

        password_errors = password_validation_messages(password)
        if password_errors:
            flash(" ".join(password_errors), "danger")
            return render_template("signup.html", form=form)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (form["email"], form["phone"]))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("SELECT id FROM users WHERE email = ?", (form["email"],))
            if cursor.fetchone():
                flash("This email is already registered. Please log in or use another email.", "danger")
            else:
                flash("This phone number is already registered. Please use another phone number.", "danger")
            return render_template("signup.html", form=form)

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
            (form["name"], form["email"], form["phone"], hashed_password),
        )
        db.commit()
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Enter both email and password.", "danger")
            return render_template("login.html", email=email)

        if not validate_email(email):
            flash("Enter a valid email address.", "danger")
            return render_template("login.html", email=email)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, email, phone, created_at FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()
    if not user:
        session.clear()
        flash("User record not found. Please log in again.", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/students")
def students():
    if not session.get("user_id"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
    students_list = cursor.fetchall()
    return render_template("students.html", students=students_list)


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if not session.get("user_id"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    form = {"name": "", "email": "", "phone": "", "course": ""}
    if request.method == "POST":
        form["name"] = request.form.get("name", "").strip()
        form["email"] = request.form.get("email", "").strip().lower()
        form["phone"] = request.form.get("phone", "").strip()
        form["course"] = request.form.get("course", "").strip()

        if not all(form.values()):
            flash("All fields are required.", "danger")
            return render_template("add_student.html", form=form)

        if not validate_email(form["email"]):
            flash("Enter a valid email address.", "danger")
            return render_template("add_student.html", form=form)

        if not validate_phone(form["phone"]):
            flash("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.", "danger")
            return render_template("add_student.html", form=form)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM students WHERE email = ? OR phone = ?", (form["email"], form["phone"]))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("SELECT id FROM students WHERE email = ?", (form["email"],))
            if cursor.fetchone():
                flash("This email is already registered.", "danger")
            else:
                flash("This phone number is already registered.", "danger")
            return render_template("add_student.html", form=form)

        cursor.execute(
            "INSERT INTO students (name, email, phone, course) VALUES (?, ?, ?, ?)",
            (form["name"], form["email"], form["phone"], form["course"]),
        )
        db.commit()
        flash("Student added successfully!", "success")
        return redirect(url_for("students"))

    return render_template("add_student.html", form=form)


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if not session.get("user_id"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        course = request.form.get("course", "").strip()

        if not name or not email or not phone or not course:
            flash("All fields are required.", "danger")
            return render_template("edit_student.html", student=student)

        if not validate_email(email):
            flash("Enter a valid email address.", "danger")
            return render_template("edit_student.html", student=student)

        if not validate_phone(phone):
            flash("Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.", "danger")
            return render_template("edit_student.html", student=student)

        cursor.execute("SELECT id FROM students WHERE (email = ? OR phone = ?) AND id != ?", (email, phone, student_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("SELECT id FROM students WHERE email = ? AND id != ?", (email, student_id))
            if cursor.fetchone():
                flash("This email is already registered.", "danger")
            else:
                flash("This phone number is already registered.", "danger")
            return render_template("edit_student.html", student=student)

        cursor.execute(
            "UPDATE students SET name = ?, email = ?, phone = ?, course = ? WHERE id = ?",
            (name, email, phone, course, student_id),
        )
        db.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("students"))

    return render_template("edit_student.html", student=student)


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    if not session.get("user_id"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("students"))


# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
