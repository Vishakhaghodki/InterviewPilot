import re
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import execute, query

bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = []
        if not 2 <= len(name) <= 80:
            errors.append("Name must be 2-80 characters.")
        if not EMAIL_RE.match(email):
            errors.append("Enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not errors and query("SELECT id FROM users WHERE email=?", (email,), one=True):
            errors.append("An account with this email already exists. Try logging in.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", name=name, email=email), 400
        uid = execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                      (name, email, generate_password_hash(password)))
        execute("INSERT INTO profiles(user_id) VALUES(?)", (uid,))
        session.clear()
        session["user_id"], session["user_name"] = uid, name
        flash("Welcome to InterviewPilot! Complete your profile for personalised questions.", "success")
        return redirect(url_for("pages.profile"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = query("SELECT * FROM users WHERE email=?", (email,), one=True)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Incorrect email or password.", "error")
            return render_template("login.html", email=email), 401
        session.clear()
        session["user_id"], session["user_name"] = user["id"], user["name"]
        return redirect(url_for("pages.dashboard"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("pages.home"))
