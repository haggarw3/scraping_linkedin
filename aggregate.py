import pandas as pd
import os
import re
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, ConceptsOptions, \
    CategoriesOptions
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

dir_web_dev = '/Users/himanshuaggarwal/PycharmProjects/pythonProject/web_dev/csv_webDEVs'
all_files = os.listdir(dir_web_dev)
df = pd.DataFrame(columns=['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                           'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                           'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                           'Hiring Trend Company Wide-Engineering', 'Median Tenure'])
for file in all_files:
    if file.endswith('.csv'):
        temp = pd.read_csv(dir_web_dev + '/' + file)
        temp = temp.drop('Unnamed: 0', axis=1)
        print(file)
        if len(temp.columns) > 20:
            print(file)
            temp = temp[['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']]
            temp.columns = ['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                            'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                            'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                            'Hiring Trend Company Wide-Engineering', 'Median Tenure']
            temp = temp.reset_index(drop=True)
        elif 'search_keyword' in temp.columns:
            temp = temp.drop('search_keyword', axis=1)
        if len(df.columns) == len(temp.columns):
            df = pd.concat([df, temp])

df = df.reset_index(drop=True)
print(df.shape)

# Removing nulls
df = df.dropna(subset=['company_name', 'position', 'location', 'descriptions'])

# Removing duplicates
df = df.drop_duplicates()


# Standardize text data in the columns
def standardize_col(df_temp, col):
    df_temp[col] = df_temp[col].apply(lambda x: x if pd.isna(x) else x.lower())
    return df_temp[col]


df['company_name'] = standardize_col(df, 'company_name')
df['position'] = standardize_col(df, 'position')
df['location'] = standardize_col(df, 'location')
df['full-time/part-time'] = standardize_col(df, 'full-time/part-time')
df['seniority level'] = standardize_col(df, 'seniority level')
df['descriptions'] = standardize_col(df, 'descriptions')


# Removing job positions which are not relevant to web dev positions
# Filtering out the rows in the dataframe where the sector is in remove_jobs_list
def clean_position(x):
    for item in ['product owner', 'ios', 'android', 'data', 'tech lead', 'c backend',
                 'scala', 'linux', 'liferay', 'ui', 'ux', 'scrum', 'iot', 'design']:
        if item in x:
            return "TO BE REMOVED"
    return x


df['position'] = list(map(clean_position, df['position']))
df = df[df['position'] != 'TO BE REMOVED']
df = df.reset_index(drop=True)
print(df.shape)
df.to_csv('Web Dev AGGREGATED.csv')

top_skills = []
for row_content in df['top competitive skills']:
    row_content = row_content.replace('/', ' ').replace('-', ' ')
    if len(row_content) > 10:
        try:
            for item in re.findall('\w+ \w+ \w+', row_content):  # Skills with 3 words
                top_skills.append(item)
            for item in re.findall('\w+ \w+', row_content):  # Skills with 2 words
                top_skills.append(item)
            for item in re.findall('\'\w+\'', row_content):  # Skill with single word
                top_skills.append(re.findall('\w+', item)[0])
        except TypeError:
            pass

top_skills = pd.DataFrame(pd.Series(top_skills).value_counts()).reset_index()
top_skills.columns = ['Skill', 'Count']
print(top_skills.head())
top_skills.to_csv('Web_dev_TOP_SKILLS.csv')


def ibm_keywords_generator(data):  # Here we use the IBM NLP/ AI to get the keywords from the descriptions
    authenticator = IAMAuthenticator('vAP-M01COhN26DY-_BX6p_8CiF3-9HE89_Omiydl5ABX')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-03-25',
        authenticator=authenticator)
    natural_language_understanding.set_service_url('https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/018787a2-0cbb-438e-add2-290b6f1f0158')
    ibm_df = pd.DataFrame()
    counter = 0
    try:
        for description in data['descriptions']:
            response = natural_language_understanding.analyze(
                text=description,
                features=Features(
                    entities=EntitiesOptions(emotion=True, sentiment=True, limit=None),
                    keywords=KeywordsOptions(emotion=True, sentiment=True, limit=20),
                    concepts=ConceptsOptions(limit=10),
                    categories=CategoriesOptions(limit=1))).get_result()
            chars = response['usage']['text_characters']
            keywords = [item_keywords['text'] for item_keywords in response['keywords']]
            concepts = [item_keywords['text'] for item_keywords in response['concepts']]
            categories = response['categories'][0]['label'].strip()
            temp_list = [data['company_name'][0], data['position'][0], data['location'][0], chars,
                         keywords, concepts, categories, data['top competitive skills'][0],
                         data['industry'][0]]
            temp_df = pd.DataFrame(temp_list).T
            ibm_df = pd.concat([ibm_df, temp_df], axis=0)
            ibm_df.reset_index(drop=True, inplace=True)
            print(counter)
            counter += 1
            if counter % 60 == 0:
                authenticator = IAMAuthenticator('vAP-M01COhN26DY-_BX6p_8CiF3-9HE89_Omiydl5ABX')
                natural_language_understanding = NaturalLanguageUnderstandingV1(
                    version='2021-03-25',
                    authenticator=authenticator)
                natural_language_understanding.set_service_url(
                    'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/018787a2-0cbb-438e'
                    '-add2-290b6f1f0158')
                time.sleep(2)
    except Exception as e:
        print(e)
        return ibm_df
    ibm_df.columns = ['company_name', 'position', 'location', C'Top Competitive Skills',
                      'industry']
    return ibm_df


ibm_watson_df = ibm_keywords_generator(df)
ibm_watson_df.to_csv('WebDev_IBM_Watson.csv')
print(ibm_watson_df.head())
print(all_files)
