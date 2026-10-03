"""Business logic for interviews (kept out of the route handlers)."""
import json

from database import execute, query
from services import ai_service


def create_interview(user_id, itype, count):
    profile = query("SELECT * FROM profiles WHERE user_id=?", (user_id,), one=True)
    questions = ai_service.generate_questions(itype, dict(profile) if profile else {}, count)
    iid = execute("INSERT INTO interviews(user_id,type,ai_mode) VALUES(?,?,?)",
                  (user_id, itype, ai_service.mode()))
    for pos, q in enumerate(questions, 1):
        execute("INSERT INTO questions(interview_id,position,text,category,topic,keywords) VALUES(?,?,?,?,?,?)",
                (iid, pos, q["text"], q["category"], q["topic"], ",".join(q.get("keywords", []))))
    return iid


def owned(user_id, interview_id):
    return query("SELECT * FROM interviews WHERE id=? AND user_id=?", (interview_id, user_id), one=True)


def submit_answer(interview_id, question_id, text):
    q = query("SELECT * FROM questions WHERE id=? AND interview_id=?", (question_id, interview_id), one=True)
    if not q:
        raise LookupError("Question not found in this interview.")
    if query("SELECT id FROM answers WHERE question_id=?", (question_id,), one=True):
        raise ValueError("This question was already answered.")
    ev = ai_service.evaluate_answer(dict(q), text)
    aid = execute("INSERT INTO answers(question_id,answer_text) VALUES(?,?)", (question_id, text))
    execute("INSERT INTO evaluations(answer_id,score,strengths,weaknesses,suggestions,feedback) VALUES(?,?,?,?,?,?)",
            (aid, ev["score"], json.dumps(ev["strengths"]), json.dumps(ev["weaknesses"]),
             json.dumps(ev["suggestions"]), ev["feedback"]))
    return ev


def detail(interview_id):
    iv = dict(query("SELECT * FROM interviews WHERE id=?", (interview_id,), one=True))
    rows = query(
        """SELECT q.id, q.position, q.text, q.category, q.topic, a.answer_text,
                  e.score, e.strengths, e.weaknesses, e.suggestions, e.feedback
           FROM questions q
           LEFT JOIN answers a ON a.question_id = q.id
           LEFT JOIN evaluations e ON e.answer_id = a.id
           WHERE q.interview_id=? ORDER BY q.position""", (interview_id,))
    qs = []
    for r in rows:
        d = dict(r)
        d["answered"] = d["answer_text"] is not None
        for k in ("strengths", "weaknesses", "suggestions"):
            d[k] = json.loads(d[k]) if d[k] else []
        qs.append(d)
    iv["questions"] = qs
    return iv


def answered_count(interview_id):
    return query("""SELECT COUNT(*) c FROM answers a JOIN questions q ON q.id=a.question_id
                    WHERE q.interview_id=?""", (interview_id,), one=True)["c"]


def finalize(interview_id):
    """Mark complete, compute scores and write the interview_history row."""
    iv = query("SELECT * FROM interviews WHERE id=?", (interview_id,), one=True)
    if iv["status"] == "completed":
        return
    rows = query("""SELECT q.category, e.score FROM questions q
                    JOIN answers a ON a.question_id=q.id JOIN evaluations e ON e.answer_id=a.id
                    WHERE q.interview_id=?""", (interview_id,))

    def avg(cat=None):
        s = [r["score"] for r in rows if cat is None or r["category"] == cat]
        return round(sum(s) / len(s), 1) if s else None

    overall, tech, hr = avg(), avg("technical"), avg("hr")
    summary = f"Answered {len(rows)} question(s) in a {iv['type']} interview. Average score {overall}/10."
    execute("UPDATE interviews SET status='completed', avg_score=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
            (overall, interview_id))
    execute("""INSERT INTO interview_history(user_id,interview_id,interview_type,avg_score,technical_score,hr_score,summary)
               VALUES(?,?,?,?,?,?,?)""", (iv["user_id"], interview_id, iv["type"], overall, tech, hr, summary))
