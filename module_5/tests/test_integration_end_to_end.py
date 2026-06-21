"""End-to-end tests for pull, update, database, and rendering."""

import os

import psycopg
import pytest

from src import app as app_module
from src.load_data import create_schema, load_records


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql:///gradcafe_test",
)


def database_connection():
    return psycopg.connect(TEST_DATABASE_URL)


@pytest.fixture(autouse=True)
def empty_test_database():
    connection = database_connection()
    create_schema(connection)

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE applicants RESTART IDENTITY")

    connection.commit()
    connection.close()
    app_module.pull_data_running = False

    yield

    app_module.pull_data_running = False


@pytest.fixture
def records():
    return [
        {
            "program": "Computer Science, Johns Hopkins University",
            "comments": "First test record",
            "date_added": "Jun 10, 2026",
            "url": "https://www.thegradcafe.com/result/integration-1",
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
        },
        {
            "program": "Statistics, Example University",
            "comments": "Second test record",
            "date_added": "Jun 11, 2026",
            "url": "https://www.thegradcafe.com/result/integration-2",
            "status": "Rejected on Jun 2",
            "term": "Fall 2026",
            "US/International": "International",
            "GPA": "3.70",
            "GRE": "315",
            "GRE V": "155",
            "GRE AW": "4.0",
            "Degree": "PhD",
            "llm-generated-program": "Statistics",
            "llm-generated-university": "Example University",
        },
    ]


def make_app(scraper):
    return app_module.create_app(
        {
            "TESTING": True,
            "DATABASE_URL": TEST_DATABASE_URL,
        },
        scraper=scraper,
        loader=lambda rows: load_records(rows, database_connection),
    )


@pytest.mark.integration
def test_pull_update_render_end_to_end(records):
    app = make_app(lambda: records)
    client = app.test_client()

    pull_response = client.post("/pull-data")

    assert pull_response.status_code == 200
    assert pull_response.get_json() == {"ok": True, "inserted": 2}

    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM applicants")
            assert cursor.fetchone()[0] == 2

    update_response = client.post("/update-analysis")

    assert update_response.status_code == 200
    assert update_response.get_json() == {"ok": True}

    page_response = client.get("/analysis")
    page_text = page_response.get_data(as_text=True)

    assert page_response.status_code == 200
    assert "Answer: Applicant count: 2" in page_text
    assert "50.00%" in page_text


@pytest.mark.integration
def test_overlapping_pulls_follow_uniqueness_policy(records):
    third_record = {
        **records[0],
        "program": "Mathematics, Sample University",
        "url": "https://www.thegradcafe.com/result/integration-3",
    }
    batches = [
        records,
        [records[1], third_record],
    ]
    app = make_app(lambda: batches.pop(0))
    client = app.test_client()

    first_response = client.post("/pull-data")
    second_response = client.post("/pull-data")

    assert first_response.get_json()["inserted"] == 2
    assert second_response.get_json()["inserted"] == 1

    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM applicants")
            assert cursor.fetchone()[0] == 3
