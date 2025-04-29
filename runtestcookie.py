import time
import pickle
import undetected_chromedriver as uc
import os

def setup_driver_with_cookies(headless=False):
    # Use a temp profile directory to avoid using your real Chrome profile
    temp_profile_path = r"C:\Temp\chrome-temp-profile"
    os.makedirs(temp_profile_path, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_profile_path}")  # clean temporary profile
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options, enable_automation=False, version_main=134)
    time.sleep(3)  # Let browser initialize

    # Go to LinkedIn main page to set the right domain
    driver.get("https://www.linkedin.com")
    time.sleep(3)

    # ✅ Load cookies
    try:
        with open("linkedin_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"  # fix for undetected_chromedriver bug

            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Could not add cookie: {e}")

        # Refresh to apply cookies
        driver.get("https://www.linkedin.com/feed")
        time.sleep(5)

    except FileNotFoundError:
        print("❌ linkedin_cookies.pkl not found. Please log in and save cookies first.")
        driver.quit()
        return None

    return driver

# Run the driver
if __name__ == "__main__":
    driver = setup_driver_with_cookies(headless=False)

    if driver:
        print("✅ Logged into LinkedIn with cookies!")
        input("Press Enter to close browser...")
        driver.quit()
