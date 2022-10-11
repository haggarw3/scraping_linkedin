import logIn
import scraper
# import wrangling
import pandas as pd
import time
import os
# 'business analyst', 'data scientist', 'junior analyst',
# 'business intelligence analyst', 'data scientist', 'business intelligence analyst',
# 'sql developer', 'sql dba', 'data engineer','data analyst'
# 'python developers', 'data quality'
scraping_keywords = ['data analyst', 'sql developer', 'business intelligence']
locations = ['barcelona']
scraped_df = pd.DataFrame(
    columns=['company_name', 'position', 'location', 'date_posted', 'Number of applicants', 'number of views',
             'job_type', 'employees', 'sector', 'descriptions', 'search_keyword'])

# Removing all the old data files / csv files
files = os.listdir()
for file in files:
    if file.endswith('.csv'):
        os.remove(file)

# driver, home_url = logIn.login()  # Later, will send masked credentials to the function instead of hard coding
for location in locations:
    for keyword in scraping_keywords:
        try:
            driver, home_url = logIn.login()
            driver, url = scraper.scrape_phase1(driver, home_url, location, keyword)
            if url == home_url:
                break
        except Exception as e:
            print(e)
        try:
            data = scraper.scrape_phase2(driver, url, keyword, location)
            scraped_df = pd.concat([scraped_df, data])
        except Exception as e:
            print(e)
            print('Errored in scrape phase 2')
        time.sleep(10)


scraped_df.to_csv('final_scrape.csv')


