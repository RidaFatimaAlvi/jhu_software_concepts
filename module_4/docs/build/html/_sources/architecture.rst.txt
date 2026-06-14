Architecture
============

Web Layer
---------

``src.app`` creates the Flask application and exposes these routes:

``GET /`` and ``GET /analysis``
   Query PostgreSQL and render the analysis page.

``POST /pull-data``
   Start a data pull. Injected scraper and loader functions make this route
   deterministic during tests. A request returns HTTP 409 while a pull is
   already active.

``POST /update-analysis``
   Permit an analysis refresh when the service is idle. A request returns HTTP
   409 while a pull is active.

ETL Layer
---------

``src.scrape``
   Uses Selenium and Beautiful Soup to collect raw Grad Cafe records.

``src.clean``
   Parses raw page text and converts records into the required Module 3 field
   structure.

``src.pull_data``
   Coordinates the scraper and loader.

Database Layer
--------------

``src.load_data``
   Creates the ``applicants`` table, validates required fields, normalizes
   values, inserts rows transactionally, and ignores duplicate URLs.

``src.query_data``
   Provides reusable functions that read applicant dictionaries and return the
   analysis answer keys expected by the Flask template. The current Flask route
   executes equivalent SQL directly.

Data Flow
---------

The application contains these ETL stages:

#. ``scrape_data`` collects raw records.
#. ``clean_records`` converts raw text to structured records.
#. ``load_records`` writes unique records to PostgreSQL.
#. Analysis queries read the stored rows.
#. Flask renders the results in ``src/templates/index.html``.

``src.pull_data.pull_data`` currently coordinates the scraper and loader
directly. Structured or cleaned records must therefore be supplied to the
loader; cleaning is also available separately through ``src.clean``.
