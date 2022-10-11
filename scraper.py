from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
import re


# This functions takes to the first page for scraping
def scrape_phase1(driver, home_url, location, keyword):
    trial_counter = 0
    while trial_counter < 3:
        driver.get(home_url)
        time.sleep(2)
        driver.find_element_by_class_name('jobs-search-box__inner').click()
        time.sleep(4)
        driver.switch_to.active_element.send_keys(keyword)
        time.sleep(2)
        # driver.find_element_by_class_name('jobs-search-box__inner').click()
        driver.switch_to.active_element.send_keys(Keys.TAB)
        time.sleep(2)
        driver.switch_to.active_element.send_keys(location)
        time.sleep(2)
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(4)
        if ("keywords" in driver.current_url) and ("location" in driver.current_url):
            # # CLICK ON THE Experience Level drop down
            # driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
            # # this index 1 is for the second element on the page that has a down arrow (in the
            # # group of date posted, experience level, company, job type)
            # time.sleep(2)
            # # Selecting Entry Level Jobs
            # driver.find_elements_by_class_name('search-reusables__value-label')[5].click()
            # time.sleep(2)
            # driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
            # time.sleep(2)
            driver.find_element_by_css_selector('.msg-overlay-bubble-header__details').click()
            time.sleep(2)
            return driver, driver.current_url
        else:
            trial_counter += 1

    raise AttributeError("Scrape 1 errored")
    return


def scrape_phase2(driver, url, keyword, location):
    page1_url = url
    # This is for storing all the scraped data
    jobs_card_data = {}
    df = pd.DataFrame(columns=['company_name', 'position', 'location', 'date_posted', 'Number of applicants', 'number of views',
                 'job_type', 'employees', 'sector', 'descriptions', 'job_functions', 'industry'])

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
    while page <= max_pages:  # scraping through all the pages
        time.sleep(4)
        # number of job cards in a page
        try:
            iterations_per_page = len(soup.find_all('li', {'class': re.compile('jobs-search-results*')}))
        except AttributeError:
            print('Page did not load properly')
            try:
                driver.refresh()
            except AttributeError:
                data = pd.DataFrame(jobs_card_data).T
                data.columns = ['company_name', 'position', 'location', 'date_posted', 'Number of applicants',
                                'number of views',
                                'job_type', 'employees', 'sector', 'descriptions', 'job_functions', 'industry']
                data = data.reset_index()
                data['search_keyword'] = keyword
                file = keyword + '.csv'
                data.to_csv(file)

                return data

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        job_cards = soup.find_all('li', {'class': re.compile('jobs-search-results*')})

        # Now for each job card , we will start scraping the data
        for i in range(iterations_per_page):
            try:
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
            except (AttributeError, IndexError):
                print('Page not loaded')

            # Job position
            try:
                position = right_rail_soup.find('h2', {'class': 'jobs-details-top-card__job-title t-20 t-black t-normal'}).text
                position = re.findall('\w+', position)
                position = " ".join(position)
            except AttributeError:
                position = ''
            if position == '':
                try:
                    position = right_rail_soup.find('h2', {'class': 't-24 t-bold'}).text
                    position = re.findall('\w+', position)
                    position = " ".join(position)
                except (AttributeError, IndexError):
                    position = ''
            time.sleep(1)

            # company Name
            try:
                company_name = right_rail_soup.find('a', {
                    'class': 'jobs-details-top-card__company-url t-black--light t-normal ember-view'}).text
                company_name = re.findall('\w+', company_name)
                company_name = " ".join(company_name)
            except (AttributeError, IndexError):
                company_name = ''
            if company_name == '':
                try:
                    company_name = right_rail_soup.find('a', {
                        'class': 'ember-view t-black t-normal'}).text.strip()
                except (AttributeError, IndexError):
                    company_name = ''

            time.sleep(1)
            # location
            try:
                location = right_rail_soup.find_all('span', {'class': 'jobs-details-top-card__bullet'})[0].text.strip()
            except (AttributeError, IndexError):
                location = ''
            if location == '':
                try:
                    location = right_rail_soup.find_all('span', {'class': 'jobs-unified-top-card__bullet'})[
                        0].text.strip()
                except (AttributeError, IndexError):
                    location = ''

            time.sleep(1)
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
                date_posted = ''
            if date_posted == '':
                try:
                    date_posted = right_rail_soup.find('span', {'class': 'jobs-unified-top-card__posted-date jobs-unified-top-card__posted-date--new t-bold'}).strip()
                except AttributeError:
                    date_posted = ''

            time.sleep(1)
            # Number of views of the job posting
            try:
                views = right_rail_soup.findAll('span', {'class': re.compile('jobs-details*')})[1].text
                views = re.findall('\w+', views)
                views = " ".join(views)
            except (AttributeError, IndexError):
                views = ''

            time.sleep(1)
            # Other job details
            try:
                job_details = right_rail_soup.find_all('span', {'class': 'jobs-details-job-summary__text--ellipsis'})
                # Number of applicants
                applicants = job_details[0].text
                applicants = re.findall('\w+', applicants)
                applicants = " ".join(applicants)
            except (AttributeError, IndexError):
                applicants = ''
            if applicants == '':
                try:
                    applicants = soup.find('span', {'class': re.compile('jobs-unified-top-card__applicant-count*')}).text.strip()
                except AttributeError:
                    applicants = ''

            time.sleep(1)
            # job type - Entry level or senior level etc
            try:
                job_type = job_details[1].text
                job_type = re.findall('\w+', job_type)
                job_type = " ".join(job_type)
            except (AttributeError, IndexError):
                job_type = ''
            if job_type == '':
                try:
                    job_type = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[0].text.strip()
                except AttributeError:
                    job_type = ''

            # Company Details: Number of employees
            try:
                employees = job_details[2].text
                employees = re.findall('\S+', employees)
                employees = " ".join(employees)
            except (AttributeError, IndexError):
                employees = ''
            if employees == '':
                try:
                    emp_industry = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[1].text.strip()
                    employees = emp_industry.split(" ")[0]
                except (AttributeError, IndexError):
                    employees = ''

            # Company Details: Sector
            try:
                sector = job_details[3].text
                sector = re.findall('\S+', sector)
                sector = " ".join(sector)
            except (AttributeError, IndexError):
                sector = ''
            if sector == '':
                try:
                    emp_industry = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[1].text.strip()
                    sector = emp_industry.split(" ")[3]
                except IndexError:
                    sector = ''

            # Job posting details
            try:
                descriptions = right_rail_soup.find('div', {'id': 'job-details'}).find('span').text
                descriptions = re.findall('\w+', descriptions)
                descriptions = " ".join(descriptions)
            except (AttributeError, IndexError):
                descriptions = ''

            # To get the other details like seniority level, industry, and job functions
            # try:
            #     other_details = right_rail_soup.find('div', {'class': 'jobs-description-details pt4'})
            #     industry = other_details.find_all('li', {'class': 'jobs-description-details__list-item t-14'})[
            #         0].text
            #     industry = re.findall('\w+', industry)
            #     industry = " ".join(industry)
            #
            #     job_functions = \
            #         other_details.find_all('li', {'class': 'jobs-description-details__list-item t-14'})[1].text
            #     job_functions = re.findall('\w+', job_functions)
            #     job_functions = " ".join(job_functions)
            # except (AttributeError, IndexError):
            #     industry = ''
            #     job_functions = ''
            #     print('\n')

            jobs_card_data[counter] = [company_name, position, location, date_posted, applicants, views, job_type,
                                       employees, sector, descriptions]
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
        time.sleep(7)

    data = pd.DataFrame(jobs_card_data).T
    data.columns = ['company_name', 'position', 'location', 'date_posted', 'Number of applicants', 'number of views',
                    'job_type', 'employees', 'sector', 'descriptions']
    data = data.reset_index()
    data['search_keyword'] = keyword
    file = keyword + " " + location + '.csv'
    data.to_csv(file)

    return data

