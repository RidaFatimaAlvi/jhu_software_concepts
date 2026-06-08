import psycopg

connection = psycopg.connect(
    dbname="gradcafe_db"
)

with connection.cursor() as cur:

    # Question 1
    print("\nQuestion 1")
    print("How many entries applied for Fall 2026?")

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2026';
    """)

    print(cur.fetchone()[0])

    # Question 2
    print("\nQuestion 2")
    print("What percentage of entries are international students?")

    cur.execute("""
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE us_or_international NOT IN ('American', 'Other')
            ) / COUNT(*),
            2
        )
        FROM applicants;
    """)

    print(cur.fetchone()[0])

    # Question 3
    print("\nQuestion 3")
    print("Average GPA, GRE, GRE V, GRE AW")

    cur.execute("""
        SELECT
            ROUND(AVG(gpa)::numeric, 2),
            ROUND(AVG(gre)::numeric, 2),
            ROUND(AVG(gre_v)::numeric, 2),
            ROUND(AVG(gre_aw)::numeric, 2)
        FROM applicants;
    """)

    print(cur.fetchone())

    # Question 4
    print("\nQuestion 4")
    print("Average GPA of American students in Fall 2026")

    cur.execute("""
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE us_or_international = 'American'
        AND term = 'Fall 2026';
    """)

    print(cur.fetchone()[0])

    # Question 5
    print("\nQuestion 5")
    print("Percent of Fall 2026 entries that are acceptances")

    cur.execute("""
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE status ILIKE 'Accepted%'
            ) / COUNT(*),
            2
        )
        FROM applicants
        WHERE term = 'Fall 2026';
    """)

    print(cur.fetchone()[0])

    # Question 6
    print("\nQuestion 6")
    print("Average GPA of Fall 2026 acceptances")

    cur.execute("""
        SELECT ROUND(AVG(gpa)::numeric, 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND status ILIKE 'Accepted%';
    """)

    print(cur.fetchone()[0])

    # Question 7
    print("\nQuestion 7")
    print("How many entries are from applicants who applied to JHU for a Masters degree in Computer Science?")

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE degree = 'Masters'
        AND program ILIKE '%Computer Science%'
        AND (
            program ILIKE '%Johns Hopkins%'
            OR program ILIKE '%JHU%'
        );
    """)

    print(cur.fetchone()[0])

        # Question 8
    print("\nQuestion 8")
    print("2026 acceptances to Georgetown, MIT, Stanford, or Carnegie Mellon for a PhD in Computer Science using downloaded fields")

    cur.execute("""
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
    """)

    print(cur.fetchone()[0])

    # Question 9
    print("\nQuestion 9")
    print("Same question using LLM-generated fields")

    cur.execute("""
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
    """)

    print(cur.fetchone()[0])

    # Question 10
    print("\nQuestion 10")
    print("Which top 10 universities receive the most applications?")

    cur.execute("""
        SELECT
            llm_generated_university,
            COUNT(*) AS total_applications
        FROM applicants
        WHERE llm_generated_university IS NOT NULL
        GROUP BY llm_generated_university
        ORDER BY total_applications DESC
        LIMIT 10;
    """)

    print(cur.fetchall())

    # Question 11
    print("\nQuestion 11")
    print("Which degree type has the highest average GPA?")

    cur.execute("""
        SELECT
            degree,
            ROUND(AVG(gpa)::numeric, 2) AS average_gpa
        FROM applicants
        WHERE gpa IS NOT NULL
        GROUP BY degree
        ORDER BY average_gpa DESC
        LIMIT 1;
    """)

    print(cur.fetchall())

connection.close()