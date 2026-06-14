"""PostgreSQL queries used by the Grad Cafe analysis page."""

import os

import psycopg
from psycopg.rows import dict_row

ANALYSIS_KEYS = tuple(f"q{number}" for number in range(1, 12))
RECORD_KEYS = (
    "p_id",
    "program",
    "comments",
    "date_added",
    "url",
    "status",
    "term",
    "us_or_international",
    "gpa",
    "gre",
    "gre_v",
    "gre_aw",
    "degree",
    "llm_generated_program",
    "llm_generated_university",
)


def get_connection(database_url=None):
    """Return a PostgreSQL connection for queries."""
    url = database_url or os.getenv("DATABASE_URL")
    if url:
        return psycopg.connect(url)
    return psycopg.connect(dbname="gradcafe_db")


def query_records(connection_factory=get_connection):
    """Return applicant rows as dictionaries with Module 3 schema keys."""
    connection = connection_factory()
    try:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT p_id, program, comments, date_added, url, status, term,
                       us_or_international, gpa, gre, gre_v, gre_aw, degree,
                       llm_generated_program, llm_generated_university
                FROM applicants
                ORDER BY p_id;
                """
            )
            return cursor.fetchall()
    finally:
        connection.close()


def get_analysis(connection_factory=get_connection):
    """Return the eleven Module 3 analysis answers."""
    connection = connection_factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';"
            )
            q1 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COALESCE(ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE us_or_international NOT IN ('American', 'Other')
                    ) / NULLIF(COUNT(*), 0), 2
                ), 0) FROM applicants;
                """
            )
            q2 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT ROUND(AVG(gpa)::numeric, 2),
                       ROUND(AVG(gre)::numeric, 2),
                       ROUND(AVG(gre_v)::numeric, 2),
                       ROUND(AVG(gre_aw)::numeric, 2)
                FROM applicants;
                """
            )
            q3 = cursor.fetchone()

            cursor.execute(
                """
                SELECT ROUND(AVG(gpa)::numeric, 2) FROM applicants
                WHERE us_or_international = 'American'
                  AND term = 'Fall 2026';
                """
            )
            q4 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COALESCE(ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE status ILIKE 'Accepted%'
                    ) / NULLIF(COUNT(*), 0), 2
                ), 0) FROM applicants WHERE term = 'Fall 2026';
                """
            )
            q5 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT ROUND(AVG(gpa)::numeric, 2) FROM applicants
                WHERE term = 'Fall 2026' AND status ILIKE 'Accepted%';
                """
            )
            q6 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM applicants
                WHERE degree = 'Masters'
                  AND program ILIKE '%Computer Science%'
                  AND (program ILIKE '%Johns Hopkins%'
                       OR program ILIKE '%JHU%');
                """
            )
            q7 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM applicants
                WHERE date_added BETWEEN '2026-01-01' AND '2026-12-31'
                  AND status ILIKE 'Accepted%' AND degree = 'PhD'
                  AND (program ILIKE '%Computer%Science%'
                       OR program ILIKE '%ComputerScience%'
                       OR program ILIKE '%CS%')
                  AND (program ILIKE '%Georgetown%' OR program ILIKE '%MIT%'
                       OR program ILIKE '%Massachusetts Institute%'
                       OR program ILIKE '%Stanford%'
                       OR program ILIKE '%Carnegie Mellon%'
                       OR program ILIKE '%CMU%');
                """
            )
            q8 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM applicants
                WHERE date_added BETWEEN '2026-01-01' AND '2026-12-31'
                  AND status ILIKE 'Accepted%' AND degree = 'PhD'
                  AND (llm_generated_program ILIKE '%Computer%Science%'
                       OR llm_generated_program ILIKE '%ComputerScience%'
                       OR llm_generated_program ILIKE '%CS%')
                  AND (llm_generated_university ILIKE '%Georgetown%'
                       OR llm_generated_university ILIKE '%MIT%'
                       OR llm_generated_university
                          ILIKE '%Massachusetts Institute%'
                       OR llm_generated_university ILIKE '%Stanford%'
                       OR llm_generated_university ILIKE '%Carnegie Mellon%'
                       OR llm_generated_university ILIKE '%CMU%');
                """
            )
            q9 = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT llm_generated_university, COUNT(*) AS total_applications
                FROM applicants
                WHERE llm_generated_university IS NOT NULL
                GROUP BY llm_generated_university
                ORDER BY total_applications DESC LIMIT 10;
                """
            )
            q10 = cursor.fetchall()

            cursor.execute(
                """
                SELECT degree, ROUND(AVG(gpa)::numeric, 2) AS average_gpa
                FROM applicants WHERE gpa IS NOT NULL
                GROUP BY degree ORDER BY average_gpa DESC LIMIT 1;
                """
            )
            q11 = cursor.fetchone() or ("No data", None)

            return dict(zip(ANALYSIS_KEYS, (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11)))
    finally:
        connection.close()


if __name__ == "__main__":  # pragma: no cover - command-line helper
    print(get_analysis())
