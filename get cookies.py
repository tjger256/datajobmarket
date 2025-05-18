import time
import pickle
import undetected_chromedriver as uc
import tempfile
# Set up Chrome with your working profile
def setup_driver(headless=False):
    options = uc.ChromeOptions()

    temp_profile = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options, enable_automation=False)
    time.sleep(5)  # Let profile load fully
    return driver

# ✅ Launch browser and log in manually
driver = setup_driver(headless=False)
driver.get("https://www.linkedin.com")

input("🧠 After logging in manually, press Enter to save cookies...")

# ✅ Save cookies
with open("linkedin_cookies2.pkl", "wb") as f:
    pickle.dump(driver.get_cookies(), f)

print("✅ Cookies saved to linkedin_cookies.pkl")
driver.quit()
