from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not username or not email or not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "error": "username, email, and password (at least 8 characters) are required"
        }), 400
    if User.query.filter(or_(User.username == username, User.email == email)).first():
        return jsonify({"error": "Username or email already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identity = str(data.get("username_or_email", "")).strip()
    password = data.get("password", "")

    user = User.query.filter(
        or_(User.username == identity, User.email == identity.lower())
    ).first()

    if not user or not isinstance(password, str) or not user.check_password(password):
        return jsonify({"error": "Invalid username/email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200
