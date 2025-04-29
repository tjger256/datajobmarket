
import re
from datetime import datetime
from gspread_dataframe import set_with_dataframe
import pandas as pd
import numpy as np
# This will clean up and upload to google sheet
def process_and_upload_keywords_to_sheets(df_keys, skills_sheet, next_row):
    # Drop unnecessary columns
    df_keys.drop(columns="text", inplace=True)
    
    # Extract job ID
    df_keys["job_id"] = df_keys["job_link"].apply(
        lambda x: re.search(r"linkedin\.com/jobs/view/(\d{10})", x).group(1)
        if isinstance(x, str) and re.search(r"linkedin\.com/jobs/view/(\d{10})", x)
        else ""
    )
    df_keys.drop(columns=["job_link", "index"], inplace=True)

    # Clean keywords
    df_keys.dropna(subset=["job_id", "keywords"], inplace=True)
    df_keys["keywords"] = df_keys["keywords"].astype(str).str.lower()
    df_keys["keywords"] = df_keys["keywords"].str.split(",")
    df_keys = df_keys.explode("keywords")
    df_keys["keywords"] = df_keys["keywords"].str.strip()
    df_keys = df_keys[df_keys["keywords"] != ""]
    df_keys.drop_duplicates(subset=["job_id", "keywords"], inplace=True)

    # Ensure job_id is first column
    col = df_keys.pop("job_id")
    df_keys.insert(0, "job_id", col)

    # Upload to Google Sheets
    set_with_dataframe(skills_sheet, df_keys, row=next_row, include_column_header=False)
    print(f"✅ Uploaded {len(df_keys)} skill rows to Google Sheets!")

    # Return the number of rows uploaded so we can update next_row
    return len(df_keys)


def clean_and_upload_job_df(df, sheet, chunk_index):
    # 🔹 Clean whitespace from all string cells
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # Find the next available row dynamically
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # 🔹 Add import timestamp
    df["date_imported"] = datetime.now()

    # 🔹 Extract job_id from job_link
    df["job_id"] = df["job_link"].apply(
        lambda x: re.search(r"linkedin\.com/jobs/view/(\d{10})", x).group(1)
        if isinstance(x, str) and re.search(r"linkedin\.com/jobs/view/(\d{10})", x)
        else ""
    )

    # 🔹 Drop duplicates and invalid job_ids
    df = df.drop_duplicates(subset="job_id")
    df = df[df["job_id"].str.isnumeric()]

    # 🔹 Define role categories
    role_keywords = {
        "data scientist": ("data scientist", "statistician"),
        "data engineer": ("data engineer", "etl engineer", "data architect"),
        "data analyst": ("data analyst", "business analyst", "operations data analyst", "reporting analyst", "analytic"),
        "machine learning engineer": ("machine learning engineer", "ml engineer", "mlops", "ai engineer"),
        "cloud engineer": ("cloud engineer", "infrastructure engineer", "cloud architect", "platform engineer"),
        "solution architect": ("solution architect", "solutions architect", "systems architect")
    }

    # 🔹 Role mapping
    def rolecheck(title):
        if pd.isna(title):
            return None
        title_lower = title.lower()
        for role, keywords in role_keywords.items():
            if any(kw in title_lower for kw in keywords):
                return role
        return None

    df["role"] = df["job_title"].apply(rolecheck)

    # 🔹 Clean salary columns
    for col in ["min_salary", "max_salary"]:
        df[col] = df[col].replace(["NaN", ""], np.nan)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].apply(lambda x: int(x * 2080) if pd.notna(x) and x < 1000 else x)

    # 🔹 Drop salary_type (no longer needed)
    if "salary_type" in df.columns:
        df.drop(columns="salary_type", inplace=True)

    # 🔹 Compute job_posted_time
    df["hour_posted"] = pd.to_numeric(df["hour_posted"], errors='coerce')
    df["job_posted_time"] = df.apply(
        lambda row: row["date_imported"] - pd.to_timedelta(row["hour_posted"], unit="h")
        if pd.notna(row["hour_posted"]) else pd.NaT,
        axis=1
    )

    # 🔹 Upload cleaned data to Google Sheets
    last_row = len(sheet.col_values(1)) + 1
    set_with_dataframe(sheet, df, row=last_row, include_column_header=False)
    print(f"✅ Chunk #{chunk_index + 1} data uploaded to Google Sheets!")

    return df  # Optional: return cleaned DataFrame if needed


#breaking down into chunks:
def split_jobs_by_word_limit(file_path, max_words=15000):
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Split by job post marker
    jobs = full_text.split("--- Job #")
    jobs = [f"--- Job #{job.strip()}" for job in jobs if job.strip()]

    chunks = []
    current_chunk = ""
    current_word_count = 0

    for job in jobs:
        job_words = job.split()
        job_word_count = len(job_words)

        # If adding this job exceeds the word limit, save current chunk and start new one
        if current_word_count + job_word_count > max_words:
            chunks.append(current_chunk.strip())
            current_chunk = job + "\n\n"
            current_word_count = job_word_count
        else:
            current_chunk += job + "\n\n"
            current_word_count += job_word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Run it


