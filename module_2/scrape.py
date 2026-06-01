from urllib import parse, robotparser
import json
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.thegradcafe.com/"


def check_robots():
    agent = "rida"

    parser = robotparser.RobotFileParser()
    parser.set_url(parse.urljoin(BASE_URL, "robots.txt"))
    parser.read()

    return parser.can_fetch(agent, BASE_URL)


def scrape_data():

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    records = []
    page_num = 1

    while True:

        current_url = parse.urljoin(BASE_URL, f"survey?page={page_num}")

        print(f"\nProcessing page {page_num}")
        print(current_url)

        driver.get(current_url)
        time.sleep(2)

        try:
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@href, '/result/')]")
                )
            )
        except:
            print("No more results found.")
            break

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        body_text = driver.find_element(By.TAG_NAME, "body").text

        result_elements = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/result/')]"
        )

        page_records = 0

        for element in result_elements:

            full_url = element.get_attribute("href")

            if full_url:

                # Get the visible text from the result card/link area
                program_text = element.text.strip()

                records.append({
                    "program": program_text,
                    "university": None,
                    "comments": None,
                    "date_added": None,
                    "url": full_url,
                    "applicant_status": None,
                    "acceptance_date": None,
                    "rejection_date": None,
                    "start_term": None,
                    "student_type": None,
                    "gre_score": None,
                    "gre_v": None,
                    "degree": None,
                    "gpa": None,
                    "gre_aw": None,
                    "raw_text": body_text
                })

                page_records += 1

        print(f"Found {page_records} records on page {page_num}")

        if page_records == 0:
            print("No records found. Ending scrape.")
            break

        if len(records) >= 3:
            print("Collected at least 30,000 records.")
            break

        page_num += 1

    driver.quit()
    return records


def clean_data(records):
    return records


def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

try:
    print("Robots Allowed:", check_robots())
except Exception as e:
    print("robots.txt check skipped:", e)

survey_url = parse.urljoin(BASE_URL, "survey")
parsed_url = parse.urlparse(survey_url)

print("Scheme:", parsed_url.scheme)
print("Domain:", parsed_url.netloc)
print("Path:", parsed_url.path)

records = scrape_data()
cleaned_records = clean_data(records)

if len(cleaned_records) > 0:
    print(cleaned_records[0]["url"])

save_data(cleaned_records, "module_2/applicant_data.json")

print(f"\nSaved {len(cleaned_records)} records.")