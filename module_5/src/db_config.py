"""Database connection settings loaded from environment variables."""

import os


def connection_kwargs():
    """Return psycopg keyword arguments from DB_* environment variables."""
    kwargs = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    return {key: value for key, value in kwargs.items() if value}


def database_url():
    """Return an optional full PostgreSQL URL from the environment."""
    return os.getenv("DATABASE_URL")
