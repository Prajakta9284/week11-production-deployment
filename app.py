import os

from flask import Flask, jsonify

from config import CONFIGS
from extensions import db, jwt, migrate
from logging_config import configure_logging
from routes.auth import auth_bp
from routes.comments import comments_bp
from routes.health import health_bp
from routes.posts import posts_bp


def create_app(test_config=None):
    app = Flask(__name__)

    environment = os.getenv("APP_ENV", "development").lower()
    if environment not in CONFIGS:
        raise RuntimeError(f"Unsupported APP_ENV: {environment}")

    app.config.from_object(CONFIGS[environment])
    if test_config:
        app.config.update(test_config)

    if environment == "production":
        for key in ("SECRET_KEY", "JWT_SECRET_KEY"):
            if not app.config.get(key):
                raise RuntimeError(f"{key} must be configured in production")

    configure_logging(app)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can discover them.
    from models import Comment, Post, User

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(comments_bp, url_prefix="/api")
    app.register_blueprint(health_bp)

    @app.get("/")
    def index():
        return jsonify({
            "name": "Production-Ready Blog API",
            "environment": environment,
            "status": "running",
        })

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled internal server error: %s", error)
        return jsonify({"error": "Internal server error"}), 500

    # Convenient for a first local run. In deployed environments, use
    # `flask db upgrade` as part of the release process instead.
    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()

    return app


app = create_app()
