# Module 5: Grad Cafe Assurance and Security

This module contains the Flask, ETL, PostgreSQL, Pytest, CI, and Sphinx work
for the Grad Cafe analytics application.

Repository SSH URL:
`git@github.com:RidaFatimaAlvi/jhu_software_concepts.git`

## Project Structure

```text
module_5/
├── src/                 # Flask, scraping, cleaning, loading, and queries
├── tests/               # Pytest suite
├── docs/                # Sphinx source and generated HTML
├── pytest.ini
├── requirements.txt
└── coverage_summary.txt
```

## Setup

From the repository root:

```bash
python3 -m venv module_5/.venv
source module_5/.venv/bin/activate
python -m pip install -r module_5/requirements.txt
```

## Fresh Install

Use one of the following install paths from the repository root.

With `pip`:

```bash
python3 -m venv module_5/.venv
source module_5/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r module_5/requirements.txt
cd module_5
python -m pip install -e .
```

With `uv`:

```bash
python3 -m venv module_5/.venv
source module_5/.venv/bin/activate
python -m pip install uv
uv pip sync module_5/requirements.txt
cd module_5
uv pip install -e .
```

`uv pip sync` makes the virtual environment match `requirements.txt`, which
helps keep local development and CI reproducible.

Create the PostgreSQL databases used by the application and tests:

```bash
createdb gradcafe_db
createdb gradcafe_test
```

Set the application database URL:

```bash
export TEST_DATABASE_URL="postgresql:///gradcafe_test"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="gradcafe_db"
export DB_USER="gradcafe_app"
export DB_PASSWORD="<set-this-locally>"
```

`DATABASE_URL` is still supported as an override for local testing or CI, but
production-style runs should use the separate `DB_*` environment variables so
database credentials are not hard-coded in application code.

## Run the Application

```bash
python module_5/src/app.py
```

Open <http://127.0.0.1:8080/analysis>.

## Run the Tests

From the repository root:

```bash
python -m pytest module_5 \
  -m "web or buttons or analysis or db or integration"
```

The suite requires 100% coverage through `module_5/pytest.ini`.

## Run Pylint

From the repository root, run Pylint only on the Module 5 application source:

```bash
module_5/.venv/bin/python -m pylint module_5/src/*.py
```

The required final output is:

```text
Your code has been rated at 10.00/10
```

Evidence of the passing lint score is saved in `module_5/pylint_score.txt`.

## SQL Injection Defenses

Database code in `module_5/src/load_data.py` and `module_5/src/query_data.py`
uses psycopg SQL composition instead of raw string-built SQL. SQL statements are
constructed with `sql.SQL(...)`, table and column names use
`sql.Identifier(...)`, and values are passed separately through
`cursor.execute(statement, params)`.

Read queries include an explicit `LIMIT`. User-controlled limits are passed
through `clamp_limit(...)`, which enforces the allowed range of `1` to `100`.

## Dependency Graph

The dependency graph is saved as `module_5/dependency.svg` and was generated
with pydeps and Graphviz. The graph shows `src/app.py` as the Flask entry point
because it creates the web app, defines routes, and renders the analysis page.
It depends on Flask modules for routing, JSON responses, and template rendering.
The app also depends on `psycopg` because the page opens PostgreSQL connections
for analysis data. The project modules `src.query_data` and `src.load_data`
appear because they handle database reads, SQL composition, schema setup, and
record inserts. The `src.db_config` module appears because connection settings
are read from environment variables instead of being hard-coded.

## Packaging

This module includes `setup.py` so the project can be installed consistently in
local development, tests, and CI. Packaging matters because it makes imports
behave the same way across environments instead of depending on the current
working directory. An editable install keeps the source files live while making
the package importable:

```bash
python -m pip install -e .
```

This reduces "works on my machine" path problems and gives tools such as `uv`
or `pip` a standard place to read project dependency metadata.

## Snyk Code Scan

Snyk Code static analysis was run against `module_5`. The scan reported `112`
open issues total: `1` high severity issue, `36` medium severity issues, and
`75` low severity issues. The findings shown in the saved output are primarily
inside the local `.venv/lib/python3.12/site-packages/` directory, meaning they
come from installed third-party packages and development tools rather than the
application source files in `module_5/src`. The most common finding types were
path traversal, command injection, insecure XML parser warnings, weak hash
algorithm warnings, and archive extraction warnings. Evidence of the scan is
saved as `module_5/snyk-code-results.png`.

## Build the Documentation

```bash
cd module_5/docs
make html
```

Open `module_5/docs/build/html/index.html` after the build finishes.

Published documentation:
<https://rida-jhu-software-concepts.readthedocs.io/en/latest/>

## Limitations

- The scraper depends on the current Grad Cafe page structure and a local
  Chrome/Selenium installation. Website changes may require updates to the
  selectors.
- Live scraping can be slow because each page includes a delay. Tests therefore
  use fake scraper and browser objects instead of accessing the internet.
- The busy state is stored in one in-memory Boolean. It works for this
  single-process application but would not coordinate multiple server
  processes.
- The background pull command depends on the application's working directory
  and available `python` executable.
- Cleaning is provided as a separate ETL step. The pull helper currently passes
  scraper output directly to the loader, so production input must already
  contain the required database fields.
- Duplicate detection uses the record URL as the uniqueness key. Records with
  different URLs but otherwise identical data are not treated as duplicates.
- The Analysis page requires a running PostgreSQL database and does not
  currently provide a user-friendly page when the database is unavailable.
- Grad Cafe records are self-reported and may contain missing or inconsistent
  values, so the displayed analysis should not be treated as verified
  admissions data.

## Continuous Integration

The workflow in `.github/workflows/ci.yml` runs Pylint, starts PostgreSQL and
runs the marked Pytest suite with coverage, regenerates `dependency.svg`, and
prints Snyk dependency-scan output. Evidence of a successful run is stored in
`module_5/actions_success.png`.

## Module 5 Report

The final PDF report is saved as `module_5/module_5_report.pdf`. It explains
the pip and uv install paths, dependency graph summary, SQL injection defenses,
least-privilege database configuration, and required SQL safety behaviors.
