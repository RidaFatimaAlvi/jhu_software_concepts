"""Command-line entry point for scraping and loading Grad Cafe records."""

try:
    from .load_data import load_records
    from .scrape import scrape_data
except ImportError:  # pragma: no cover - supports ``python pull_data.py``
    from load_data import load_records
    from scrape import scrape_data


def pull_data(scraper=scrape_data, loader=load_records):
    """Scrape records and load them into PostgreSQL."""
    return loader(scraper())


if __name__ == "__main__":  # pragma: no cover - command-line helper
    print(f"Pull Data inserted {pull_data()} new records.")
