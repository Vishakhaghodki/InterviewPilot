"""Offline question bank used in demo mode (and as personalisation source)."""

# topic -> [(question, [keywords used by the demo evaluator])]
TECH_BANK = {
    "python": [
        ("What is the difference between a list and a tuple in Python, and when would you use each?",
         ["mutable", "immutable", "tuple", "list", "hashable", "performance"]),
        ("Explain how decorators work in Python and give a practical example.",
         ["function", "wrapper", "closure", "logging", "arguments", "returns"]),
    ],
    "sql": [
        ("Explain the difference between INNER JOIN and LEFT JOIN with an example.",
         ["inner", "left", "null", "match", "rows", "table"]),
        ("What is database normalization and why does it matter?",
         ["redundancy", "normal form", "integrity", "anomaly", "tables", "duplicate"]),
    ],
    "javascript": [
        ("What is the difference between var, let and const in JavaScript?",
         ["scope", "hoisting", "block", "reassign", "function", "const"]),
        ("Explain how promises and async/await help with asynchronous code.",
         ["callback", "promise", "await", "async", "then", "error"]),
    ],
    "flask": [
        ("How does routing work in Flask, and what are blueprints used for?",
         ["route", "decorator", "blueprint", "modular", "url", "view"]),
        ("How would you protect Flask routes so only logged-in users can access them?",
         ["session", "login", "decorator", "password", "hash", "cookie"]),
    ],
    "html": [
        ("What is semantic HTML and why is it important?",
         ["semantic", "accessibility", "seo", "header", "article", "screen reader"]),
        ("How do you make a web page responsive?",
         ["media query", "flexbox", "grid", "viewport", "relative", "mobile"]),
    ],
    "git": [
        ("What is the difference between git merge and git rebase?",
         ["history", "merge", "rebase", "commit", "branch", "conflict"]),
        ("How do you resolve a merge conflict in Git?",
         ["conflict", "markers", "edit", "add", "commit", "branch"]),
    ],
    "data structures": [
        ("Compare arrays and linked lists. When is each a better choice?",
         ["index", "memory", "insertion", "pointer", "traversal", "size"]),
        ("How does a hash map work and what happens when there is a collision?",
         ["hash", "bucket", "collision", "chaining", "key", "lookup"]),
    ],
    "algorithms": [
        ("Explain binary search and its time complexity.",
         ["sorted", "middle", "log", "half", "compare", "complexity"]),
        ("What is the difference between BFS and DFS?",
         ["queue", "stack", "graph", "level", "depth", "visited"]),
    ],
    "oop": [
        ("Explain the four pillars of object-oriented programming with examples.",
         ["encapsulation", "inheritance", "polymorphism", "abstraction", "class", "object"]),
        ("What is the difference between inheritance and composition?",
         ["reuse", "coupling", "flexible", "class", "relationship", "object"]),
    ],
}

GENERAL_TOPICS = ["data structures", "oop", "algorithms", "sql", "git", "python"]

# (topic, question, keywords)
HR_BANK = [
    ("teamwork", "Tell me about a time you worked in a team to achieve a goal. What was your role?",
     ["team", "role", "goal", "communication", "result", "together"]),
    ("conflict", "Describe a disagreement with a teammate and how you resolved it.",
     ["listen", "conflict", "compromise", "understand", "resolved", "communication"]),
    ("strengths", "What are your greatest strengths and how have they helped you?",
     ["strength", "example", "result", "skill", "helped"]),
    ("weaknesses", "What is one weakness you are working on, and what are you doing about it?",
     ["weakness", "improve", "learn", "feedback", "progress", "working"]),
    ("failure", "Tell me about a time you failed. What did you learn?",
     ["failed", "mistake", "learn", "changed", "responsibility", "next time"]),
    ("motivation", "Why do you want this role, and where do you see yourself in five years?",
     ["goal", "grow", "interest", "company", "learn", "career"]),
    ("time management", "How do you prioritize when you have multiple deadlines at once?",
     ["prioritize", "deadline", "plan", "schedule", "important", "urgent"]),
    ("adaptability", "Describe a time you had to learn something new quickly.",
     ["learn", "new", "quickly", "resources", "practice", "applied"]),
]

TIPS = {
    "python": "Practice core data types, comprehensions, decorators and generators; solve 3 small problems a day.",
    "sql": "Rewrite JOIN, GROUP BY and subquery examples from memory on a sample database.",
    "javascript": "Review scope, closures, the event loop and promises; build one small fetch-based page.",
    "flask": "Re-read routing, blueprints, sessions and request handling; explain this project's architecture aloud.",
    "html": "Rebuild a page using semantic tags and a mobile-first responsive layout.",
    "git": "Practice branching, merging, rebasing and conflict resolution in a throw-away repo.",
    "data structures": "Implement a stack, queue, linked list and hash map from scratch and state their complexities.",
    "algorithms": "Practice binary search, BFS/DFS and sorting; always state time and space complexity.",
    "oop": "Explain each OOP pillar with a real example from your own projects.",
    "teamwork": "Prepare two STAR stories (Situation, Task, Action, Result) about group projects.",
    "conflict": "Prepare a calm, specific story about resolving a disagreement with a concrete outcome.",
    "strengths": "Pick 3 strengths and attach a real example and result to each.",
    "weaknesses": "Choose a genuine weakness and describe the concrete steps you are taking to improve.",
    "failure": "Prepare a failure story that focuses on what you learned and changed.",
    "motivation": "Research the company and link your goals to the role in 2-3 sentences.",
    "time management": "Describe a prioritisation method (e.g. urgent/important matrix) with a real example.",
    "adaptability": "Prepare a story where you learned a new tool or skill under time pressure.",
}
