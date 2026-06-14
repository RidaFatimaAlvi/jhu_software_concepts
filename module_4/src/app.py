"""Flask application for the Grad Cafe analysis page."""

import os
import subprocess
import threading

import psycopg
from flask import Flask, jsonify, render_template

app = Flask(__name__)
pull_data_running = False


def create_app(config=None, *, scraper=None, loader=None):
    """Configure and return the Flask application.

    Tests may inject a scraper and loader so no live scrape is required.
    """
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "gradcafe-development"),
        DATABASE_URL=os.getenv("DATABASE_URL"),
        SCRAPER=scraper,
        LOADER=loader,
    )
    if config:
        app.config.update(config)
    return app


def get_db_connection():
    """Connect to PostgreSQL using ``DATABASE_URL`` when it is configured."""
    database_url = app.config.get("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)
    return psycopg.connect(dbname="gradcafe_db")


def run_pull_data():
    """Run the existing Module 3 pull script in the background."""
    global pull_data_running
    try:
        subprocess.run(["python", "pull_data.py"], check=True)
    finally:
        pull_data_running = False


@app.route("/pull-data", methods=["POST"])
def pull_data():
    """Start a data pull or reject the request while another pull is active."""
    global pull_data_running

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
    except Exception as error:
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
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2026';
        """
    )
    q1 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE us_or_international NOT IN ('American', 'Other')
            ) / COUNT(*),
            2
        )
        FROM applicants;
        """
    )
    q2 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT
            ROUND(AVG(gpa)::numeric, 2),
            ROUND(AVG(gre)::numeric, 2),
            ROUND(AVG(gre_v)::numeric, 2),
            ROUND(AVG(gre_aw)::numeric, 2)
        FROM applicants;
        """
    )
    q3 = cur.fetchone()

    cur.execute(
        """
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE us_or_international = 'American'
        AND term = 'Fall 2026';
        """
    )
    q4 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE status ILIKE 'Accepted%'
            ) / COUNT(*),
            2
        )
        FROM applicants
        WHERE term = 'Fall 2026';
        """
    )
    q5 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND status ILIKE 'Accepted%';
        """
    )
    q6 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE degree = 'Masters'
        AND program ILIKE '%Computer Science%'
        AND (
            program ILIKE '%Johns Hopkins%'
            OR program ILIKE '%JHU%'
        );
        """
    )
    q7 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE date_added BETWEEN '2026-01-01' AND '2026-12-31'
        AND status ILIKE 'Accepted%'
        AND degree = 'PhD'
        AND (
            program ILIKE '%Computer%Science%'
            OR program ILIKE '%ComputerScience%'
            OR program ILIKE '%CS%'
        )
        AND (
            program ILIKE '%Georgetown%'
            OR program ILIKE '%MIT%'
            OR program ILIKE '%Massachusetts Institute%'
            OR program ILIKE '%Stanford%'
            OR program ILIKE '%Carnegie Mellon%'
            OR program ILIKE '%CMU%'
        );
        """
    )
    q8 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE date_added BETWEEN '2026-01-01' AND '2026-12-31'
        AND status ILIKE 'Accepted%'
        AND degree = 'PhD'
        AND (
            llm_generated_program ILIKE '%Computer%Science%'
            OR llm_generated_program ILIKE '%ComputerScience%'
            OR llm_generated_program ILIKE '%CS%'
        )
        AND (
            llm_generated_university ILIKE '%Georgetown%'
            OR llm_generated_university ILIKE '%MIT%'
            OR llm_generated_university ILIKE '%Massachusetts Institute%'
            OR llm_generated_university ILIKE '%Stanford%'
            OR llm_generated_university ILIKE '%Carnegie Mellon%'
            OR llm_generated_university ILIKE '%CMU%'
        );
        """
    )
    q9 = cur.fetchone()[0]

    cur.execute(
        """
        SELECT
            llm_generated_university,
            COUNT(*) AS total_applications
        FROM applicants
        WHERE llm_generated_university IS NOT NULL
        GROUP BY llm_generated_university
        ORDER BY total_applications DESC
        LIMIT 10;
        """
    )
    q10 = cur.fetchall()

    cur.execute(
        """
        SELECT
            degree,
            ROUND(AVG(gpa)::numeric, 2) AS average_gpa
        FROM applicants
        WHERE gpa IS NOT NULL
        GROUP BY degree
        ORDER BY average_gpa DESC
        LIMIT 1;
        """
    )
    q11 = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        q1=q1,
        q2=q2,
        q3=q3,
        q4=q4,
        q5=q5,
        q6=q6,
        q7=q7,
        q8=q8,
        q9=q9,
        q10=q10,
        q11=q11,
    )


create_app()


if __name__ == "__main__":  # pragma: no cover - development entry point
    app.run(host="0.0.0.0", port=8080)
