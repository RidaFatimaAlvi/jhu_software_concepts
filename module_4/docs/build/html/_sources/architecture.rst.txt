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
   Reads applicant dictionaries and computes the analysis answers used by the
   Flask template.

Data Flow
---------

The normal flow is:

#. ``scrape_data`` collects raw records.
#. ``clean_records`` converts raw text to structured records.
#. ``load_records`` writes unique records to PostgreSQL.
#. Analysis queries read the stored rows.
#. Flask renders the results in ``src/templates/index.html``.
