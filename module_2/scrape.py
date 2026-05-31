from urllib import parse, robotparser

from selenium import webdriver
from bs4 import BeautifulSoup


# Confirm robots.txt permits scraping
agent = "rida"
base_url = "https://www.thegradcafe.com/"

parser = robotparser.RobotFileParser()
parser.set_url(parse.urljoin(base_url, "robots.txt"))
parser.read()

print(parser.can_fetch(agent, base_url))


# Use urllib to construct and manage GradCafe URL
survey_url = parse.urljoin(base_url, "survey")

print(survey_url)


# Use Selenium to open the page
driver = webdriver.Chrome()

driver.get(survey_url)

print(driver.title)


# Extract rendered HTML using Selenium page_source
html = driver.page_source

print(type(html))
print(html[:500])


# Parse rendered HTML with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

print(type(soup))
print(soup.title.text)


driver.quit()