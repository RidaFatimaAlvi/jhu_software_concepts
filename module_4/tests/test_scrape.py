"""Tests for scraper helper functions without using the live internet."""

import pytest

from src import scrape


class Element:
    text = "Computer Science"

    def __init__(self, url):
        self.url = url

    def get_attribute(self, name):
        return self.url


class Driver:
    page_source = "<html></html>"

    def __init__(self, elements):
        self.elements = elements
        self.page = 0
        self.quit_called = False

    def get(self, url):
        self.page += 1

    def find_element(self, by, value):
        return type("Body", (), {"text": "Rendered page"})()

    def find_elements(self, by, value):
        return self.elements

    def quit(self):
        self.quit_called = True


def install_fake_browser(monkeypatch, driver, stop_after_first_page=False):
    class Wait:
        def __init__(self, current_driver, timeout):
            self.driver = current_driver

        def until(self, condition):
            if stop_after_first_page and self.driver.page > 1:
                raise RuntimeError("done")
            return True

    monkeypatch.setattr(scrape.webdriver, "Chrome", lambda: driver)
    monkeypatch.setattr(scrape, "WebDriverWait", Wait)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)


@pytest.mark.buttons
def test_robots_file_and_json_helpers(tmp_path, monkeypatch):
    class RobotParser:
        def set_url(self, url):
            pass

        def read(self):
            pass

        def can_fetch(self, agent, url):
            return True

    monkeypatch.setattr(scrape.robotparser, "RobotFileParser", RobotParser)
    assert scrape.check_robots() is True

    rows = [{"url": "https://example.test/1"}]
    output_file = tmp_path / "records.json"

    assert scrape.clean_data(rows) == rows
    scrape.save_data(rows, output_file)
    assert scrape.load_data(output_file) == rows


@pytest.mark.buttons
def test_scrape_data(monkeypatch):
    driver = Driver(
        [
            Element(None),
            Element("https://www.thegradcafe.com/result/1"),
        ]
    )
    install_fake_browser(monkeypatch, driver, stop_after_first_page=True)

    records = scrape.scrape_data()

    assert len(records) == 1
    assert records[0]["url"].endswith("/result/1")
    assert driver.quit_called is True


@pytest.mark.buttons
def test_scrape_empty_page(monkeypatch):
    driver = Driver([])
    install_fake_browser(monkeypatch, driver)

    assert scrape.scrape_data() == []


@pytest.mark.buttons
def test_scrape_record_limit(monkeypatch):
    driver = Driver([Element("https://www.thegradcafe.com/result/limit")])
    install_fake_browser(monkeypatch, driver)
    monkeypatch.setattr(scrape, "MAX_RECORDS", 1)

    assert len(scrape.scrape_data()) == 1
