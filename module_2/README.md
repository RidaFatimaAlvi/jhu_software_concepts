# Module 2 - Web Scraping
## Reference Materials Used

- Real Python: Python Web Scraping Practical Introduction
- Real Python: Beautiful Soup Web Scraper
- GeeksforGeeks: Selenium Python Tutorial
- GeeksforGeeks: Selenium Features
- GeeksforGeeks: Limitations of Selenium
- GeeksforGeeks: Selenium Python Introduction and Installation
- GeeksforGeeks: Navigating Links Using get() in Selenium Python
- GeeksforGeeks: Interacting with Webpages Using Selenium Python
- GeeksforGeeks: Locating Multiple Elements in Selenium Python
- GeeksforGeeks: Selenium Locating Strategies
- GeeksforGeeks: Explicit Waits in Selenium Python
- GeeksforGeeks: Implicit Waits in Selenium Python

# Module 2 - Web Scraping

## Robots.txt Compliance

Before scraping GradCafe, I checked the robots.txt file at:

https://www.thegradcafe.com/robots.txt

I reviewed the file manually in the browser and also plan to verify crawler access programmatically in `scrape.py` using Python's `urllib.robotparser`. The scraper will only access publicly available GradCafe pages that are permitted by robots.txt.

A screenshot of the robots.txt page is included in this folder as `screenshot.jpg`.

The scraper will use polite scraping practices, including delays between requests, and will stop if the website blocks, rate-limits, or rejects requests.