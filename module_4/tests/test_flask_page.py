"""Tests for the Flask application and Analysis page."""

import pytest
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

    assert response.status_code == 200
    assert b"Analysis" in response.data
    assert b"Pull Data" in response.data
    assert b"Update Analysis" in response.data
    assert b"Answer:" in response.data
    assert b'data-testid="pull-data-btn"' in response.data
    assert b'data-testid="update-analysis-btn"' in response.data
