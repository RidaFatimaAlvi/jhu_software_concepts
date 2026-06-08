import psycopg
import json
from datetime import datetime


def clean_float(value):
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
    if value == "":
        return None
    return datetime.strptime(value, "%b %d, %Y").date()


connection = psycopg.connect(
    dbname="gradcafe_db"
)

with connection.cursor() as cur:

    cur.execute("""
        DROP TABLE IF EXISTS applicants;

        CREATE TABLE applicants (
            p_id INTEGER PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
    """)

    print("Table created.")

    with open("llm_extend_applicant_data_array.json", "r") as file:
        applicants = json.load(file)

    for index, applicant in enumerate(applicants, start=1):
        cur.execute("""
            INSERT INTO applicants VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            );
        """, (
            index,
            applicant.get("program"),
            applicant.get("comments"),
            clean_date(applicant.get("date_added")),
            applicant.get("url"),
            applicant.get("status"),
            applicant.get("term"),
            applicant.get("US/International"),
            clean_float(applicant.get("GPA")),
            clean_float(applicant.get("GRE")),
            clean_float(applicant.get("GRE V")),
            clean_float(applicant.get("GRE AW")),
            applicant.get("Degree"),
            applicant.get("llm-generated-program"),
            applicant.get("llm-generated-university")
        ))

connection.commit()
connection.close()

print(f"Loaded {len(applicants)} records into applicants table.")