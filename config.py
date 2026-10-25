
import os
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///local.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "text")
    FEATURE_POST_EXPORT = os.getenv(
        "FEATURE_POST_EXPORT", "false"
    ).strip().lower() in {"true", "1", "yes", "on"}
    AUTO_CREATE_TABLES = os.getenv(
        "AUTO_CREATE_TABLES", "true"
    ).strip().lower() in {"true", "1", "yes", "on"}


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class StagingConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    AUTO_CREATE_TABLES = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    AUTO_CREATE_TABLES = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {}
    AUTO_CREATE_TABLES = True


CONFIGS = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
