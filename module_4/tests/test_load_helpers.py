"""Tests for loading and database helper functions."""

import json
from datetime import date

import pytest

from src import load_data, query_data


@pytest.mark.db
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        ("", None),
        ("1,234.", 1234.0),
        ("invalid", None),
    ],
)
def test_clean_float(value, expected):
    assert load_data.clean_float(value) == expected


@pytest.mark.db
@pytest.mark.parametrize(
    "value, expected",
    [
        ("", None),
        (date(2026, 6, 14), date(2026, 6, 14)),
        ("Jun 14, 2026", date(2026, 6, 14)),
    ],
)
def test_clean_date(value, expected):
    assert load_data.clean_date(value) == expected


@pytest.mark.db
def test_required_fields():
    with pytest.raises(ValueError, match="Missing required fields"):
        load_data.normalize_record({})


@pytest.mark.db
@pytest.mark.parametrize("module", [load_data, query_data])
def test_database_connection(module, monkeypatch):
    calls = []
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(
        module.psycopg,
        "connect",
        lambda *args, **kwargs: calls.append((args, kwargs)) or "connection",
    )

    assert module.get_connection("postgresql://test") == "connection"
    assert module.get_connection() == "connection"
    assert calls == [
        (("postgresql://test",), {}),
        ((), {"dbname": "gradcafe_db"}),
    ]


@pytest.mark.db
def test_load_json_file(tmp_path, monkeypatch):
    input_file = tmp_path / "rows.json"
    input_file.write_text(
        json.dumps([{"program": "Computer Science"}]),
        encoding="utf-8",
    )
    received = []
    monkeypatch.setattr(
        load_data,
        "load_records",
        lambda rows, factory: received.extend(rows) or 1,
    )

    assert load_data.load_json_file(input_file, lambda: None) == 1
    assert received == [{"program": "Computer Science"}]


@pytest.mark.db
def test_insert_error_rolls_back():
    class Cursor:
        rowcount = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, query, row=None):
            if row is not None:
                raise RuntimeError("insert failed")

    class Connection:
        rolled_back = False
        closed = False

        def cursor(self):
            return Cursor()

        def commit(self):
            pass

        def rollback(self):
            self.rolled_back = True

        def close(self):
            self.closed = True

    connection = Connection()
    row = {
        "program": "Computer Science",
        "date_added": "Jun 14, 2026",
        "url": "https://example.test/error",
        "status": "Accepted on Jun 1",
        "term": "Fall 2026",
        "US/International": "American",
        "Degree": "Masters",
    }

    with pytest.raises(RuntimeError, match="insert failed"):
        load_data.load_records([row], lambda: connection)

    assert connection.rolled_back is True
    assert connection.closed is True
