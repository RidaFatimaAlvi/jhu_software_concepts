"""Tests for Analysis labels and percentage formatting."""

import re

import pytest
from bs4 import BeautifulSoup


@pytest.mark.analysis
def test_analysis_labels_and_percentage_rounding(client):
    response = client.get("/analysis")
    page_text = response.get_data(as_text=True)
    page = BeautifulSoup(page_text, "html.parser")
    analysis_items = page.select("div.question")[1:]

    assert "Answer:" in page_text
    assert all("Answer:" in item.get_text(" ", strip=True) for item in analysis_items)
    assert "39.28%" in page_text
    assert "42.50%" in page_text

    percentages = re.findall(r"\d+\.\d{2}%", page_text)

    assert percentages == ["39.28%", "42.50%"]
