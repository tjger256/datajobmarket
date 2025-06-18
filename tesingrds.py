import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

rds_conn = pymysql.connect(
    host=os.getenv("RDS_HOST"),
    user=os.getenv("RDS_USER"),
    password=os.getenv("RDS_PASSWORD"),
    database=os.getenv("RDS_DATABASE"),
    charset="utf8mb4"
)
cursor = rds_conn.cursor()
print("✅ Connected!")

try:
    job_id = 4229269717  # Job ID from the provided data

    cursor.execute("""
        INSERT INTO jobs (
            company_name, industries, job_title, city, state,
            employment_type, seniority_level, min_salary, max_salary,
            applicant_count, job_link, job_type, requirements,
            keywords, reposted, min_year_experience, hour_posted,
            date_imported, job_id, role, job_posted_time
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """, (
        "Jobs via Dice", "Professional and Business Services", "Salesforce Certified Solution Architect w/ Pre-Sales exp - Remote - US-Physical Resident", None, "US",
        "Full time", "Mid-Senior level", None, None, 1,
        "https://www.linkedin.com/jobs/view/4229269716", "remote", 
        "As a Salesforce Architect, you will lead the adoption, optimization, and evolution of the Salesforce platform, integrating advanced technologies to deliver innovative solutions. You'll be responsible for defining the architecture, establishing standards, and ensuring the health of the overall solution, all while mentoring the technical team, sharing knowledge, and driving process improvements.",
        "Salesforce", "no", 8, 13,
        "2025-05-17 07:55:02", job_id, "solution architect", "2025-05-16 18:55:02"
    ))

    rds_conn.commit()
    print("✅ Job row inserted.")

except Exception as e:
    print(f"❌ Failed to insert: {e}")

finally:
    rds_conn.close()
