"""Shared fixtures for the Module 4 test suite."""

import pytest

from src import app as app_module

ALLOWED_MARKERS = {"web", "buttons", "analysis", "db", "integration"}


def pytest_collection_modifyitems(items):
    """Fail collection when a test has none of the required markers."""
    unmarked = [
        item.nodeid
        for item in items
        if not ALLOWED_MARKERS.intersection(item.keywords)
    ]
    if unmarked:
        raise pytest.UsageError(
            "Tests missing a required marker: " + ", ".join(unmarked)
        )


class FakeCursor:
    """Small DB cursor test double for Flask page rendering tests."""

    def __init__(self):
        self.results = iter(
            [
                (12,),
                (39.28,),
                (3.80, 320.00, 160.00, 4.50),
                (3.75,),
                (42.50,),
                (3.90,),
                (2,),
                (3,),
                (4,),
                [("Johns Hopkins University", 10)],
                ("PhD", 3.95),
            ]
        )

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query, params=None):
        """Accept composed SQL and optional params like a psycopg cursor."""
        self.result = next(self.results)

    def fetchone(self):
        return self.result

    def fetchall(self):
        return self.result

    def close(self):
        pass


class FakeConnection:
    def cursor(self):
        return FakeCursor()

    def close(self):
        pass


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(app_module, "get_db_connection", FakeConnection)
    return app_module.create_app({"TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()
