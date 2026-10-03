"""REST API (JSON). All routes except /health require a logged-in session."""
import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.utils import secure_filename

from database import execute, query
from services import ai_service, analytics, resume_parser
from services import interview_service as svc
from utils import login_required

bp = Blueprint("api", __name__, url_prefix="/api")
ALLOWED_EXT = {"pdf", "docx", "txt"}


def err(msg, code=400):
    return jsonify(error=msg), code


@bp.get("/health")
def health():
    return jsonify(status="ok", ai_mode=ai_service.mode())


# ------------------------------------------------------------------ profile
@bp.get("/profile")
@login_required
def get_profile():
    u = query("SELECT name,email FROM users WHERE id=?", (session["user_id"],), one=True)
    p = query("SELECT skills,education,experience,resume_filename,resume_skills FROM profiles WHERE user_id=?",
              (session["user_id"],), one=True)
    return jsonify({**dict(u), **dict(p)})


@bp.put("/profile")
@login_required
def update_profile():
    d = request.get_json(silent=True) or {}
    name = str(d.get("name", "")).strip()
    if not 2 <= len(name) <= 80:
        return err("Name must be 2-80 characters.")
    f = {k: str(d.get(k, "")).strip() for k in ("skills", "education", "experience")}
    if any(len(v) > 2000 for v in f.values()):
        return err("Each profile field must be under 2000 characters.")
    uid = session["user_id"]
    execute("UPDATE users SET name=? WHERE id=?", (name, uid))
    execute("UPDATE profiles SET skills=?,education=?,experience=?,updated_at=CURRENT_TIMESTAMP WHERE user_id=?",
            (f["skills"], f["education"], f["experience"], uid))
    session["user_name"] = name
    return jsonify(message="Profile updated")


@bp.post("/resume")
@login_required
def upload_resume():
    file = request.files.get("resume")
    if not file or not file.filename:
        return err("No file selected.")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXT:
        return err("Only PDF, DOCX or TXT files are allowed.")
    original = secure_filename(file.filename)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}_{original}")
    file.save(path)
    try:
        text = resume_parser.extract_text(path, ext)
    except Exception:  # noqa: BLE001
        os.remove(path)
        return err("Could not read this file. Try another one.")
    if len(text.strip()) < 30:
        os.remove(path)
        return err("No readable text found (scanned PDFs are not supported).")
    parsed = resume_parser.parse_resume(text)
    execute("UPDATE profiles SET resume_filename=?, resume_text=?, resume_skills=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?",
            (original, text[:20000], ", ".join(parsed["skills"]), session["user_id"]))
    return jsonify(filename=original, parsed=parsed)


# --------------------------------------------------------------- interviews
@bp.post("/interviews")
@login_required
def start_interview():
    d = request.get_json(silent=True) or {}
    itype = d.get("type")
    if itype not in ("hr", "technical", "mixed"):
        return err("Type must be hr, technical or mixed.")
    try:
        n = int(d.get("num_questions", 5))
    except (TypeError, ValueError):
        return err("num_questions must be a number.")
    if not 2 <= n <= 10:
        return err("num_questions must be between 2 and 10.")
    return jsonify(interview_id=svc.create_interview(session["user_id"], itype, n)), 201


@bp.get("/interviews")
@login_required
def list_interviews():
    rows = query("""SELECT interview_id, interview_type, avg_score, technical_score, hr_score, summary, created_at
                    FROM interview_history WHERE user_id=? ORDER BY created_at DESC, id DESC""", (session["user_id"],))
    return jsonify(interviews=[dict(r) for r in rows])


@bp.get("/interviews/<int:iid>")
@login_required
def get_interview(iid):
    if not svc.owned(session["user_id"], iid):
        return err("Interview not found.", 404)
    return jsonify(svc.detail(iid))


@bp.post("/interviews/<int:iid>/answer")
@login_required
def answer(iid):
    iv = svc.owned(session["user_id"], iid)
    if not iv:
        return err("Interview not found.", 404)
    if iv["status"] == "completed":
        return err("This interview is already completed.", 409)
    d = request.get_json(silent=True) or {}
    text = str(d.get("answer", "")).strip()
    if len(text) < 5:
        return err("Please write a longer answer (at least 5 characters).")
    if len(text) > 5000:
        return err("Answer is too long (max 5000 characters).")
    try:
        qid = int(d.get("question_id"))
        return jsonify(evaluation=svc.submit_answer(iid, qid, text))
    except (TypeError, ValueError) as e:
        code = 409 if "already" in str(e) else 400
        return err(str(e) if code == 409 else "Invalid question_id.", code)
    except LookupError as e:
        return err(str(e), 404)


@bp.post("/interviews/<int:iid>/complete")
@login_required
def complete(iid):
    if not svc.owned(session["user_id"], iid):
        return err("Interview not found.", 404)
    if svc.answered_count(iid) == 0:
        return err("Answer at least one question before finishing.")
    svc.finalize(iid)
    return jsonify(svc.detail(iid))


# ---------------------------------------------------------------- analytics
@bp.get("/analytics")
@login_required
def get_analytics():
    return jsonify(analytics.get_stats(session["user_id"]))


@bp.get("/recommendations")
@login_required
def recommendations():
    weak = [t["topic"] for t in analytics.get_stats(session["user_id"])["weak_topics"]]
    return jsonify(recommendations=ai_service.recommend_topics(weak))
