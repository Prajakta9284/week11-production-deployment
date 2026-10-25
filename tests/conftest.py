import pytest

from app import create_app
from extensions import db


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SQLALCHEMY_ENGINE_OPTIONS": {},
        "AUTO_CREATE_TABLES": False,
        "SECRET_KEY": "test-secret",
        "JWT_SECRET_KEY": "test-jwt-secret",
        "FEATURE_POST_EXPORT": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
