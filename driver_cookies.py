import time
import random
from io import StringIO
from datetime import datetime
import undetected_chromedriver as uc
import os
import pickle
#testgit
def human_delay(min_delay=1.0, max_delay=3.0):
    time.sleep(random.uniform(min_delay, max_delay))

def setup_driver(headless=False):
    temp_profile_path = "/tmp/chrome-temp-profile"  # Change to /tmp for Linux
    os.makedirs(temp_profile_path, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options, enable_automation=False, version_main=134)
    human_delay()

    # Go to LinkedIn main page to set domain
    driver.get("https://www.linkedin.com")
    human_delay()

    try:
        with open("linkedin_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Could not add cookie: {e}")

        driver.get("https://www.linkedin.com/feed")
        human_delay(2, 4)
    except FileNotFoundError:
        print("❌ linkedin_cookies.pkl not found. Please save cookies first.")
        driver.quit()
        return None

    return driver