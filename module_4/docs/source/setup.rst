Overview and Setup
==================

Requirements
------------

The service requires Python 3.12, PostgreSQL, and the packages listed in
``module_4/requirements.txt``.

Install the project from the repository root:

.. code-block:: console

   $ python3 -m venv venv
   $ source venv/bin/activate
   $ python -m pip install -r module_4/requirements.txt

PostgreSQL Setup
----------------

Create one database for the application and one isolated database for tests:

.. code-block:: console

   $ createdb gradcafe_db
   $ createdb gradcafe_test

Environment Variables
---------------------

``DATABASE_URL``
   PostgreSQL connection URL used by the Flask application and data modules.
   When it is omitted, the application uses the local database
   ``gradcafe_db``.

``TEST_DATABASE_URL``
   PostgreSQL connection URL used by database and integration tests.

``SECRET_KEY``
   Optional Flask secret key. The development configuration supplies a local
   default, but a deployed service should set its own value.

Example local configuration:

.. code-block:: console

   $ export DATABASE_URL="postgresql:///gradcafe_db"
   $ export TEST_DATABASE_URL="postgresql:///gradcafe_test"

Run the Application
-------------------

From the repository root:

.. code-block:: console

   $ python module_4/src/app.py

Open ``http://127.0.0.1:8080/analysis``.

Build the Documentation
-----------------------

Following the lecture's separate source/build layout:

.. code-block:: console

   $ cd module_4/docs
   $ make html

The generated home page is ``module_4/docs/build/html/index.html``.
