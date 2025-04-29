
import re
import pandas as pd

# This function check if there are mathcing keywords mentioned in the job post
def create_df_keys(results, skill_list):
    # Convert results list to DataFrame
    df_keys = pd.DataFrame(results)
    
    # Ensure job descriptions are strings
    df_keys['text'] = df_keys['text'].astype(str)

    # Function to find matching skills
    def match_skills(job_text):
        matched = [
            skill for skill in skill_list 
            if re.search(r'\b' + re.escape(skill) + r'\b', job_text, re.IGNORECASE)
        ]
        return ", ".join(matched) if matched else "NaN"

    # Apply matching function to each row
    df_keys['keywords'] = df_keys['text'].apply(match_skills)

    return df_keys