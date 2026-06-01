def scrape_data():

    driver = webdriver.Chrome()
    records = []
    page_num = 1

    while True:

        current_url = parse.urljoin(BASE_URL, f"survey?page={page_num}")

        print(f"\nProcessing page {page_num}")
        print(current_url)

        driver.get(current_url)
        time.sleep(3)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split("\n")

        if "Graduate School Admission Results" not in body_text:
            print("No results page found.")
            break

        records.append({
            "url": current_url,
            "raw_text": body_text
        })

        print(f"Saved raw text for page {page_num}")

        if page_num >= 10:
            print("Stopping test run after page 10.")
            break

        page_num += 1

    driver.quit()
    return records