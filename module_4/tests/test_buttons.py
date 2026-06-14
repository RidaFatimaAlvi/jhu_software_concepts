"""Tests for button endpoints and busy-state behavior."""

import pytest

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_busy_state():
    app_module.pull_data_running = False
    yield
    app_module.pull_data_running = False


@pytest.mark.buttons
def test_pull_data(client, app):
    rows = [{"program": "Computer Science"}]
    loaded_rows = []

    app.config["SCRAPER"] = lambda: rows
    app.config["LOADER"] = lambda scraped_rows: loaded_rows.extend(scraped_rows) or 1

    response = client.post("/pull-data")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True, "inserted": 1}
    assert loaded_rows == rows


@pytest.mark.buttons
def test_update_analysis_when_not_busy(client):
    response = client.post("/update-analysis")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


@pytest.mark.buttons
def test_update_analysis_when_busy(client):
    app_module.pull_data_running = True

    response = client.post("/update-analysis")

    assert response.status_code == 409
    assert response.get_json() == {"ok": False, "busy": True}


@pytest.mark.buttons
def test_pull_data_when_busy(client, app):
    calls = []
    app.config["SCRAPER"] = lambda: calls.append("scraper")
    app.config["LOADER"] = lambda rows: calls.append("loader")
    app_module.pull_data_running = True

    response = client.post("/pull-data")

    assert response.status_code == 409
    assert response.get_json() == {"ok": False, "busy": True}
    assert calls == []
