import os
from flask import Flask, jsonify, render_template, request

import database
from config import Config
from routes.api import bp as api_bp
from routes.auth import bp as auth_bp
from routes.pages import bp as pages_bp
from services import ai_service
from services.seed import seed_demo


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.teardown_appcontext(database.close_db)
    for bp in (auth_bp, pages_bp, api_bp):
        app.register_blueprint(bp)

    with app.app_context():
        database.init_db()  # creates tables if they don't exist

    @app.context_processor
    def inject_globals():
        return {"ai_mode": ai_service.mode()}

    def error_response(code, message):
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("error.html", code=code, message=message), code

    @app.errorhandler(404)
    def not_found(e):
        return error_response(404, "That page or resource does not exist.")

    @app.errorhandler(413)
    def too_large(e):
        return error_response(413, "File too large. Maximum size is 5 MB.")

    @app.errorhandler(500)
    def server_error(e):
        return error_response(500, "Something went wrong on our side. Please try again.")

    @app.cli.command("init-db")
    def init_db_cmd():
        """Create database tables."""
        database.init_db()
        print("Database initialised.")

    @app.cli.command("seed-demo")
    def seed_cmd():
        """Add a demo user (demo@interviewpilot.com / demo1234) with sample history."""
        print("Demo data added." if seed_demo() else "Demo user already exists.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
