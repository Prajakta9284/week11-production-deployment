from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Comment, Post

comments_bp = Blueprint("comments", __name__)


@comments_bp.post("/posts/<int:post_id>/comments")
@jwt_required()
def create_comment(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json(silent=True) or {}
    body = str(data.get("body", "")).strip()
    if not body:
        return jsonify({"error": "body is required"}), 400

    comment = Comment(
        body=body,
        post_id=post.id,
        user_id=int(get_jwt_identity()),
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"comment": comment.to_dict()}), 201


@comments_bp.get("/posts/<int:post_id>/comments")
def list_comments(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"comments": [c.to_dict() for c in post.comments]}), 200
