"""Demo data: user demo@interviewpilot.com / demo1234 with 4 completed interviews."""
import json
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from database import execute, query
from services import interview_service
from services.question_bank import HR_BANK, TECH_BANK

DEMO_EMAIL = "demo@interviewpilot.com"

# (days_ago, type, [(category, topic, score)])
SAMPLES = [
    (14, "technical", [("technical", "python", 6.5), ("technical", "sql", 4.5),
                       ("technical", "data structures", 5.0), ("technical", "flask", 7.0)]),
    (10, "hr", [("hr", "teamwork", 7.5), ("hr", "conflict", 5.5), ("hr", "failure", 6.0)]),
    (6, "mixed", [("technical", "javascript", 6.0), ("technical", "algorithms", 4.0),
                  ("hr", "motivation", 7.0), ("hr", "time management", 6.5)]),
    (2, "technical", [("technical", "python", 7.5), ("technical", "sql", 6.0),
                      ("technical", "oop", 7.0), ("technical", "algorithms", 5.0)]),
]


def _question_text(category, topic):
    if category == "technical":
        return TECH_BANK[topic][0][0]
    return next(q for t, q, _ in HR_BANK if t == topic)


def seed_demo():
    if query("SELECT id FROM users WHERE email=?", (DEMO_EMAIL,), one=True):
        return False
    uid = execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                  ("Demo Student", DEMO_EMAIL, generate_password_hash("demo1234")))
    execute("INSERT INTO profiles(user_id,skills,education,experience) VALUES(?,?,?,?)",
            (uid, "Python, Flask, SQL, JavaScript", "B.Tech in Computer Science (2025)",
             "Intern at a startup - built REST APIs with Flask and SQLite."))
    for days_ago, itype, items in SAMPLES:
        when = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        iid = execute("INSERT INTO interviews(user_id,type,ai_mode,started_at) VALUES(?,?,?,?)",
                      (uid, itype, "demo", when))
        for pos, (cat, topic, score) in enumerate(items, 1):
            qid = execute("INSERT INTO questions(interview_id,position,text,category,topic) VALUES(?,?,?,?,?)",
                          (iid, pos, _question_text(cat, topic), cat, topic))
            aid = execute("INSERT INTO answers(question_id,answer_text) VALUES(?,?)",
                          (qid, "Sample demo answer used for seeded data."))
            execute("INSERT INTO evaluations(answer_id,score,strengths,weaknesses,suggestions,feedback) VALUES(?,?,?,?,?,?)",
                    (aid, score, json.dumps(["Clear structure."]), json.dumps(["Could add more depth."]),
                     json.dumps(["Add a concrete example."]), "Sample feedback (seeded demo data)."))
        interview_service.finalize(iid)
        execute("UPDATE interviews SET completed_at=? WHERE id=?", (when, iid))
        execute("UPDATE interview_history SET created_at=? WHERE interview_id=?", (when, iid))
    return True
