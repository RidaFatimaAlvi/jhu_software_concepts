# Module 4: Grad Cafe Testing and Documentation

This module contains the Flask, ETL, PostgreSQL, Pytest, CI, and Sphinx work
for the Grad Cafe analytics application.

## Project Structure

```text
module_4/
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
python3 -m venv venv
source venv/bin/activate
python -m pip install -r module_4/requirements.txt
```

Create the PostgreSQL databases used by the application and tests:

```bash
createdb gradcafe_db
createdb gradcafe_test
```

Set the application database URL:

```bash
export DATABASE_URL="postgresql:///gradcafe_db"
export TEST_DATABASE_URL="postgresql:///gradcafe_test"
```

## Run the Application

```bash
python module_4/src/app.py
```

Open <http://127.0.0.1:8080/analysis>.

## Run the Tests

From the repository root:

```bash
python -m pytest module_4 \
  -m "web or buttons or analysis or db or integration"
```

The suite requires 100% coverage through `module_4/pytest.ini`.

## Build the Documentation

```bash
cd module_4/docs
make html
```

Open `module_4/docs/build/html/index.html` after the build finishes.

Published documentation:
<https://jhu-software-concepts.readthedocs.io/en/latest/>

If Read the Docs assigns a different project slug during import, replace this
URL with the URL shown on the successful Read the Docs build page.

## Continuous Integration

The workflow in `.github/workflows/tests.yml` starts PostgreSQL and runs the
marked Pytest suite with coverage. Evidence of a successful run is stored in
`module_4/actions_success.png`.
