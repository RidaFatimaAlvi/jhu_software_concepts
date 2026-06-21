"""Flask application for the Grad Cafe analysis page."""

import os
import subprocess
import threading

import psycopg
from flask import Flask, jsonify, render_template

from src import db_config

app = Flask(__name__)
pull_data_running = False  # pylint: disable=invalid-name


def create_app(config=None, *, scraper=None, loader=None):
    """Configure and return the Flask application.

    Tests may inject a scraper and loader so no live scrape is required.
    """
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "gradcafe-development"),
        DATABASE_URL=db_config.database_url(),
        SCRAPER=scraper,
        LOADER=loader,
    )
    if config:
        app.config.update(config)
    return app


def get_db_connection():
    """Connect to PostgreSQL using environment-provided credentials."""
    database_url = app.config.get("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)
    return psycopg.connect(**db_config.connection_kwargs())


def run_pull_data():
    """Run the existing Module 3 pull script in the background."""
    global pull_data_running  # pylint: disable=global-statement
    try:
        subprocess.run(["python", "pull_data.py"], check=True)
    finally:
        pull_data_running = False


@app.route("/pull-data", methods=["POST"])
def pull_data():
    """Start a data pull or reject the request while another pull is active."""
    global pull_data_running  # pylint: disable=global-statement

    if pull_data_running:
        return jsonify(ok=False, busy=True), 409

    pull_data_running = True
    try:
        scraper = app.config.get("SCRAPER")
        loader = app.config.get("LOADER")
        if scraper is not None and loader is not None:
            rows = scraper()
            inserted = loader(rows)
            return jsonify(ok=True, inserted=inserted), 200

        thread = threading.Thread(target=run_pull_data)
        thread.start()
        return jsonify(ok=True), 202
    except RuntimeError as error:
        pull_data_running = False
        return jsonify(ok=False, error=str(error)), 500
    finally:
        if app.config.get("SCRAPER") is not None:
            pull_data_running = False


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    """Return success when analysis can be refreshed."""
    if pull_data_running:
        return jsonify(ok=False, busy=True), 409
    return jsonify(ok=True), 200


@app.route("/")
@app.route("/analysis")
def index():
    """Query PostgreSQL and render the original Module 3 analysis page."""
    from src.query_data import get_analysis  # pylint: disable=import-outside-toplevel

    answers = get_analysis(get_db_connection)

    return render_template(
        "index.html",
        **answers,
    )


create_app()


if __name__ == "__main__":  # pragma: no cover - development entry point
    app.run(host="0.0.0.0", port=8080)
