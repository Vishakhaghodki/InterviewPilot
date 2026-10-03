from flask import Blueprint, abort, redirect, render_template, session, url_for

from database import query
from services import interview_service as svc
from utils import login_required

bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@bp.route("/profile")
@login_required
def profile():
    u = query("""SELECT u.name,u.email,p.skills,p.education,p.experience,p.resume_filename
                 FROM users u JOIN profiles p ON p.user_id=u.id WHERE u.id=?""", (session["user_id"],), one=True)
    return render_template("profile.html", u=u)


@bp.route("/resume")
@login_required
def resume():
    p = query("SELECT resume_filename, resume_skills FROM profiles WHERE user_id=?", (session["user_id"],), one=True)
    return render_template("resume.html", p=p)


@bp.route("/interview/setup")
@login_required
def setup():
    return render_template("setup.html")


@bp.route("/interview/<int:iid>")
@login_required
def interview(iid):
    iv = svc.owned(session["user_id"], iid) or abort(404)
    if iv["status"] == "completed":
        return redirect(url_for("pages.result", iid=iid))
    return render_template("session.html", iid=iid)


@bp.route("/interview/<int:iid>/result")
@login_required
def result(iid):
    iv = svc.owned(session["user_id"], iid) or abort(404)
    if iv["status"] != "completed":
        return redirect(url_for("pages.interview", iid=iid))
    return render_template("result.html", iid=iid)


@bp.route("/history")
@login_required
def history():
    return render_template("history.html")


@bp.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")
