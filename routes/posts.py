import csv
import io

from flask import Blueprint, Response, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Post

posts_bp = Blueprint("posts", __name__)


@posts_bp.get("")
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify({"posts": [p.to_dict() for p in posts]}), 200


@posts_bp.post("")
@jwt_required()
def create_post():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    body = str(data.get("body", "")).strip()
    if not title or not body:
        return jsonify({"error": "title and body are required"}), 400
    post = Post(
        title=title,
        body=body,
        user_id=int(get_jwt_identity()),
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({"post": post.to_dict()}), 201


@posts_bp.get("/<int:post_id>")
def get_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"post": post.to_dict(include_comments=True)}), 200


@posts_bp.delete("/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You can delete only your own posts"}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"}), 200


@posts_bp.get("/export.csv")
def export_posts():
    if not current_app.config.get("FEATURE_POST_EXPORT", False):
        return jsonify({"error": "Post export is currently disabled"}), 404

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "body", "author", "created_at"])
    for post in Post.query.order_by(Post.id).all():
        writer.writerow([
            post.id, post.title, post.body,
            post.author.username if post.author else "",
            post.created_at.isoformat() if post.created_at else "",
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=posts.csv"},
    )
