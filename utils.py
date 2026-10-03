from functools import wraps
from flask import session, redirect, url_for, jsonify, request, flash


def login_required(view):
    """Protect pages (redirect to login) and API routes (401 JSON)."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify(error="Authentication required"), 401
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped
