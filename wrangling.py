import pandas as pd
import numpy as np
import os
import re
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

all_files = os.listdir('/Users/himanshuaggarwal/Downloads/scraped_content_raw_data')
data_files = []
for file in all_files:
    if (file.endswith('.csv')) or (file.endswith('.xlsx')):
        data_files.append(file)

raw_data = pd.DataFrame()
for file in data_files:
    # print(file)
    current_path = '/Users/himanshuaggarwal/Downloads/scraped_content_raw_data/' + file
    try:
        temp = pd.read_csv(current_path)
    except UnicodeDecodeError:
        temp = pd.read_excel(current_path)
    raw_data = pd.concat([raw_data, temp], axis=0)
    raw_data = raw_data.reset_index(drop=True)
    # print(raw_data['Number of applicants'][0])

raw_data.columns = [column.lower() for column in raw_data.columns]
raw_data = raw_data.drop(['unnamed: 0', 'index', 'search_keyword'], axis=1)

print('shape of raw aggregated data', raw_data.shape)

print('Nulls in the data frame: ', '\n', raw_data.isna().sum())
# Drop rows where company_name or position is null
raw_data = raw_data.dropna(subset=['company_name', 'position', 'sector', 'location'], axis=0)
print('VERIFY Nulls in the data frame: \n', raw_data.isna().sum())


# clean data using column job_type (current job types are entry level, mid senior level, associate, director, executive, full time, part time etc )
job_types = raw_data['job_type'].value_counts()
job_type_df = pd.DataFrame(raw_data['job_type'].value_counts()).reset_index()
remove_job_types = list(job_type_df[job_type_df['job_type'] <= 6]['index'])

# Filtering out the rows in the dataframe where the job type is in remove_job_types list
raw_data = raw_data[~raw_data['job_type'].isin(remove_job_types)]

# Cleaning the dataframe using the column sector
remove_sector = []
for item in raw_data['sector'].unique():
    if (pd.notnull(item)) and (len(item) > 100):
        remove_sector.append(item)

# Filtering out the rows in the dataframe where the sector is in remove_sector list
raw_data = raw_data[~raw_data['sector'].isin(remove_sector)]

print("Shape before removing duplicates", raw_data.shape)
# Dropping duplicates now
raw_data = raw_data.drop_duplicates(subset=['company_name', 'position', 'location', 'job_type',
                                            'sector'], keep='first')

print("Shape after removing duplicates", raw_data.shape)
raw_data = raw_data.dropna(subset=['descriptions'], axis=0)

raw_data['position'] = list(map(lambda x_: x_.lower(), raw_data['position']))
# Cleaning the dataframe using the column sector
remove_position = []
for item in raw_data['position'].unique():
    if (pd.notnull(item)) and (len(item) > 50):
        remove_position.append(item)

# Filtering out the rows in the dataframe where the sector is in remove_sector list
raw_data = raw_data[~raw_data['position'].isin(remove_position)]


def positions_segments(x):
    if ('data engineer' in x) or (('data' in x) and ('engineer' in x)) or ('oracle' in x):
        return 'data engineer'
    elif ('etl' in x) or ('sql' in x) or ('qa' in x) or ('quality assurance ' in x):
        return 'data engineer'
    elif ('data analyst' in x) or ('data analytics' in x) or ('data lead' in x) or ('sap' in x):
        return 'data analyst'
    elif ('analytics' in x) or ('analytics engineer' in x):
        return 'data analyst'
    elif ('data scientist' in x) or ('data science' in x) or ('artificial intelligence' in x) or ('machine learning' in x):
        return 'data scientist'
    elif ('big data' in x) or ('spark' in x):
        return 'big data engineer'
    elif (('business' in x) and ('analyst' in x)) or ('business intelligence' in x) or ('bi' in x):
        return 'BI/business analyst'
    # Note: after the conditions for business analyst have been checked, then we use the next simple condition for data analysts again
    elif ('analyst' in x) or ('data' in x) or ('analista' in x) or ('powercenter' in x):
        return 'data analyst'
    elif ('business' in x) or ('intelligence' in x):
        return 'BI/business analyst'
    elif 'software' in x:
        return 'software engineer'
    elif ('front' in x) or ('back' in x) or ('stack' in x) or ('devops' in x) or ('java' in x) or ('php' in x) or ('ruby' in x):
        return 'dev ops/frontend/backend/fullstack'
    elif 'web' in x:
        return 'dev ops/frontend/backend/fullstack'
    elif 'python' in x:
        return 'python developer'
    elif ('cloud' in x) or ('azure' in x) or ('aws' in x) or ('sharepoint' in x):
        return 'cloud engineer'
    elif 'developer' in x:
        return 'dev ops/frontend/backend/fullstack'
    else:
        return 'Other'

raw_data['positions_segments'] = list(map(positions_segments, raw_data['position']))
raw_data = raw_data[~raw_data['positions_segments'].isin(['Other', 'software engineer', 'dev ops/frontend/backend/fullstack'])]
print(raw_data['positions_segments'].value_counts())

for item in raw_data['descriptions']:
    if len(item)<50:
        raw_data = raw_data[raw_data['descriptions'] != item]


def clean_date_posted(x):
    if (pd.notnull(x)) and (x != ''):
        if ('week' in x) or ('weeks' in x):
            number = re.findall('\d+', x)[0]
            return int(number)*7
        if ('day' in x) or ('days' in x):
            return int(re.findall('\d+', x)[0])
        if ('month' in x) or ('months' in x):
            number = re.findall('\d+', x)[0]
            return int(number)*30  # for simplicity we are taking it to be 30
        if ('hour' in x) or ('hours' in x):
            return 1  # posted on the same day
    else:
        return 'NA'


def clean_applicants(x):
    try:
        if (pd.notnull(x)) and (x != ''):
            return int(re.findall('\d+', x)[0])
        else:
            return 'NA'
    except Exception as e:
        # print(e)
        # print(x)
        return 'NA'


def clean_views(x):
    if ('view' in x) and (pd.notnull(x)) and (x != ''):
        try:
            x = int(re.findall('\d+', x)[0])
            return x
        except IndexError:
            return 'NA'
    elif 'applicant' in x:
        return 'NA'
    else:
        return 'NA'


def clean_employees(x):
    if (pd.notnull(x)) and (x != ''):
        if 'employees' in x:
            return x.replace('employees', '').strip()
    else:
        return 'NA'

raw_data['date_posted_days_ago'] = list(map(clean_date_posted, raw_data['date_posted']))
# print('clean_date_posted Ok')
raw_data['number of applicants'] = list(map(clean_applicants, raw_data['number of applicants']))
# print('clean_applicants Ok')
raw_data['number of views'] = list(map(clean_views, raw_data['number of views']))
# print('clean_views Ok')
raw_data['employees'] = list(map(clean_employees, raw_data['employees']))
# print('clean_employees Ok')
raw_data = raw_data.drop(['date_posted'], axis=1)


# data = raw_data[['company_name', 'position', 'location', ]]
raw_data = raw_data.reset_index(drop=True)
raw_data.to_csv('Clean_aggregated_data.csv')

print(raw_data['positions_segments'].value_counts())
da = raw_data[raw_data['positions_segments'] == 'data analyst']
print('da', da.shape)
ba = raw_data[raw_data['positions_segments'] == 'BI/business analyst']
print('ba', ba.shape)
de = raw_data[raw_data['positions_segments'] == 'data engineer']
print('de', de.shape)
ds = raw_data[raw_data['positions_segments'] == 'data scientist']
print('ds', ds.shape)
pydev = raw_data[raw_data['positions_segments'] == 'python developer']
print('pydev', pydev.shape)
cloud = raw_data[raw_data['positions_segments'] == 'cloud engineer']
print('cloud:', cloud.shape)


print(raw_data.head(2))

# print(raw_data.columns)
