import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
import openai
import re
from selenium.common.exceptions import TimeoutException
from google import genai


urls = ["https://www.linkedin.com/jobs/search/?currentJobId=4205727374&distance=25&f_TPR=r2400&geoId=103644278&keywords=%22data%20analytics%22",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203732064&f_TPR=r86400&geoId=103644278&keywords=%22data%20analyst%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4200849863&f_TPR=r86400&geoId=103644278&keywords=%22data%20scientist%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4201325602&f_TPR=r86400&geoId=103644278&keywords=%22data%20engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4200953581&f_TPR=r86400&geoId=103644278&keywords=%22Machine%20Learning%20Engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203256390&f_TPR=r86400&geoId=103644278&keywords=%22AI%20Engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203246482&f_TPR=r86400&geoId=103644278&keywords=%22Infrastructure%20Engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON",
        "https://www.linkedin.com/jobs/search/?currentJobId=4201105920&f_TPR=r86400&geoId=103644278&keywords=%22Platform%20Engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203536945&f_TPR=r86400&geoId=103644278&keywords=%22data%20architect%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4200953766&f_TPR=r86400&geoId=103644278&keywords=%22Cloud%20engineer%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203854911&f_TPR=r86400&geoId=103644278&keywords=%22Systems%20Architect%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4204505306&f_TPR=r86400&geoId=103644278&keywords=%22solutions%20architect%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "https://www.linkedin.com/jobs/search/?currentJobId=4204400464&f_TPR=r86400&geoId=103644278&keywords=%22%20System%20Architect%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON",
        "https://www.linkedin.com/jobs/search/?currentJobId=4203473557&f_TPR=r86400&geoId=103644278&keywords=%22Solution%20Architect%22&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
]
skill_list = [
"MongoDB","A/B", "A/B testing", "PowerBI", "Cassandra", "MariaDB", "DynamoDB", "Neo4j", "Couchbase", "SQL Server", "DB2", "MySQL", "Elasticsearch", "SQLite", "Redis", "Firebase", "PostgreSQL", "Hadoop", "Azure", "TensorFlow", "Spark", "PyTorch", "AWS", "Power BI", "Scala", "Keras", "Word", "SAS", "Excel", "Tableau", "Redshift", "NoSQL", "Terraform", "Kotlin", "Swift", "Drupal", "VMware", "CouchDB", "DataRobot", "MLR", "Snowflake", "Theano", "Heroku", "Airflow", "Java", "Colocation", "OpenStack", "Erlang", "NLTK", "Perl", "Zoom", "OpenCV", "Ansible", "Puppet", "Elixir", "Splunk", "Aurora", "Docker", "CodeCov", "Angular.js", "RShiny", "Tidyverse", "Kubernetes", "RingCentral", "Wire", "CSS", "Play Framework", "Airtable", "Pulumi", "Yarn", "Python", "GCP", "React.js", "Express", "Matplotlib", "macOS", "Fastify", "GDPR", "PHP", "Dlib", "DataBricks", "Django", "Unreal", "Clojure", "Groovy", "Flask", "IBM Cloud","IBM", "Seaborn", "Jenkins", "Linux", "Confluence", "Jupyter", "Unity", "GitHub", "Twilio", "Julia", "Laravel", "C#", "Selenium", "C++", "CentOS", "R", "jQuery", "SUSE", "MATLAB", "Flow", "PySpark", "RedHat", "Qlik", "Nuix", "Bash", "Bitbucket", "Spring", "Unify", "SQL", "Plotly", "Phoenix", "T-SQL", "PowerShell", "JavaScript", "Git", "Unix", "Flutter", "Jira", "HTML", "Mattermost", "Chef", "GitLab", "SVN", "ASP.NET Core","ASP.NET", "ASP", "SSIS", "Xamarin", "Sass", "NumPy", "Scikit-learn","scikitlearn", "ggplot2", "Pandas", "Oracle", "React", "Objective-C", "Alteryx", "Cognos", "DAX", "Assembly", "SSRS", "Visio", "Microsoft", "WebEx", "Ionic", "Symfony", "Dart", "Nuxt.js","nuxt", "CodeCommit", "Digital Ocean", "Spreadsheet", "MicroStrategy", "Google Sheets", "googlesheet","google sheet", "Microsoft Teams","Microsoft", "R IDE", "IDE", "Google Data Studio", "google studio", "QlikView", "Looker", "Sisense", "Domo", "TIBCO Spotfire", "TIBCO","Spotfire", "Superset", "Zoho", "Chartio", "Mode Analytics", "mode", "Datawrapper", "Klipfolio", "SPSS", "Stata", "KNIME", "RapidMiner", "Hive", "Pig", "NiFi", "Flink", "Sqoop", "BigQuery", "Data Factory", "Informatica", "Presto", "Data Integrator", "Kafka Connect","kafka", "Redash", "DBeaver", "Google Cloud", "Prometheus", "Grafana", "Packer", "HashiCorp Vault", "Istio", "Lucidchart", "Draw.io", "Enterprise Architect", "Archi", "Postman", "Swagger", "MuleSoft", "IBM", "Red Hat Fuse","redhatfuse", "NGINX", "HAProxy", "F5 BIG-IP", "bigip", "f5", "ServiceNow", "ELK Stack", "ELK", "Slack", "RStudio", "Anaconda", "IBM Watson","IBM","watson", "Colab", "H2O.ai","H2O", "Weka", "BigML", "MXNet", "Caffe", "ONNX", "MLflow", "Kubeflow", "TensorBoard", "SageMaker", "Google AI", "DVC", "CUDA", "cuDNN", "SciPy", "XGBoost", "LightGBM", "CatBoost", "DuckDB", "dbt", "Metabase", "Trino", "Starburst", "Amundsen", "Apache", "Delta Lake", "Iceberg", "Hudi", "MLlib", "Bedrock", "LangChain", "Hugging Face", "huggingface", "AutoML", "Vertex AI", "vetexai", "Dataform", "Prefect", "Evidently", "Feast", "Featuretools", "BentoML", "Streamlit", "Gradio", "Weights & Biases","weight and biases","weight and bias", "Neptune.ai", "Ray", "Dask", "RAPIDS", "Snowpark", "Synapse", "Azure ML", "Azure", "Databricks", "QuickSight", "Athena", "Glue", "AppFlow", "EventBridge", "CloudFormation", "CloudWatch", "IAM", "VPC", "ECS", "EKS", "API Gateway", "Step Functions", "CloudTrail", "Datadog", "New Relic", "relic", "OpenTelemetry", "Monte Carlo", "Alation", "Collibra", "Atlan", "Immuta", "Fivetran", "Stitch", "Hevo", "Airbyte", "RudderStack", "Census", "Hightouch", "Dagster", "Tecton", "DataHub", "MLReef", "Flyte", "Pachyderm", "ClearML", "Polyaxon", "Hopsworks", "Trifacta", "PowerCenter", "Google Cloud PLatform"
]


def build_prompt(input_string):
    prompt1 = f"""
        
    You are an assistant that helps extract structured information from job descriptions and outputs it as a CSV row.
    For every job post, you will create one CSV row. For example, if there are 20 job posts, you will return 20 rows.
    Each row must contain exactly 17 commas (18 values) in the following order:
    "company_name","industry","job_title","city","state","employment_type","seniority_level","min_salary","max_salary","salary_type","applicant_count","job_link","job_type","requirements","keywords","reposted","min_year_experience","hour_posted"
                
    📌 Process:

    Step 0: Count the number of job posts from the input
    - save total count: n
    . With each job, assign a number from 1 to n 
    - loop through each job from 1 to n
    - for each job go through steps 1 to 15.
    - The number of final CSV rows must exactly match the number of job posts.

    Step 1: Extract the company name.
    - This field can not be empty
    - if not found give the best guest from the job
    - Save as: "company_name"

    Step 2: Determine the company's industry.
    - Choose one from this list only:
    Agriculture and Forestry, Mining and Extraction, Manufacturing, Energy and Utilities, Construction, Transportation and Logistics, Retail and Wholesale Trade, Financial Services, Healthcare, Technology and IT, Professional and Business Services, Education, Entertainment and Media, Hospitality and Tourism, Real Estate, Public Administration and Government, Nonprofit and Social Services, Personal and Consumer Services.
    - If not found, output "NaN".
    - Save as: "industry"

    Step 3: Extract the job title.
    - Wrap the title in quotation marks: "Data Analyst - Data Engineer"
    - This field can not be empty
    - if not found give the best guest from the job
    - Save as: "job_title"

    Step 4: Extract the city.
    - Do not include "US", "USA", or "United States"
    - Must not include country names
    - Must not include state names
    - If not found, output "NaN"
    - Save as: "city"

    Step 5: Extract the state (2-letter abbreviation, e.g., CA, TX).
    - Must not include country names
    - Do not include "US", "USA", or "United States"
    - If not found, make the best guess from the job post, if still not found, output "NaN"
    - Save as: "state"

    Step 6: Extract the employment type.
    - Must be One of: Full time, Part time, Contract, Internship, Temporary
    - If not found, output "NaN"
    - Exclude “Remote” or “Onsite”
    - Save as: "employment_type"

    Step 7: Extract the seniority level.
    - Must be one of: Internship, Entry level, Associate, Mid level, Mid-Senior level, Senior level, Director, Executive
    - If not found, make the best guess from the job post, otherwise, output "NaN"
    - Save as: "seniority_level"

    Step 8: Extract the minimum salary.
    - Numeric only, no $ or commas
    - If not found, make the best guess from the job post, otherwise, output "NaN"
    - Save as: "min_salary"

    Step 9: Extract the maximum salary.
    - Same rules as minimum
    - If not found, make the best guess from the job post, otherwise, output "NaN"
    - Save as: "max_salary"

    Step 10: Extract salary type.
    - One of: hourly, monthly, yearly
    - If not found, output "NaN"
    - Save as: "salary_type"

    Step 11: Extract applicant count.
    - Must be a number (e.g. 43)
    - This field can not be empty, if not fount, make the best guess from the job
    - Save as: "applicant_count"

    Step 12: Extract the job link (ending with job ID only).
    - For instance: https://www.linkedin.com/jobs/view/4191528049/?tracking → https://www.linkedin.com/jobs/view/4191528049
    - No parameters
    - If not found, output "NaN"
    - Save as: "job_link"

    Step 13: Extract the job type.
    - Must be One of: remote, hybrid, onsite
    - If not found, output "NaN"
    - Save as: "job_type"

    Step 14: Summarize the requirements and skills.
    - One paragraph
    - If not found, output "NaN"
    - Save as: "requirements"
    
    Step 15: Extarct the words from this skill list: "MongoDB, Cassandra, MariaDB, DynamoDB, Neo4j, Couchbase, SQL Server, DB2, MySQL, Elasticsearch, SQLite, Redis, Firebase, PostgreSQL, Hadoop, Azure, TensorFlow, Spark, PyTorch, AWS, Power BI, Scala, Keras, Word, SAS, Excel, Tableau, Redshift, NoSQL, Terraform, Kotlin, Swift, Drupal, VMware, CouchDB, DataRobot, MLR, Snowflake, Theano, Heroku, Airflow, Java, Colocation, OpenStack, Erlang, NLTK, Perl, Zoom, OpenCV, Ansible, Puppet, Elixir, Splunk, Aurora, Docker, CodeCov, Angular.js, RShiny, Tidyverse, Kubernetes, RingCentral, Wire, CSS, Play Framework, Airtable, Pulumi, Yarn, Python, GCP, React.js, Express, Matplotlib, macOS, Fastify, GDPR, PHP, Dlib, DataBricks, Django, Unreal, Clojure, Groovy, Flask, IBM Cloud, Seaborn, Jenkins, Linux, Confluence, Jupyter, Unity, GitHub, Twilio, Julia, Laravel, C#, Selenium, C++, CentOS, R, jQuery, SUSE, MATLAB, Flow, PySpark, RedHat, Qlik, Nuix, Bash, Bitbucket, Spring, Unify, SQL, Plotly, Phoenix, T-SQL, PowerShell, JavaScript, Git, Unix, Flutter, Jira, HTML, Mattermost, Chef, GitLab, SVN, ASP.NET Core, SSIS, Xamarin, Sass, NumPy, Scikit-learn, ggplot2, Pandas, Oracle, React, Objective-C, Alteryx, Cognos, DAX, Assembly, SSRS, Visio, Microsoft, WebEx, Ionic, Symfony, Dart, Nuxt.js, CodeCommit, Digital Ocean, Spreadsheet, MicroStrategy, Google Sheets, Microsoft Teams, R IDE, Google Data Studio, QlikView, Looker, Sisense, Domo, TIBCO Spotfire, Superset, Zoho, Chartio, Mode Analytics, Datawrapper, Klipfolio, SPSS, Stata, KNIME, RapidMiner, Hive, Pig, NiFi, Flink, Sqoop, BigQuery, Data Factory, Informatica, Presto, Data Integrator, Kafka Connect, Redash, DBeaver, Google Cloud, Prometheus, Grafana, Packer, HashiCorp Vault, Istio, Lucidchart, Draw.io, Enterprise Architect, Archi, Postman, Swagger, MuleSoft, IBM, Red Hat Fuse, NGINX, HAProxy, F5 BIG-IP, ServiceNow, ELK Stack, Slack, RStudio, Anaconda, IBM Watson, Colab, H2O.ai, Weka, BigML, MXNet, Caffe, ONNX, MLflow, Kubeflow, TensorBoard, SageMaker, Google AI, DVC, CUDA, cuDNN, SciPy, XGBoost, LightGBM, CatBoost"
    - Must be mentioned in the job post
    - Must belong to the skill list
    - Separated by commas
    - If not found, output "NaN"
    - Save the extracted list as: "keywords"

    Step 16: extract the status of the job if it is reposted
    - job reposted usually has: Reposted *time* hours ago
    - output "yes" if job reposted, "no" if job is not reposted
    - Save as: "reposted"
    
    Step 17: extract the minimum year of experience required
    - output a numerical number
    - must be an interger number and less than 20
    - If not found, make the best guess from the job post, otherwise, output "NaN"
    - Save as: "min_year_experience"
    
    Step 18: extract the time the job posted or reposted
    - output the time in number of hour only (EX: 2 hours ago -> 2, 14 hours ago -> 14)
    - if the less then 1 hour an in minutes (ex: 50 minutues), convert it to 1
    - This field can not be empty
    - This field mut be an interger number less than 24
    - If not found, make the best guess from the job post, otherwise, output "NaN"
    - Save as: "hour_posted"
    
    Step 19: Combine all the values into one CSV row, separated by commas and each wrapped in double quotes like this:
    "company_name","industry","job_title","city","state","employment_type","seniority_level","min_salary","max_salary","salary_type","applicant_count","job_link","job_type","requirements","keywords","reposted","min_year_experience","hour_posted"

    Step 20: Output one line per job post.
    - Do not include anything else but the data
    - Each line must contain exactly 17 commas (18 values).
    - Do not include any quotes, formatting, value titles(like company_name, job_title) or bullet points outside of the CSV lines such as (```csv,())
    - Each line is a job post in csv, do not include anything beside that

    Here are 3 lines examples of the output"
    
    "TikTok","Technology and IT","Senior Machine Learning Engineer, TikTok Ads Core Global - Traffic & Strategy","San Jose","CA","Full time","Senior level","187040","280000","yearly","17","https://www.linkedin.com/jobs/view/4193267801","onsite","Develop, refine and optimize ML/DL models to improve CTR, CVR, and ROI predictions, ensuring scalability and robustness in large-scale global deployments. Establish scalable system frameworks and performance benchmarks that continuously improve delivery efficiency while supporting the unique needs of various vertical businesses. Understand ads platform objectives and take full advantage of modern machine learning to improve ads quality, relevancy, and select the best ads formats delivered to end-users.","MongoDB, Cassandra, MariaDB, DynamoDB, Neo4j, Couchbase, SQL Server, DB2, MySQL, Elasticsearch, SQLite, Redis, Firebase, PostgreSQL, Hadoop, Azure, TensorFlow, Spark, PyTorch, AWS, Power BI, Scala, Keras, Word, SAS, Excel, Tableau, Redshift, NoSQL, Terraform, Kotlin, Swift, Drupal, VMware, CouchDB, DataRobot, MLR, Snowflake, Theano, Heroku, Airflow, Java, Colocation, OpenStack, Erlang, NLTK, Perl, Zoom, OpenCV, Ansible, Puppet, Elixir, Splunk, Aurora, Docker, CodeCov, Angular.js, RShiny, Tidyverse, Kubernetes, RingCentral, Wire, CSS, Play Framework, Airtable, Pulumi, Yarn, Python, GCP, React.js, Express, Matplotlib, macOS, Fastify, GDPR, PHP, Dlib, DataBricks, Django, Unreal, Clojure, Groovy, Flask, IBM Cloud, Seaborn, Jenkins, Linux, Confluence, Jupyter, Unity, GitHub, Twilio, Julia, Laravel, C#, Selenium, C++, CentOS, R, jQuery, SUSE, MATLAB, Flow, PySpark, RedHat, Qlik, Nuix, Bash, Bitbucket, Spring, Unify, SQL, Plotly, Phoenix, T-SQL, PowerShell, JavaScript, Git, Unix, Flutter, Jira, HTML, Mattermost, Chef, GitLab, SVN, ASP.NET Core, SSIS, Xamarin, Sass, NumPy, Scikit-learn, ggplot2, Pandas, Oracle, React, Objective-C, Alteryx, Cognos, DAX, Assembly, SSRS, Visio, Microsoft, WebEx, Ionic, Symfony, Dart, Nuxt.js, CodeCommit, Digital Ocean, Spreadsheet, MicroStrategy, Google Sheets, Microsoft Teams, R IDE, Google Data Studio, QlikView, Looker, Sisense, Domo, TIBCO Spotfire, Superset, Zoho, Chartio, Mode Analytics, Datawrapper, Klipfolio, SPSS, Stata, KNIME, RapidMiner, Talend, Platforms, Hive, Pig, NiFi, Flink, Sqoop, BigQuery, Data Factory, Informatica, Presto, Data Integrator, Kafka Connect, Redash, DBeaver, Google Cloud, Prometheus, Grafana, Packer, HashiCorp Vault, Istio, Lucidchart, Draw.io, Enterprise Architect, Archi, Postman, Swagger, MuleSoft, IBM, Red Hat Fuse, NGINX, HAProxy, F5 BIG-IP, ServiceNow, ELK Stack, Slack, RStudio, Anaconda, IBM Watson, Colab, H2O.ai, Weka, BigML, MXNet, Caffe, ONNX, MLflow, Kubeflow, TensorBoard, SageMaker, Google AI, DVC, CUDA, cuDNN, SciPy, XGBoost, LightGBM, CatBoost","no","5","3"
    "Walmart","Retail and Wholesale Trade","Software Engineer III, Machine Learning Engineer","Sunnyvale","CA","Full time","Mid level","117000","234000","yearly","100","https://www.linkedin.com/jobs/view/4094911348","onsite","Execute a roadmap for engagement and bid recommendation modeling, balancing innovative modeling approaches with business objectives. Build Walmart-scale optimizations to improve advertiser outcomes using cutting-edge techniques in the industry. Support the Model development lifecycle from ideation to deployment, ensuring high standards of ML performance and robustness.","Python, Nodejs, TensorFlow, PyTorch","yes","2","7"
    "Walgreens","Healthcare","Senior Machine Learning Engineer I","Deerfield","IL","Full time","Senior level","127500","204000","yearly","100","https://www.linkedin.com/jobs/view/4093521112","onsite","Develops software that processes, stores and serves data and machine learning models for use by others. Develops large scale data structures and pipelines to organize, collect and standardize data that helps generate insights and intelligence to support business needs. Writes ETL processes, designs data stores and develops tools for real-time and offline analytic processing on premise or on cloud infrastructure.","Python, SQL","yes","4","10"
    
    Here is the job post to analyze:
    {input_string}
    """
    return prompt1


