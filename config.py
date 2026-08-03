import os


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key-change-before-deployment",
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///home_secretary.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False