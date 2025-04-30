import time
import random
import undetected_chromedriver as uc
import pickle
import os
import shutil


# Simulated human-like delay
def human_delay(min_delay=1.0, max_delay=3.0):
    time.sleep(random.uniform(min_delay, max_delay))


# Robust directory cleanup
def delete_and_create_dir(path):
    # Kill Chrome processes in case they're locking files
    os.system("taskkill /f /im chrome.exe >nul 2>&1")
    time.sleep(1)

    # Retry-safe directory deletion
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"⚠️ Initial deletion failed: {e}")
            time.sleep(2)
            try:
                shutil.rmtree(path)
            except Exception as e2:
                print(f"❌ Final deletion failed: {e2}")
                raise

    # Create fresh directory
    os.makedirs(path, exist_ok=False)


# Main driver setup function
def setup_driver(headless=False):
    temp_profile_path = r"C:\Temp\chrome-temp-profile"
    delete_and_create_dir(temp_profile_path)

    # Set Chrome options
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Launch undetected Chrome driver
    driver = uc.Chrome(options=options, enable_automation=False, version_main=135)

    human_delay()

    # Go to LinkedIn to initialize cookies
    driver.get("https://www.linkedin.com")
    human_delay()

    try:
        cookie_path = (
            r"C:\Users\Will\Desktop\Permanent file\Linkedin project\organizer\linkedin_cookies.pkl"
        )
        with open(cookie_path, "rb") as f:
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