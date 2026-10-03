"""Basic resume parsing: text extraction + keyword-based skill detection."""
import re

SKILLS = ["python", "java", "javascript", "typescript", "c++", "c#", "sql", "mysql", "postgresql",
          "sqlite", "mongodb", "flask", "django", "fastapi", "react", "node.js", "html", "css", "git",
          "docker", "aws", "linux", "machine learning", "data structures", "algorithms", "oop",
          "rest api", "pandas", "numpy", "tensorflow"]


def extract_text(path, ext):
    if ext == "pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if ext == "docx":
        import docx
        return "\n".join(p.text for p in docx.Document(path).paragraphs)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_resume(text):
    low = text.lower()
    skills = [s for s in SKILLS
              if re.search(r"(?<![\w+#])" + re.escape(s) + r"(?![\w+#])", low)]
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    edu = [ln.strip() for ln in text.splitlines()
           if re.search(r"\b(b\.?tech|b\.?sc|m\.?tech|m\.?sc|bachelor|master|university|college|degree)\b", ln, re.I)][:3]
    return {"skills": skills, "email": email.group(0) if email else None,
            "education": edu, "word_count": len(text.split())}
