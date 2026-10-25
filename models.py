from datetime import UTC, datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(UTC)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    posts = db.relationship("Post", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship(
        "Comment", backref="post", cascade="all, delete-orphan", lazy=True
    )

    def to_dict(self, include_comments=False):
        result = {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "user_id": self.user_id,
            "author": self.author.username if self.author else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_comments:
            result["comments"] = [c.to_dict() for c in self.comments]
        return result


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user = db.relationship("User", backref="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "body": self.body,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "author": self.user.username if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
