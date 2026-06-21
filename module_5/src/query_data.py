"""PostgreSQL queries used by the Grad Cafe analysis page."""

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from src import db_config
from src.load_data import REQUIRED_INPUT_FIELDS

MAX_QUERY_LIMIT = 100
DEFAULT_QUERY_LIMIT = 100
DEFAULT_TOP_LIMIT = 10
APPLICANTS_TABLE = "applicants"
ANALYSIS_KEYS = tuple(f"q{number}" for number in range(1, 12))
RECORD_KEYS = (
    "p_id",
    REQUIRED_INPUT_FIELDS[0],
    "comments",
    *REQUIRED_INPUT_FIELDS[1:6],
    "gpa",
    "gre",
    "gre_v",
    "gre_aw",
    REQUIRED_INPUT_FIELDS[6],
    "llm_generated_program",
    "llm_generated_university",
)


def clamp_limit(limit, minimum=1, maximum=MAX_QUERY_LIMIT):
    """Clamp database row limits to the allowed range."""
    return max(minimum, min(int(limit), maximum))


def get_connection(database_url=None):
    """Return a PostgreSQL connection for queries."""
    url = database_url or db_config.database_url()
    if url:
        return psycopg.connect(url)
    return psycopg.connect(**db_config.connection_kwargs())


def query_records(connection_factory=get_connection, limit=DEFAULT_QUERY_LIMIT):
    """Return applicant rows as dictionaries with Module 3 schema keys."""
    connection = connection_factory()
    try:
        with connection.cursor(row_factory=dict_row) as cursor:
            statement = sql.SQL(
                """
                SELECT {columns}
                FROM {table}
                ORDER BY {id_column}
                LIMIT %s;
                """
            ).format(
                columns=sql.SQL(", ").join(
                    sql.Identifier(column) for column in RECORD_KEYS
                ),
                table=sql.Identifier(APPLICANTS_TABLE),
                id_column=sql.Identifier("p_id"),
            )
            params = [clamp_limit(limit)]
            cursor.execute(statement, params)
            return cursor.fetchall()
    finally:
        connection.close()


def get_analysis(  # pylint: disable=too-many-locals,too-many-statements
    connection_factory=get_connection,
    limit=DEFAULT_TOP_LIMIT,
):
    """Return the eleven Module 3 analysis answers."""
    connection = connection_factory()
    single_row_limit = clamp_limit(1)
    top_limit = clamp_limit(limit)
    try:
        with connection.cursor() as cursor:
            statement = sql.SQL(
                """
                SELECT COUNT(*)
                FROM {table}
                WHERE {term_column} = %s
                LIMIT %s;
                """
            ).format(
                table=sql.Identifier(APPLICANTS_TABLE),
                term_column=sql.Identifier("term"),
            )
            params = ["Fall 2026", single_row_limit]
            cursor.execute(statement, params)
            q1 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT COALESCE(ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE {student_type_column} NOT IN (%s, %s)
                    ) / NULLIF(COUNT(*), 0), 2
                ), 0)
                FROM {table}
                LIMIT %s;
                """
            ).format(
                student_type_column=sql.Identifier("us_or_international"),
                table=sql.Identifier(APPLICANTS_TABLE),
            )
            params = ["American", "Other", single_row_limit]
            cursor.execute(statement, params)
            q2 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT ROUND(AVG({gpa})::numeric, 2),
                       ROUND(AVG({gre})::numeric, 2),
                       ROUND(AVG({gre_v})::numeric, 2),
                       ROUND(AVG({gre_aw})::numeric, 2)
                FROM {table}
                LIMIT %s;
                """
            ).format(
                gpa=sql.Identifier("gpa"),
                gre=sql.Identifier("gre"),
                gre_v=sql.Identifier("gre_v"),
                gre_aw=sql.Identifier("gre_aw"),
                table=sql.Identifier(APPLICANTS_TABLE),
            )
            params = [single_row_limit]
            cursor.execute(statement, params)
            q3 = cursor.fetchone()

            statement = sql.SQL(
                """
                SELECT ROUND(AVG({gpa})::numeric, 2)
                FROM {table}
                WHERE {student_type_column} = %s
                  AND {term_column} = %s
                LIMIT %s;
                """
            ).format(
                gpa=sql.Identifier("gpa"),
                table=sql.Identifier(APPLICANTS_TABLE),
                student_type_column=sql.Identifier("us_or_international"),
                term_column=sql.Identifier("term"),
            )
            params = ["American", "Fall 2026", single_row_limit]
            cursor.execute(statement, params)
            q4 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT COALESCE(ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE {status_column} ILIKE %s
                    ) / NULLIF(COUNT(*), 0), 2
                ), 0)
                FROM {table}
                WHERE {term_column} = %s
                LIMIT %s;
                """
            ).format(
                status_column=sql.Identifier("status"),
                table=sql.Identifier(APPLICANTS_TABLE),
                term_column=sql.Identifier("term"),
            )
            params = ["Accepted%", "Fall 2026", single_row_limit]
            cursor.execute(statement, params)
            q5 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT ROUND(AVG({gpa})::numeric, 2)
                FROM {table}
                WHERE {term_column} = %s
                  AND {status_column} ILIKE %s
                LIMIT %s;
                """
            ).format(
                gpa=sql.Identifier("gpa"),
                table=sql.Identifier(APPLICANTS_TABLE),
                term_column=sql.Identifier("term"),
                status_column=sql.Identifier("status"),
            )
            params = ["Fall 2026", "Accepted%", single_row_limit]
            cursor.execute(statement, params)
            q6 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT COUNT(*)
                FROM {table}
                WHERE {degree_column} = %s
                  AND {program_column} ILIKE %s
                  AND ({program_column} ILIKE %s
                       OR {program_column} ILIKE %s)
                LIMIT %s;
                """
            ).format(
                table=sql.Identifier(APPLICANTS_TABLE),
                degree_column=sql.Identifier("degree"),
                program_column=sql.Identifier("program"),
            )
            params = [
                "Masters",
                "%Computer Science%",
                "%Johns Hopkins%",
                "%JHU%",
                single_row_limit,
            ]
            cursor.execute(statement, params)
            q7 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT COUNT(*)
                FROM {table}
                WHERE {date_column} BETWEEN %s AND %s
                  AND {status_column} ILIKE %s
                  AND {degree_column} = %s
                  AND ({program_column} ILIKE %s
                       OR {program_column} ILIKE %s
                       OR {program_column} ILIKE %s)
                  AND ({program_column} ILIKE %s
                       OR {program_column} ILIKE %s
                       OR {program_column} ILIKE %s
                       OR {program_column} ILIKE %s
                       OR {program_column} ILIKE %s
                       OR {program_column} ILIKE %s)
                LIMIT %s;
                """
            ).format(
                table=sql.Identifier(APPLICANTS_TABLE),
                date_column=sql.Identifier("date_added"),
                status_column=sql.Identifier("status"),
                degree_column=sql.Identifier("degree"),
                program_column=sql.Identifier("program"),
            )
            params = [
                "2026-01-01",
                "2026-12-31",
                "Accepted%",
                "PhD",
                "%Computer%Science%",
                "%ComputerScience%",
                "%CS%",
                "%Georgetown%",
                "%MIT%",
                "%Massachusetts Institute%",
                "%Stanford%",
                "%Carnegie Mellon%",
                "%CMU%",
                single_row_limit,
            ]
            cursor.execute(statement, params)
            q8 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT COUNT(*)
                FROM {table}
                WHERE {date_column} BETWEEN %s AND %s
                  AND {status_column} ILIKE %s
                  AND {degree_column} = %s
                  AND ({llm_program_column} ILIKE %s
                       OR {llm_program_column} ILIKE %s
                       OR {llm_program_column} ILIKE %s)
                  AND ({llm_university_column} ILIKE %s
                       OR {llm_university_column} ILIKE %s
                       OR {llm_university_column} ILIKE %s
                       OR {llm_university_column} ILIKE %s
                       OR {llm_university_column} ILIKE %s
                       OR {llm_university_column} ILIKE %s)
                LIMIT %s;
                """
            ).format(
                table=sql.Identifier(APPLICANTS_TABLE),
                date_column=sql.Identifier("date_added"),
                status_column=sql.Identifier("status"),
                degree_column=sql.Identifier("degree"),
                llm_program_column=sql.Identifier("llm_generated_program"),
                llm_university_column=sql.Identifier("llm_generated_university"),
            )
            params = [
                "2026-01-01",
                "2026-12-31",
                "Accepted%",
                "PhD",
                "%Computer%Science%",
                "%ComputerScience%",
                "%CS%",
                "%Georgetown%",
                "%MIT%",
                "%Massachusetts Institute%",
                "%Stanford%",
                "%Carnegie Mellon%",
                "%CMU%",
                single_row_limit,
            ]
            cursor.execute(statement, params)
            q9 = cursor.fetchone()[0]

            statement = sql.SQL(
                """
                SELECT {llm_university_column}, COUNT(*) AS {total_alias}
                FROM {table}
                WHERE {llm_university_column} IS NOT NULL
                GROUP BY {llm_university_column}
                ORDER BY {total_alias} DESC
                LIMIT %s;
                """
            ).format(
                llm_university_column=sql.Identifier("llm_generated_university"),
                total_alias=sql.Identifier("total_applications"),
                table=sql.Identifier(APPLICANTS_TABLE),
            )
            params = [top_limit]
            cursor.execute(statement, params)
            q10 = cursor.fetchall()

            statement = sql.SQL(
                """
                SELECT {degree_column},
                       ROUND(AVG({gpa})::numeric, 2) AS {average_alias}
                FROM {table}
                WHERE {gpa} IS NOT NULL
                GROUP BY {degree_column}
                ORDER BY {average_alias} DESC
                LIMIT %s;
                """
            ).format(
                degree_column=sql.Identifier("degree"),
                gpa=sql.Identifier("gpa"),
                average_alias=sql.Identifier("average_gpa"),
                table=sql.Identifier(APPLICANTS_TABLE),
            )
            params = [single_row_limit]
            cursor.execute(statement, params)
            q11 = cursor.fetchone() or ("No data", None)

            answers = (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11)
            return dict(zip(ANALYSIS_KEYS, answers))
    finally:
        connection.close()


if __name__ == "__main__":  # pragma: no cover - command-line helper
    print(get_analysis())
