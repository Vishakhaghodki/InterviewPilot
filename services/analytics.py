"""Performance statistics for the dashboard and analytics page."""
from database import query

WEAK_THRESHOLD = 6.5


def _avg(values):
    return round(sum(values) / len(values), 1) if values else None


def get_stats(user_id):
    rows = query(
        """SELECT q.category, q.topic, e.score FROM evaluations e
           JOIN answers a ON a.id=e.answer_id JOIN questions q ON q.id=a.question_id
           JOIN interviews i ON i.id=q.interview_id WHERE i.user_id=?""", (user_id,))
    completed = query("SELECT COUNT(*) c FROM interviews WHERE user_id=? AND status='completed'",
                      (user_id,), one=True)["c"]
    timeline = query("""SELECT interview_id, interview_type, avg_score, created_at FROM interview_history
                        WHERE user_id=? ORDER BY created_at, id LIMIT 30""", (user_id,))
    by_topic = {}
    for r in rows:
        by_topic.setdefault(r["topic"], []).append(r["score"])
    topics = sorted(({"topic": t, "avg": _avg(s), "count": len(s)} for t, s in by_topic.items()),
                    key=lambda x: x["avg"])
    return {
        "average_score": _avg([r["score"] for r in rows]),
        "interviews_completed": completed,
        "answers_count": len(rows),
        "technical_avg": _avg([r["score"] for r in rows if r["category"] == "technical"]),
        "hr_avg": _avg([r["score"] for r in rows if r["category"] == "hr"]),
        "timeline": [{"interview_id": t["interview_id"], "type": t["interview_type"],
                      "score": t["avg_score"], "date": (t["created_at"] or "")[:10]} for t in timeline],
        "topics": topics,
        "weak_topics": [t for t in topics if t["avg"] < WEAK_THRESHOLD][:6],
    }
