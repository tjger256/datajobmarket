import time
import random
from io import StringIO
from datetime import datetime
from driver_cookies import human_delay
from driver_cookies import setup_driver
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
        
        # 🔁 Retry ONCE in case the new page just loaded empty
        print("🔄 Refreshing and retrying once...")
        try:
            driver.get(driver.current_url)
            human_delay(2, 3)
            job_list_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='scaffold-layout__list-item']"))
            )
        except Exception:
            print("❌ Still no jobs found after refresh. Skipping this page.")
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
"""
def go_to_next_page(driver, max_retries=3):
    try:
        current_url = driver.current_url

        # 🔁 Try clicking "Next Page" button
        for attempt in range(max_retries):
            try:
                next_button = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='View next page']"))
                )

                if next_button.is_displayed() and next_button.is_enabled():
                    print(f"🔄 Attempting to click 'Next Page' (try #{attempt + 1})")
                    ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.3, 0.6)).click().perform()
                    human_delay(1.6, 2)

                    WebDriverWait(driver, 8).until(lambda d: d.current_url != current_url)
                    print("✅ Page changed using 'Next Page' button.")

                    driver.get(driver.current_url)
                    print("🔁 First refresh complete.")
                    human_delay(2, 3)
                    driver.get(driver.current_url)
                    print("🔁 Second refresh complete.")
                    human_delay(2, 3)

                    return True

            except TimeoutException:
                print(f"⚠️ Attempt #{attempt + 1} failed. Retrying...")

        print("❌ 'Next Page' button failed. Trying numbered pagination...")

        # 🔁 Fallback: Click numbered page button
        current_active = driver.find_element(By.CSS_SELECTOR, "li.artdeco-pagination__indicator--number.active")
        next_sibling = current_active.find_element(By.XPATH, "following-sibling::li[1]")

        if next_sibling:
            try:
                button = next_sibling.find_element(By.TAG_NAME, "button")
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                human_delay(0.5, 1)
                driver.execute_script("arguments[0].click();", button)
                print("✅ Page changed using numbered pagination.")
                human_delay(2, 3)
                return True
            except Exception as e:
                print("❌ Could not click numbered pagination:", e)
                return False

        print("❌ No next page found via numbered pagination.")
        return False

    except Exception as e:
        print("❌ Unexpected error during pagination:", e)
        return False
# combine all the funtions above
"""
def go_to_next_page(driver, use_numbered_only=False, max_retries=3):
    try:
        current_url = driver.current_url

        # 🚫 Skip Next if we're already in numbered-only mode
        if use_numbered_only:
            success = click_next_numbered_page(driver, current_url, max_retries)
            return success, True

        # ✅ Try clicking "Next Page" button first
        for attempt in range(max_retries):
            try:
                next_button = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='View next page']"))
                )

                if next_button.is_displayed() and next_button.is_enabled():
                    print(f"🔄 Attempting to click 'Next Page' (attempt #{attempt + 1})")
                    ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.3, 0.6)).click().perform()
                    human_delay(1.6, 2)

                    WebDriverWait(driver, 8).until(lambda d: d.current_url != current_url)
                    print("✅ Page changed via 'Next Page' button.")

                    driver.get(driver.current_url)
                    print("🔁 First refresh complete.")
                    human_delay(2, 3)
                    driver.get(driver.current_url)
                    print("🔁 Second refresh complete.")
                    human_delay(2, 3)

                    return True, False  # Success, still using Next button

            except TimeoutException:
                print(f"⚠️ Attempt #{attempt + 1} to click 'Next Page' failed.")

        # 🔁 If all retries failed, switch to numbered pagination
        print("❌ Switching to numbered pagination...")
        success = click_next_numbered_page(driver, current_url, max_retries)
        return success, True  # Now using numbered-only mode

    except Exception as e:
        print("❌ Unexpected error in go_to_next_page:", e)
        return False, use_numbered_only
    
def click_next_numbered_page(driver, current_url, max_retries=3):
    try:
        for attempt in range(max_retries):
            try:
                current_active = driver.find_element(By.CSS_SELECTOR, "li.artdeco-pagination__indicator--number.active")
                next_sibling = current_active.find_element(By.XPATH, "following-sibling::li[1]")

                if next_sibling:
                    button = next_sibling.find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    human_delay(0.5, 1)
                    print(f"🔢 Clicking numbered pagination (attempt #{attempt + 1})")
                    driver.execute_script("arguments[0].click();", button)
                    human_delay(2, 3)

                    WebDriverWait(driver, 8).until(lambda d: d.current_url != current_url)
                    print("✅ Page changed using numbered pagination.")

                    driver.get(driver.current_url)
                    print("🔁 First refresh complete.")
                    human_delay(2, 3)
                    driver.get(driver.current_url)
                    print("🔁 Second refresh complete.")
                    human_delay(2, 3)

                    return True

                else:
                    print("❌ No next numbered page found.")
                    return False

            except TimeoutException:
                print(f"⚠️ Attempt #{attempt + 1} to click numbered pagination failed.")

        print("❌ Max retries reached on numbered pagination.")
        return False

    except Exception as e:
        print("❌ Error during numbered pagination:", e)
        return False

def scrape_linkedin_jobs(driver, url: str):
    if driver is None:
        print(f"🚫 Driver not available. Skipping: {url}")
        return []

    driver.get(url)
    print(" 🚀 Page loaded.")

    # 🔁 Refresh once after initial load to ensure full content
    driver.refresh()
    human_delay(1.5, 2.5)
    print("🔁 Page refreshed.")

    job_data = []
    use_numbered_only = False  # Start with 'Next Page' logic

    while True:
        click_all_jobs_on_page(driver, job_data)

        success, switched_to_pagination = go_to_next_page(driver, use_numbered_only)

        if not success:
            print("🛑 Reached last page or failed to paginate.")
            break

        if switched_to_pagination:
            use_numbered_only = True  # Permanently switch mode

    print(f" 🚜 Finished scraping. Total job posts: {len(job_data)}")

    for i, job in enumerate(job_data):
        print(f"\n--- Job #{i + 1} ---\n{job['text'][:300]}...\n")

    return job_data


def handle_linkedin_login(driver, password="Tai836376@"):
    try:
        print("⏳ Checking for password field...")
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "password"))  # ← ✅ correct ID from your screenshot
        )
        password_input.clear()
        password_input.send_keys(password)
        print("✅ Entered password.")
        password_input.submit()
        return True
    except TimeoutException:
        print("❌ Password field not found — maybe already logged in.")
        return False