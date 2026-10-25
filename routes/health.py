from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
@health_bp.get("/health/live")
def liveness():
    return jsonify({"status": "alive"}), 200


@health_bp.get("/health/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ready", "database": "connected"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"status": "not_ready"}), 503
    finally:
        db.session.remove()
