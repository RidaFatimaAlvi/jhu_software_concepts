"""Tests for small application helper functions."""

import pytest

from src import app as app_module
from src import pull_data


@pytest.mark.buttons
def test_pull_data_helper():
    rows = [{"url": "https://example.test/1"}]
    loaded = []

    result = pull_data.pull_data(
        scraper=lambda: rows,
        loader=lambda values: loaded.extend(values) or 1,
    )

    assert result == 1
    assert loaded == rows


@pytest.mark.buttons
def test_app_database_connection(monkeypatch):
    calls = []
    monkeypatch.setattr(
        app_module.psycopg,
        "connect",
        lambda *args, **kwargs: calls.append((args, kwargs)) or "connection",
    )

    app_module.app.config["DATABASE_URL"] = "postgresql://test"
    assert app_module.get_db_connection() == "connection"

    app_module.app.config["DATABASE_URL"] = None
    assert app_module.get_db_connection() == "connection"


@pytest.mark.buttons
def test_run_pull_data(monkeypatch):
    calls = []
    monkeypatch.setattr(
        app_module.subprocess,
        "run",
        lambda command, check: calls.append((command, check)),
    )
    app_module.pull_data_running = True

    app_module.run_pull_data()

    assert calls == [(["python", "pull_data.py"], True)]
    assert app_module.pull_data_running is False


@pytest.mark.buttons
def test_background_pull(app, client, monkeypatch):
    started = []

    class Thread:
        def __init__(self, target):
            self.target = target

        def start(self):
            started.append(self.target)

    monkeypatch.setattr(app_module.threading, "Thread", Thread)
    app.config["SCRAPER"] = None
    app.config["LOADER"] = None

    response = client.post("/pull-data")

    assert response.status_code == 202
    assert started == [app_module.run_pull_data]


@pytest.mark.buttons
def test_pull_error(app, client):
    app_module.pull_data_running = False
    app.config["SCRAPER"] = lambda: (_ for _ in ()).throw(
        RuntimeError("scrape failed")
    )
    app.config["LOADER"] = lambda rows: 0

    response = client.post("/pull-data")

    assert response.status_code == 500
    assert response.get_json()["error"] == "scrape failed"
