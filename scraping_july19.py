from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
import pandas as pd
import time
# import os

driver = webdriver.Firefox(executable_path='/Users/himanshuaggarwal/PycharmProjects/pythonProject/geckodriver')
driver.maximize_window()

jobs = ['data analysis', 'data analyst', 'data analysis junior', 'business analyst', 'junior analyst',
        'data science junior']

# for each job define the function to scrape
driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
driver.find_element_by_id('username').send_keys(Keys.COMMAND + "a")
driver.find_element_by_id('username').send_keys(Keys.DELETE)
time.sleep(2)
driver.find_elements_by_id('username')[0].send_keys('himanshu.aggarwal@ironhack.com')
time.sleep(3)
# print("username successful")
driver.find_element_by_id('password').send_keys(Keys.COMMAND + "a")
driver.find_element_by_id('password').send_keys(Keys.DELETE)
time.sleep(2)
driver.find_elements_by_id('password')[0].send_keys('Himagga11!')
time.sleep(4)
# print('password successful')
driver.find_element_by_class_name('login__form_action_container').click()
time.sleep(2)
driver.find_element_by_class_name('btn__primary--large').click()
# print("entered Home page")
driver.find_element_by_id('ember24').click()
time.sleep(2)
driver.find_element_by_class_name('jobs-search-box__inner').click()
time.sleep(2)
driver.switch_to.active_element.send_keys('data analyst')
time.sleep(2)
driver.switch_to.active_element.send_keys(Keys.TAB)
time.sleep(2)
driver.switch_to.active_element.send_keys('Madrid')
time.sleep(3)
driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)
time.sleep(2)
driver.switch_to.active_element.send_keys(Keys.ENTER)
time.sleep(2)
# CLICK ON THE Experience Level drop down
driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
# this index 1 is for the second element on the page that has a down arrow (in the
# group of date posted, experience level, company, job type)
time.sleep(2)
# Selecting Entry Level Jobs
driver.find_elements_by_class_name('search-reusables__value-label')[5].click()
time.sleep(2)
driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
time.sleep(2)
driver.find_element_by_css_selector('.msg-overlay-bubble-header__details').click()
time.sleep(2)
page1_url = driver.current_url

# This is for storing all the scraped data
jobs_card_data = {}
df = pd.DataFrame(columns=['company_name', 'position', 'location', 'date_posted', 'Number of applicants', 'number of views', 'job_type', 'employees', 'sector', 'descriptions', 'job_functions', 'industry'])

# To find the max number of pages after the filter
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
time.sleep(2)
max_pages = soup.find_all('button', {'aria-label': re.compile('Page*')})[-1].text
max_pages = re.findall('\d+', max_pages)[0]
max_pages = int(max_pages)
print("maximum pages for this search: ", max_pages)

# Incremental increase for each job posting - Will be used the key for each key value pairs in job_cards_data
counter = 1

page = 1
while page < max_pages:  # scraping through all the pages

    # number of job cards in a page
    iterations_per_page = len(soup.find_all('li', {'class': re.compile('jobs-search-results*')}))

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    job_cards = soup.find_all('li', {'class': re.compile('jobs-search-results*')})

    # Now for each job card , we will start scraping the data
    for i in range(iterations_per_page):
        job_card = job_cards[i]
        # Finding the ember ID to be able to click on it
        emberID = job_card.attrs['id']
        driver.find_element_by_id(emberID).click()
        time.sleep(1)

        # To scroll view so that the job card is on the top of the screen
        element = driver.find_element_by_id(emberID)
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(4)

        html_2 = driver.page_source
        soup_2 = BeautifulSoup(html_2, 'lxml')
        right_rail_soup = soup_2.find('section', {'class': 'jobs-search__right-rail'})

        # Job position
        try:
            position = right_rail_soup.find('h2', {'class': 'jobs-details-top-card__job-title t-20 t-black t-normal'}).text
            position = re.findall('\w+', position)
            position = " ".join(position)
        except (AttributeError, IndexError):
            position = ''

        # company Name
        try:
            company_name = right_rail_soup.find('a', {'class': 'jobs-details-top-card__company-url t-black--light t-normal ember-view'}).text
            company_name = re.findall('\w+', company_name)
            company_name = " ".join(company_name)
        except (AttributeError, IndexError):
            company_name = ''

        # location
        try:
            location = right_rail_soup.find_all('span', {'class': 'jobs-details-top-card__bullet'})[0].text.strip()
        except (AttributeError, IndexError):
            location = ''

        # Date posted
        try:
            span_texts = []
            for span in right_rail_soup.find_all('span'):
                if not span.attrs.values():
                    span_texts.append(span.text)
            date_posted_list = span_texts[0].split('\n')
            date_posted = ''
            for item in date_posted_list:
                if 'ago' in item:
                    date_posted = item
            if date_posted != '':
                date_posted = date_posted.strip()
        except (AttributeError, IndexError):
            date_posted = 'NA'

        # Number of views of the job posting
        try:
            views = right_rail_soup.findAll('span', {'class': re.compile('jobs-details*')})[1].text
            views = re.findall('\w+', views)
            views = " ".join(views)
        except (AttributeError, IndexError):
            views = ''

        try:
            job_details = right_rail_soup.find_all('span', {'class': 'jobs-details-job-summary__text--ellipsis'})
            # Number of applicants
            applicants = job_details[0].text
            applicants = re.findall('\w+', applicants)
            applicants = " ".join(applicants)
        except (AttributeError, IndexError):
            applicants = ''

            # job type - Entry level or senior level etc
        try:
            job_type = job_details[1].text
            job_type = re.findall('\w+', job_type)
            job_type = " ".join(job_type)
        except (AttributeError, IndexError):
            job_type = ''

            # Company Details: Number of employees
        try:
            employees = job_details[2].text
            employees = re.findall('\S+', employees)
            employees = " ".join(employees)
        except (AttributeError, IndexError):
            employees = ''

            # Company Details: Sector
        try:
            sector = job_details[3].text
            sector = re.findall('\S+', sector)
            sector = " ".join(sector)
        except (AttributeError, IndexError):
            sector = ''

            # Job posting details
        try:
            descriptions = right_rail_soup.find('div', {'id': 'job-details'}).find('span').text
            descriptions = re.findall('\w+', descriptions)
            descriptions = " ".join(descriptions)
        except (AttributeError, IndexError):
            descriptions = ''

        # To get the other details like seniority level, industry, and job functions
        try:
            other_details = right_rail_soup.find('div', {'class': 'jobs-description-details pt4'})
            industry = other_details.find_all('li', {'class': 'jobs-description-details__list-item t-14'})[
                0].text
            industry = re.findall('\w+', industry)
            industry = " ".join(industry)

            job_functions = \
                other_details.find_all('li', {'class': 'jobs-description-details__list-item t-14'})[1].text
            job_functions = re.findall('\w+', job_functions)
            job_functions = " ".join(job_functions)
        except (AttributeError, IndexError):
            industry = ''
            job_functions = ''
            print('\n')

        jobs_card_data[counter] = [company_name, position, location, date_posted, applicants, views, job_type, employees,
                                   sector, descriptions, job_functions, industry]
        temp = pd.DataFrame({counter: jobs_card_data[counter]}).T
        df = pd.concat([temp, df])
        df.to_csv('test_scrape.csv')

        print(jobs_card_data[counter])

        # Now we increment the counter at
        # the end
        counter += 1

    if page == 1:
        new_url = page1_url + "&start=25"
    else:
        new_url = page1_url + "&start=" + str(page * 25)

    page += 1
    driver.get(new_url)
    time.sleep(3)

data = pd.DataFrame(jobs_card_data).T
data.columns = ['company_name', 'position', 'location', 'date_posted', 'Number of applicants', 'number of views', 'job_type', 'employees', 'sector', 'descriptions', 'job_functions', 'industry']
data = data.reset_index()

data.to_csv('test_scrape_final.csv')

