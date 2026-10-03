"""AI layer. Uses an OpenAI-compatible API when AI_API_KEY is set, otherwise demo mode.

Every public function falls back to the offline demo logic if the API call fails,
so the app never breaks because of the AI provider.
"""
import json
import math
import random
import re

import requests
from flask import current_app

from services.question_bank import GENERAL_TOPICS, HR_BANK, TECH_BANK, TIPS


def ai_enabled():
    return bool(current_app.config.get("AI_API_KEY"))


def mode():
    return "ai" if ai_enabled() else "demo"


def _chat_json(system, user):
    cfg = current_app.config
    resp = requests.post(
        f"{cfg['AI_BASE_URL'].rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {cfg['AI_API_KEY']}"},
        json={
            "model": cfg["AI_MODEL"],
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        },
        timeout=40,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    return json.loads(text)


def _split_counts(itype, count):
    if itype == "technical":
        return count, 0
    if itype == "hr":
        return 0, count
    return math.ceil(count / 2), count // 2


def _user_skills(profile):
    raw = f"{profile.get('skills') or ''},{profile.get('resume_skills') or ''}"
    return list(dict.fromkeys(s.strip().lower() for s in raw.split(",") if s.strip()))


# ---------------------------------------------------------------- questions
def generate_questions(itype, profile, count):
    """Return a list of {text, category, topic, keywords}."""
    if ai_enabled():
        try:
            return _ai_questions(itype, profile, count)
        except Exception as exc:  # noqa: BLE001 - any provider failure -> demo mode
            current_app.logger.warning("AI question generation failed, using demo: %s", exc)
    return _demo_questions(itype, profile, count)


def _ai_questions(itype, profile, count):
    nt, nh = _split_counts(itype, count)
    user = (
        f"Create {nt} technical and {nh} HR/behavioral interview questions for this candidate.\n"
        f"Skills: {', '.join(_user_skills(profile)) or 'not given'}\n"
        f"Education: {profile.get('education') or 'not given'}\n"
        f"Experience: {profile.get('experience') or 'not given'}\n"
        f"Resume excerpt: {(profile.get('resume_text') or '')[:1500]}\n"
        "Personalise questions to their background. Return JSON: "
        '{"questions":[{"text":"...","category":"technical or hr","topic":"1-2 word topic"}]}'
    )
    data = _chat_json("You are an expert interviewer. Reply with JSON only.", user)
    out = []
    for q in data.get("questions", []):
        text = str(q.get("text", "")).strip()
        if not text:
            continue
        cat = "hr" if str(q.get("category", "")).lower().startswith("h") else "technical"
        out.append({"text": text, "category": cat, "topic": str(q.get("topic", "general")).lower()[:40], "keywords": []})
    if not out:
        raise ValueError("AI returned no questions")
    return out[:count]


def _demo_questions(itype, profile, count):
    nt, nh = _split_counts(itype, count)
    skills = [s for s in _user_skills(profile) if s in TECH_BANK]
    topics = skills + [t for t in GENERAL_TOPICS if t not in skills]
    pool = []
    shuffled = {t: random.sample(TECH_BANK[t], len(TECH_BANK[t])) for t in topics}
    for rnd in range(2):  # round-robin so the user's own skills come first
        for t in topics:
            if rnd < len(shuffled[t]):
                q, kw = shuffled[t][rnd]
                pool.append({"text": q, "category": "technical", "topic": t, "keywords": kw})
    tech = pool[:nt]

    hr = []
    exp = (profile.get("experience") or "").strip()
    if exp:
        hr.append({"text": f'Your profile says: "{exp[:120]}". Walk me through your role and biggest contribution.',
                   "category": "hr", "topic": "experience",
                   "keywords": ["responsible", "result", "team", "learned", "impact"]})
    others = random.sample(HR_BANK, len(HR_BANK))
    hr += [{"text": q, "category": "hr", "topic": t, "keywords": kw} for t, q, kw in others]
    return tech + hr[:nh]


# --------------------------------------------------------------- evaluation
def evaluate_answer(question, answer):
    """Return {score(0-10), strengths[], weaknesses[], suggestions[], feedback}."""
    if ai_enabled():
        try:
            return _ai_eval(question, answer)
        except Exception as exc:  # noqa: BLE001
            current_app.logger.warning("AI evaluation failed, using demo: %s", exc)
    return _demo_eval(question, answer)


def _as_list(v):
    if isinstance(v, list):
        return [str(x) for x in v][:5]
    return [str(v)] if v else []


def _ai_eval(question, answer):
    user = (
        f"Interview type: {question['category']}\nQuestion: {question['text']}\nCandidate answer: {answer}\n"
        "Evaluate honestly. Return JSON: "
        '{"score": number 0-10, "strengths":[...], "weaknesses":[...], "suggestions":[...], '
        '"feedback":"2-3 sentence personalised feedback addressed to the candidate"}'
    )
    d = _chat_json("You are a strict but fair interview coach. Reply with JSON only.", user)
    return {
        "score": round(max(0.0, min(10.0, float(d["score"]))), 1),
        "strengths": _as_list(d.get("strengths")) or ["Attempted the question."],
        "weaknesses": _as_list(d.get("weaknesses")) or ["No major weaknesses identified."],
        "suggestions": _as_list(d.get("suggestions")) or ["Keep practising with real examples."],
        "feedback": str(d.get("feedback", "")).strip() or "Thanks for your answer.",
    }


def _demo_eval(question, answer):
    """Transparent heuristic: length + keyword coverage + reasoning words."""
    low = answer.lower()
    n = len(re.findall(r"\w+", low))
    kws = question.get("keywords") or []
    if isinstance(kws, str):
        kws = [k for k in kws.split(",") if k]
    hits = [k for k in kws if k.lower() in low]
    missed = [k for k in kws if k not in hits]
    kw_ratio = len(hits) / len(kws) if kws else 0.5
    markers = set(re.findall(
        r"\b(for example|for instance|because|therefore|first|then|result|situation|task|action|learned)\b", low))
    bonus = 2 if len(markers) >= 2 else (1 if markers else 0)
    score = min(10.0, min(n / 80, 1) * 4 + kw_ratio * 4 + bonus)
    if n < 5:
        score = min(score, 1.5)
    score = round(score, 1)

    strengths, weaknesses, suggestions = [], [], []
    if n >= 60:
        strengths.append("Detailed answer with good depth.")
    elif n >= 30:
        strengths.append("Reasonable answer length.")
    else:
        weaknesses.append("The answer is quite short.")
        suggestions.append("Aim for 4-6 sentences that explain the idea and give an example.")
    if hits:
        strengths.append("Covered key ideas: " + ", ".join(hits[:4]) + ".")
    if missed and kws:
        weaknesses.append("Did not mention: " + ", ".join(missed[:4]) + ".")
        suggestions.append("Try to work in concepts such as " + ", ".join(missed[:3]) + ".")
    if bonus:
        strengths.append("Supported points with reasoning or examples.")
    else:
        weaknesses.append("Lacks examples or reasoning.")
        suggestions.append("Back each claim with a concrete example from a project or class.")
    if question["category"] == "hr":
        suggestions.append("Structure it with STAR: Situation, Task, Action, Result.")
    strengths = strengths or ["You attempted the question."]
    weaknesses = weaknesses or ["No major weaknesses detected."]

    if score >= 8:
        verdict = "Excellent answer - confident and well supported."
    elif score >= 6:
        verdict = "Good answer with room to add depth."
    elif score >= 4:
        verdict = "Average answer - tighten it and cover the core concepts."
    else:
        verdict = "This answer needs more substance and structure."
    feedback = f"On '{question['topic']}' you scored {score}/10. {verdict} (Demo mode: heuristic scoring.)"
    return {"score": score, "strengths": strengths, "weaknesses": weaknesses,
            "suggestions": suggestions, "feedback": feedback}


# ---------------------------------------------------------- recommendations
def recommend_topics(weak_topics):
    """weak_topics: list of topic names. Returns [{topic, tip}]."""
    if not weak_topics:
        return []
    if ai_enabled():
        try:
            d = _chat_json(
                "You are an interview coach. Reply with JSON only.",
                f"The candidate is weak in: {', '.join(weak_topics)}. Return "
                '{"recommendations":[{"topic":"...","tip":"one actionable sentence"}]}')
            recs = [{"topic": str(r["topic"]), "tip": str(r["tip"])} for r in d["recommendations"]]
            if recs:
                return recs
        except Exception as exc:  # noqa: BLE001
            current_app.logger.warning("AI recommendations failed, using demo: %s", exc)
    return [{"topic": t, "tip": TIPS.get(t, f"Revisit core {t} concepts and practise explaining them aloud with an example.")}
            for t in weak_topics]
