Testing Guide
=============

Run the Entire Marked Suite
---------------------------

Run Pytest from the repository root so the coverage path in ``pytest.ini`` is
resolved correctly:

.. code-block:: console

   $ python -m pytest module_4 \
       -m "web or buttons or analysis or db or integration"

The configuration requires 100% coverage of ``module_4/src``. It also reports
the exact lines missing from coverage.

Markers
-------

``web``
   Flask route, page-load, and HTML structure tests.

``buttons``
   Pull Data, Update Analysis, busy-state, and endpoint error tests.

``analysis``
   Analysis labels and two-decimal percentage formatting tests.

``db``
   PostgreSQL schema, inserts, duplicate handling, and query tests.

``integration``
   End-to-end pull, update, database, and render tests.

``tests/conftest.py`` fails collection if any test lacks one of these markers.

Stable Page Selectors
---------------------

The Analysis page provides these stable selectors:

``data-testid="pull-data-btn"``
   Selects the Pull Data button.

``data-testid="update-analysis-btn"``
   Selects the Update Analysis button.

Fixtures and Test Doubles
-------------------------

``app``
   Creates a Flask application with ``TESTING`` enabled and replaces the real
   database connection with ``FakeConnection``.

``client``
   Returns Flask's test client for route requests without browser interaction.

``FakeConnection`` and ``FakeCursor``
   Return deterministic analysis values for page and formatting tests.

Injected scraper and loader functions
   Button and integration tests pass small Python functions into
   ``create_app``. These fakes provide known records and avoid live internet
   access or long-running Selenium scrapes.

``monkeypatch``
   Helper tests replace database, subprocess, thread, and Selenium operations
   with controlled test implementations.

Database Tests
--------------

Database and integration tests use ``TEST_DATABASE_URL`` and truncate the
``applicants`` table before each test. Duplicate URL inserts are ignored by the
table's uniqueness policy.
