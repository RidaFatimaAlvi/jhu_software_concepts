Operational Notes
=================

Busy-State Policy
-----------------

Only one pull may run at a time. While ``pull_data_running`` is true, both
``POST /pull-data`` and ``POST /update-analysis`` return HTTP 409 with
``{"busy": true}``.

Idempotency Policy
------------------

The ``applicants.url`` column is unique. ``load_records`` uses
``ON CONFLICT (url) DO NOTHING``, so pulling the same record again does not
create a duplicate.

Troubleshooting
---------------

``pytest: command not found``
   Activate the virtual environment or run tests with
   ``venv/bin/python -m pytest`` from the repository root.

Coverage reports zero imported modules
   Run Pytest from the repository root, because ``pytest.ini`` measures
   ``module_4/src`` relative to that directory.

PostgreSQL connection failure
   Confirm PostgreSQL is running, both databases exist, and ``DATABASE_URL``
   and ``TEST_DATABASE_URL`` point to valid databases.

Sphinx cannot import ``src``
   Run the build from ``module_4/docs``. ``source/conf.py`` adds ``module_4``
   to Python's import path for autodoc.

Read the Docs build failure
   Confirm the repository is public, the project uses
   ``.readthedocs.yaml``, and ``module_4/requirements.txt`` installs without
   errors.
