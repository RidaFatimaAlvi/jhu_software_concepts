"""Tests for cleaning Grad Cafe records."""

import json

import pytest

from src import clean


@pytest.fixture
def raw_records():
    raw_text = (
        "Johns Hopkins University\n"
        "Computer Science Masters\n"
        "Jun 14, 2026\n"
        "Accepted on Jun 1\n"
        "Total comments\n"
        "Fall 2026\n"
        "American\n"
        "GPA 3.90\n"
        "GRE 325\n"
        "GRE V 160\n"
        "GRE AW 4.5\n"
        "American\n"
        "Fall 2027\n"
        "Great program"
    )
    return [
        {"url": "https://example.test/1", "raw_text": raw_text},
        {"url": "https://example.test/1", "raw_text": raw_text},
        {"url": "https://example.test/empty", "raw_text": ""},
    ]


@pytest.mark.analysis
@pytest.mark.parametrize(
    "label, expected",
    [
        ("GPA", "3.90"),
        ("TOEFL", ""),
    ],
)
def test_extract_metric(raw_records, label, expected):
    assert clean.extract_metric(label, raw_records[0]["raw_text"]) == expected


@pytest.mark.analysis
def test_clean_records(raw_records):
    cleaned = clean.clean_records(raw_records)

    assert len(cleaned) == 1
    assert cleaned[0]["Degree"] == "Masters"
    assert cleaned[0]["comments"] == "Great program"


@pytest.mark.analysis
def test_clean_file(tmp_path, raw_records):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"
    input_file.write_text(json.dumps(raw_records), encoding="utf-8")

    cleaned = clean.clean_file(input_file, output_file)

    assert json.loads(output_file.read_text(encoding="utf-8")) == cleaned
