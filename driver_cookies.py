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
    os.makedirs(path, exist_ok=True)


# Main driver setup function
def setup_driver(headless=False):
    temp_profile_path = "/tmp/chrome-profile"
    delete_and_create_dir(temp_profile_path)

    # Chrome options
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")

    # Launch Chrome
    driver = uc.Chrome(version_main=136, options=options, enable_automation=False)
    human_delay()

    # Load LinkedIn homepage
    driver.get("https://www.linkedin.com")
    human_delay()

    # 🔁 Refresh once to ensure full session initialization
    driver.refresh()
    human_delay(1.5, 2.5)

    # Try cookie files
    cookie_files = [
        "linkedin_cookies.pkl",
        "linkedin_cookies_2.pkl",
        "linkedin_cookies_3.pkl"
    ]

    success = False

    for filename in cookie_files:
        try:
            cookie_path = os.path.join(os.getcwd(), filename)
            with open(cookie_path, "rb") as f:
                cookies = pickle.load(f)

            for cookie in cookies:
                if "sameSite" in cookie and cookie["sameSite"] == "None":
                    cookie["sameSite"] = "Strict"
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie from {filename}: {e}")

            # Reload to apply cookies
            driver.get("https://www.linkedin.com")
            human_delay(1.5, 2.5)

            # Try accessing feed
            driver.get("https://www.linkedin.com/feed")
            human_delay(2, 4)

            print(f"✅ Successfully logged in using {filename}")
            success = True
            break
        except FileNotFoundError:
            print(f"❌ {filename} not found.")
        except Exception as e:
            print(f"⚠️ Failed to use {filename}: {e}")

    if not success:
        print("❌ No working cookie file found.")
        driver.quit()
        return None

    return driver