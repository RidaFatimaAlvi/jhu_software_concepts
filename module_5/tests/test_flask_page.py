"""Tests for the Flask application and Analysis page."""

import pytest
from bs4 import BeautifulSoup
from flask import Flask


@pytest.mark.web
def test_create_app(app):
    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True

    routes = {route.rule for route in app.url_map.iter_rules()}

    assert "/" in routes
    assert "/analysis" in routes
    assert "/pull-data" in routes
    assert "/update-analysis" in routes


@pytest.mark.web
def test_analysis_page(client):
    response = client.get("/analysis")
    page = BeautifulSoup(response.data, "html.parser")
    page_text = page.get_text(" ", strip=True)

    assert response.status_code == 200
    assert page.find("h1").get_text(strip=True) == "Analysis"
    assert "Answer:" in page_text

    pull_button = page.find("button", {"data-testid": "pull-data-btn"})
    update_button = page.find(
        "button",
        {"data-testid": "update-analysis-btn"},
    )

    assert pull_button.get_text(strip=True) == "Pull Data"
    assert update_button.get_text(strip=True) == "Update Analysis"
