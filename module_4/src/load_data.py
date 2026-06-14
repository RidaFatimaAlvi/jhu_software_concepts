"""PostgreSQL schema and loading functions for Grad Cafe records."""

import json
import os
from datetime import date, datetime
from pathlib import Path

import psycopg

REQUIRED_FIELDS = (
    "program",
    "date_added",
    "url",
    "status",
    "term",
    "us_or_international",
    "degree",
)


def clean_float(value):
    """Convert a scraped numeric value to ``float`` or ``None``."""
    if value is None or value == "":
        return None
    value = str(value).strip().replace(",", "")
    if value.endswith("."):
        value = value[:-1]
    try:
        return float(value)
    except ValueError:
        return None


def clean_date(value):
    """Convert a Grad Cafe date string to a date."""
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%b %d, %Y").date()


def normalize_record(record):
    """Map scraper/Module 3 field names to the required database schema."""
    normalized = {
        "program": record.get("program"),
        "comments": record.get("comments"),
        "date_added": clean_date(record.get("date_added")),
        "url": record.get("url"),
        "status": record.get("status") or record.get("applicant_status"),
        "term": record.get("term") or record.get("start_term"),
        "us_or_international": (
            record.get("us_or_international")
            or record.get("US/International")
            or record.get("student_type")
        ),
        "gpa": clean_float(record.get("gpa", record.get("GPA"))),
        "gre": clean_float(record.get("gre", record.get("GRE"))),
        "gre_v": clean_float(record.get("gre_v", record.get("GRE V"))),
        "gre_aw": clean_float(record.get("gre_aw", record.get("GRE AW"))),
        "degree": record.get("degree") or record.get("Degree"),
        "llm_generated_program": (
            record.get("llm_generated_program")
            or record.get("llm-generated-program")
        ),
        "llm_generated_university": (
            record.get("llm_generated_university")
            or record.get("llm-generated-university")
        ),
    }
    missing = [field for field in REQUIRED_FIELDS if not normalized[field]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return normalized


def get_connection(database_url=None):
    """Return a PostgreSQL connection for loading data."""
    url = database_url or os.getenv("DATABASE_URL")
    if url:
        return psycopg.connect(url)
    return psycopg.connect(dbname="gradcafe_db")


def create_schema(connection):
    """Create the Module 3 applicants table and uniqueness constraint."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS applicants (
                p_id BIGSERIAL PRIMARY KEY,
                program TEXT NOT NULL,
                comments TEXT,
                date_added DATE NOT NULL,
                url TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                term TEXT NOT NULL,
                us_or_international TEXT NOT NULL,
                gpa FLOAT,
                gre FLOAT,
                gre_v FLOAT,
                gre_aw FLOAT,
                degree TEXT NOT NULL,
                llm_generated_program TEXT,
                llm_generated_university TEXT
            );
            """
        )
    connection.commit()


def load_records(records, connection_factory=get_connection):
    """Insert records transactionally and ignore duplicate URLs."""
    connection = connection_factory()
    inserted = 0
    try:
        create_schema(connection)
        with connection.cursor() as cursor:
            for record in records:
                row = normalize_record(record)
                cursor.execute(
                    """
                    INSERT INTO applicants (
                        program, comments, date_added, url, status, term,
                        us_or_international, gpa, gre, gre_v, gre_aw, degree,
                        llm_generated_program, llm_generated_university
                    ) VALUES (
                        %(program)s, %(comments)s, %(date_added)s, %(url)s,
                        %(status)s, %(term)s, %(us_or_international)s,
                        %(gpa)s, %(gre)s, %(gre_v)s, %(gre_aw)s, %(degree)s,
                        %(llm_generated_program)s,
                        %(llm_generated_university)s
                    )
                    ON CONFLICT (url) DO NOTHING
                    """,
                    row,
                )
                inserted += cursor.rowcount
        connection.commit()
        return inserted
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def load_json_file(path, connection_factory=get_connection):
    """Load records from a JSON array file."""
    with Path(path).open(encoding="utf-8") as file:
        return load_records(json.load(file), connection_factory)


if __name__ == "__main__":  # pragma: no cover - command-line helper
    source = Path(__file__).resolve().parents[1] / "llm_extend_applicant_data_array.json"
    print(f"Loaded {load_json_file(source)} new records into applicants table.")
