
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import undetected_chromedriver as uc
from google import genai

#Importing functions
from webinteraction import scrape_linkedin_jobs
from key_matching import create_df_keys
from clean_upload import process_and_upload_keywords_to_sheets
from clean_upload import clean_and_upload_job_df
from clean_upload import split_jobs_by_word_limit
from variables import urls,skill_list
from prompt import build_prompt
from driver_cookies import setup_driver
from webinteraction import handle_linkedin_login
# Update Google Sheets for just the current chunk
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("jobs-scraping-data-7c50ed566bd2.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Jobs data updated every 24 hours at 7pm").sheet1
skills_sheet = client.open("skillsets").sheet1
last_row = len(sheet.col_values(1)) + 1
next_row = len(skills_sheet.col_values(1)) + 1

# 🧠 Initialize driver only once

driver = setup_driver()
if driver is None:
    print("❌ Driver failed to launch. Exiting.")
    exit()
handle_linkedin_login(driver)
with open("linkedin_jobs_output.txt", "w", encoding="utf-8") as f:
    job_global_idx = 1

    for url_idx, url in enumerate(urls, start=1):
        results = scrape_linkedin_jobs(driver, url)  # Pass the same driver
        if not results:
            continue

        df_keys = create_df_keys(results, skill_list)
        uploaded_rows = process_and_upload_keywords_to_sheets(df_keys, skills_sheet, next_row)
        next_row += uploaded_rows

        f.write(f"########## URL #{url_idx} ##########\n")
        f.write(f"Scraped from: {url}\n\n")

        for job in results:
            f.write(f"--- Job #{job_global_idx} ---\n")
            f.write(f"Job Text:\n{job['text']}\n")
            f.write(f"Job Link: {job['job_link']}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            job_global_idx += 1

# ✅ Done scraping, now quit the driver
driver.quit()

# Run it
chunks = split_jobs_by_word_limit("linkedin_jobs_output.txt", max_words=15000)

# Display the result
for i, chunk in enumerate(chunks, 1):
    print(f"\n=== Chunk {i} ===\n")
    print(chunk[:10000])  # Print only first 1000 characters 
    print("\n" + "=" * 80 + "\n")


#Gimini Prompt and excecute

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

for i, input_string in enumerate(chunks):
    print(f"\n🔄 Processing chunk #{i + 1}")

    try:
        prompt = build_prompt(input_string)

        # Make LLM request
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        response_text = response.text
        print(f"✅ LLM response received for chunk #{i + 1}")

        # Parse CSV text
        try:
            df = pd.read_csv(
                StringIO(response_text),
                header=None,
                names=[
                    "company_name", "industry", "job_title", "city", "state", "employment_type",
                    "seniority_level", "min_salary", "max_salary", "salary_type",
                    "applicant_count", "job_link", "job_type", "requirements", "keywords",
                    "reposted", "min_year_experience", "hour_posted"
                ],
                on_bad_lines='skip',
                engine='python'
            )
        except Exception as e:
            print(f"❌ Failed to parse response for chunk #{i + 1}: {e}")
            continue

        # Upload to Google Sheet
        try:
            last_row = len(sheet.col_values(1)) + 1
            clean_and_upload_job_df(df, sheet, i)
            print(f"✅ Data uploaded for chunk #{i + 1}")
        except Exception as e:
            print(f"❌ Upload failed for chunk #{i + 1}: {e}")
            continue

    except Exception as e:
        print(f"❌ Failed to process chunk #{i + 1}: {e}")
        continue  
    


