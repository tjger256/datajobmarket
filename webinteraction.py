import time
import random
from io import StringIO
from datetime import datetime
from driver import human_delay
from driver import setup_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# This is the main function reponsible for clicking on the jobs and extracting data
def click_all_jobs_on_page(driver, job_data):
    try:
        job_list_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='scaffold-layout__list-item']"))
        )
    except TimeoutException:
        print("⏰ Timeout: No job listings found on the page.")
        return

    job_count = len(job_list_items)
    print(f"🔍 Found {job_count} job posts on this page.")

    for idx in range(job_count):
        try:
            # Refresh job elements each iteration to avoid stale references
            job_list_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='scaffold-layout__list-item']"))
            )

            if idx >= len(job_list_items):
                print(f"⚠️ Job index {idx} out of range. Skipping.")
                continue

            job = job_list_items[idx]

            # Scroll to and click the job listing
            ActionChains(driver).move_to_element(job).pause(random.uniform(0.3, 0.5)).click().perform()
            print(f"🗁 Clicked job #{idx}")
            human_delay(1.2, 2)

            # Try extracting the job detail panel
            try:
                detail_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-details__main-content.jobs-details__main-content--single-pane.full-width"))
                )

                job_text = detail_container.text.strip()

                # Truncate job text using cutoffs
                cutoffs = [
                    "Stand out by adding skills associated with the job post",
                    "Identified by LinkedIn",
                    "About the company"
                ]
                cut_index = min((job_text.find(phrase) for phrase in cutoffs if phrase in job_text), default=len(job_text))
                job_text = job_text[:cut_index].strip()

                # Extract job link
                try:
                    job_link_elem = detail_container.find_element(By.CSS_SELECTOR, "a[href^='/jobs/view/']")
                    job_link = job_link_elem.get_attribute("href")
                except Exception:
                    job_link = "N/A"

                job_data.append({
                    "index": idx,
                    "text": job_text,
                    "job_link": job_link
                })
                print(f" ✅ Extracted job #{idx}")

            except TimeoutException:
                print(f" ❌ Job #{idx} detail panel failed to load.")
                job_data.append({"index": idx, "text": "", "job_link": "N/A"})

        except Exception as e:
            print(f" ⚠️ Error on job #{idx}: {e}")
            job_data.append({"index": idx, "text": "", "job_link": "N/A"})
            continue

# this function responsible for going into the next page
def go_to_next_page(driver, max_retries=3):
    try:
        current_url = driver.current_url
        for attempt in range(max_retries):
            try:
                next_button = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='View next page']"))
                )

                if next_button.is_displayed() and next_button.is_enabled():
                    print(f"🔄 Attempting to click 'Next Page' (try #{attempt + 1})")
                    ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.3, 0.6)).click().perform()
                    human_delay(1.1, 2)

                    # Wait for the URL to change
                    WebDriverWait(driver, 8).until(lambda d: d.current_url != current_url)
                    print("✅ Page changed!")

                    # 🔁 Refresh #1
                    driver.get(driver.current_url)
                    print("🔁 First refresh complete.")
                    human_delay(2, 3)

                    # 🔁 Refresh #2
                    driver.get(driver.current_url)
                    print("🔁 Second refresh complete.")
                    human_delay(2, 3)

                    return True
                else:
                    print("🔐 'Next Page' button not interactable.")
                    return False

            except TimeoutException:
                print(f"⚠️ Page did not change after click attempt #{attempt + 1}. Retrying...")

        print("❌ Max retries reached. Stopping pagination.")
        return False

    except Exception as e:
        print("❌ Error while trying to go to the next page:", e)
        return False
    
# combine all the funtions above
def scrape_linkedin_jobs(url: str):
    driver = setup_driver()
    driver.get(url)
    print(" 🚀 Page loaded.")
    human_delay(2, 3)

    job_data = []

    while True:
        click_all_jobs_on_page(driver, job_data)
        if not go_to_next_page(driver):
            break
    print(f" 🚜 Finished scraping. Total job posts: {len(job_data)}")
    driver.quit()

    for i, job in enumerate(job_data):
        print(f"\n--- Job #{i + 1} ---\n{job['text'][:300]}...\n")

    return job_data