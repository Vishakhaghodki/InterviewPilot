# InterviewPilot - AI Interview Preparation Platform

A Flask web app that helps students practise technical and HR interviews. It builds questions from your resume and skills, scores each answer with AI, and tracks your progress with charts. It runs fully offline in **demo mode** when no API key is set.

![Home](docs/screenshots/home.png) <!-- placeholder -->
![Dashboard](docs/screenshots/dashboard.png) <!-- placeholder -->
![Interview session](docs/screenshots/session.png) <!-- placeholder -->
![Result](docs/screenshots/result.png) <!-- placeholder -->

## Features
- Registration, login, logout (hashed passwords, session auth)
- Profile: name, skills, education, experience, resume
- Resume upload (PDF / DOCX / TXT) with text extraction and skill detection
- Technical, HR and Mixed mock interviews with personalised questions
- Per-answer score (0-10), strengths, weaknesses, suggestions and personalised feedback
- Dashboard + analytics: average score, technical vs HR, trend over time, weak topics
- Topic recommendations, interview history, responsive UI, validation and error handling

## Tech stack
Python, Flask, SQLite (`sqlite3`), HTML/CSS/vanilla JavaScript, Chart.js (CDN), REST JSON APIs, any OpenAI-compatible chat API via `requests`.

## Architecture
```
Browser (HTML + JS fetch) -> routes/ (Flask blueprints) -> services/ (business logic) -> SQLite
                                  pages.py  HTML pages          interview_service.py  create/answer/finalize
                                  auth.py   register/login      ai_service.py         AI + demo fallback
                                  api.py    JSON REST API       analytics.py          stats for charts
                                                                resume_parser.py      text + skills
```
- **Routes stay thin**; logic lives in `services/`.
- **AI fallback:** `ai_service.py` calls the AI API only if `AI_API_KEY` is set. If the key is missing *or a call fails*, it uses the offline question bank and a transparent heuristic scorer (length + keyword coverage + reasoning words).
- **Database tables:** users, profiles, interviews, questions, answers, evaluations, interview_history.

## Installation (Windows)
```bat
git clone <your-repo-url>
cd interviewpilot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
PowerShell: use `venv\Scripts\Activate.ps1` (if blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).

## Environment variables (`.env`)
| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs session cookies. Use a long random string. |
| `AI_API_KEY` | Your AI provider key. **Empty = demo mode.** |
| `AI_BASE_URL` | OpenAI-compatible base URL (default `https://api.openai.com/v1`) |
| `AI_MODEL` | Model name (default `gpt-4o-mini`) |
| `FLASK_DEBUG` | `1` for debug mode while developing |

Never commit `.env` (it is in `.gitignore`).

## Database setup
Tables are created automatically on startup. To do it manually and load demo data:
```bat
flask --app app init-db
flask --app app seed-demo
```
Demo login: `demo@interviewpilot.com` / `demo1234` (4 completed interviews so charts are populated).

## How to run
```bat
python app.py
```
Open http://127.0.0.1:5000

## API documentation
All endpoints return JSON and (except `/api/health`) require a logged-in session cookie. Errors look like `{"error": "message"}`.

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `/api/health` | - | Status and AI mode |
| GET | `/api/profile` | - | Get profile |
| PUT | `/api/profile` | `name, skills, education, experience` | Update profile |
| POST | `/api/resume` | multipart `resume` file | Upload + parse resume |
| POST | `/api/interviews` | `{"type":"hr\|technical\|mixed","num_questions":5}` | Create interview, returns `interview_id` |
| GET | `/api/interviews` | - | Completed interview history |
| GET | `/api/interviews/<id>` | - | Interview with questions, answers, evaluations |
| POST | `/api/interviews/<id>/answer` | `{"question_id":1,"answer":"..."}` | Evaluate an answer |
| POST | `/api/interviews/<id>/complete` | - | Finish and save results |
| GET | `/api/analytics` | - | Stats for charts |
| GET | `/api/recommendations` | - | Topics to improve |

Status codes: 200/201 success, 400 validation error, 401 not logged in, 404 not found, 409 conflict (already answered/completed), 413 file too large.

## Example interview workflow
1. Register, then fill in **Profile** (skills such as "Python, Flask, SQL").
2. Upload a resume on the **Resume** page; detected skills are shown.
3. **Start interview** -> choose Mixed, 5 questions.
4. Answer each question -> instant score, strengths, weaknesses, suggestions.
5. Finish -> **Results** page. Then check **Dashboard**, **History**, **Analytics**.

## Future improvements
- CSRF protection (Flask-WTF) and rate limiting
- Voice answers (speech-to-text) and timed questions
- Difficulty levels, company-specific question sets
- PostgreSQL + Flask-Migrate, Docker, automated tests (pytest)
- Better resume parsing (NER) and exportable PDF reports
