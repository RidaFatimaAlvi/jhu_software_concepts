"""Tests for PostgreSQL inserts, constraints, and queries."""

import os

import psycopg
import pytest

from src.load_data import create_schema, load_records
from src.query_data import ANALYSIS_KEYS, RECORD_KEYS, get_analysis, query_records


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql:///gradcafe_test",
)


def database_connection():
    return psycopg.connect(TEST_DATABASE_URL)


@pytest.fixture(autouse=True)
def empty_applicants_table():
    connection = database_connection()
    create_schema(connection)

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE applicants RESTART IDENTITY")

    connection.commit()
    connection.close()


@pytest.fixture
def sample_row():
    return {
        "program": "Computer Science, Johns Hopkins University",
        "comments": "Test record",
        "date_added": "Jun 14, 2026",
        "url": "https://www.thegradcafe.com/result/test-1",
        "status": "Accepted on Jun 1",
        "term": "Fall 2026",
        "US/International": "American",
        "GPA": "3.90",
        "GRE": "325",
        "GRE V": "160",
        "GRE AW": "4.5",
        "Degree": "Masters",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Johns Hopkins University",
    }


@pytest.mark.db
def test_insert_on_pull(app, client, sample_row):
    app.config["SCRAPER"] = lambda: [sample_row]
    app.config["LOADER"] = lambda rows: load_records(rows, database_connection)

    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM applicants")
            assert cursor.fetchone()[0] == 0

    response = client.post("/pull-data")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True, "inserted": 1}

    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT program, date_added, url, status, term,
                       us_or_international, degree
                FROM applicants
                """
            )
            row = cursor.fetchone()

    assert row is not None
    assert all(value is not None for value in row)


@pytest.mark.db
def test_duplicate_pull_does_not_duplicate_rows(app, client, sample_row):
    app.config["SCRAPER"] = lambda: [sample_row]
    app.config["LOADER"] = lambda rows: load_records(rows, database_connection)

    first_response = client.post("/pull-data")
    second_response = client.post("/pull-data")

    assert first_response.get_json()["inserted"] == 1
    assert second_response.get_json()["inserted"] == 0

    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM applicants")
            assert cursor.fetchone()[0] == 1


@pytest.mark.db
def test_query_records_returns_expected_dictionary(sample_row):
    load_records([sample_row], database_connection)

    records = query_records(database_connection)

    assert len(records) == 1
    assert isinstance(records[0], dict)
    assert tuple(records[0].keys()) == RECORD_KEYS


@pytest.mark.db
def test_get_analysis_returns_expected_keys(sample_row):
    load_records([sample_row], database_connection)

    analysis = get_analysis(database_connection)

    assert tuple(analysis.keys()) == ANALYSIS_KEYS
    assert analysis["q1"] == 1
    assert analysis["q2"] == 0
    assert analysis["q5"] == 100
