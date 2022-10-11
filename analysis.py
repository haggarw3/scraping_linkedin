import json
import time
import os
import pandas as pd
import re
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, ConceptsOptions, CategoriesOptions, EntitiesOptions
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# nltk.download('stopwords')
nltk.data.path.append('/Users/himanshuaggarwal/PycharmProjects/pythonProject/nltk_data')


def ibm_keywords_generator():  # Here we use the IBM NLP/ AI to get the keywords from the descriptions
    authenticator = IAMAuthenticator('vAP-M01COhN26DY-_BX6p_8CiF3-9HE89_Omiydl5ABX')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-03-25',
        authenticator=authenticator)

    raw_data = pd.read_csv('Clean_aggregated_data.csv')
    print(raw_data['positions_segments'].value_counts())
    # da = raw_data[raw_data['positions_segments'] == 'data analyst']
    # print('da', da.shape)
    # ba = raw_data[raw_data['positions_segments'] == 'BI/business analyst']
    # print('ba', ba.shape)
    # de = raw_data[raw_data['positions_segments'] == 'data engineer']
    # print('de', de.shape)
    # ds = raw_data[raw_data['positions_segments'] == 'data scientist']
    # print('ds', ds.shape)
    # pydev = raw_data[raw_data['positions_segments'] == 'python developer']
    # print('pydev', pydev.shape)
    # cloud = raw_data[raw_data['positions_segments'] == 'cloud engineer']
    # print('cloud:', cloud.shape)

    # natural_language_understanding.set_service_url('https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/018787a2-0cbb-438e-add2-290b6f1f0158')
    #
    # df = pd.DataFrame()
    # counter = 1
    # for description in raw_data['descriptions']:
    #     response = natural_language_understanding.analyze(
    #         text=description,
    #         features=Features(
    #             entities=EntitiesOptions(emotion=True, sentiment=True, limit=None),
    #             keywords=KeywordsOptions(emotion=True, sentiment=True, limit=20),
    #             concepts=ConceptsOptions(limit=10),
    #             categories=CategoriesOptions(limit=1))).get_result()
    #     chars = response['usage']['text_characters']
    #     keywords = [item['text'] for item in response['keywords']]
    #     concepts = [item['text'] for item in response['concepts']]
    #     concepts = response['categories'][0]['label'].strip()
    #     temp_list = [chars, keywords, concepts, concepts]
    #     temp_df = pd.DataFrame(temp_list).T
    #     df = pd.concat([df, temp_df], axis=0)
    #     print(counter)
    #     counter += 1
    #     if counter % 60 == 0:
    #         df.to_csv('File'+str(counter)+'.csv')
    #         df = pd.DataFrame()
    #         authenticator = IAMAuthenticator('vAP-M01COhN26DY-_BX6p_8CiF3-9HE89_Omiydl5ABX')
    #         natural_language_understanding = NaturalLanguageUnderstandingV1(
    #             version='2021-03-25',
    #             authenticator=authenticator)
    #         natural_language_understanding.set_service_url(
    #             'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/018787a2-0cbb-438e-add2-290b6f1f0158')
    #         time.sleep(5)
    #     if counter == raw_data.shape[0]+1:
    #         df.to_csv('File' + str(counter) + '.csv')

    nlp_df = pd.DataFrame(columns=['characters', 'keywords', 'concepts', 'concepts_'])
    all_files = os.listdir()
    nlp_files = [file for file in all_files if (file.endswith('.csv')) and ('File' in file)]
    nums = list(map(lambda x__: int(re.findall('\d+', x__)[0]), nlp_files))
    nums.sort(reverse=False)
    for num in nums:
        file = 'File'+str(num)+'.csv'
        x = pd.read_csv(file)
        x = x.drop(['Unnamed: 0'], axis=1)
        x.columns = nlp_df.columns
        nlp_df = pd.concat([nlp_df, x], axis=0)
    nlp_df = nlp_df.drop(['concepts_'], axis=1)
    nlp_df = nlp_df.reset_index(drop=True)
    nlp_df = pd.concat([raw_data, nlp_df], axis=1)
    nlp_df = nlp_df.drop(['characters'], axis=1)
    nlp_df.to_csv('NLP_aggregated.csv')


# Skills for all job types

raw_data = pd.read_csv('Clean_aggregated_data.csv')
skills_unigrams = ['SQL', 'database', 'Excel', 'R', 'Python', 'NoSQL',
          'JavaScript', 'Java', 'C', 'Bash', 'TensorFlow', 'Keras', 'Pandas', 'Numpy',
          'Kafka', 'django', 'Jupyter', 'statistic', 'regression', 'bayesian',
          'A/B', 'classification', 'Tableau', 'PowerBI', 'macros',
          'Qlik', 'Looker', 'excel', 'ETL', 'Cleaning', 'wrangling', 'Knime',
          'Scikit', 'sklearn', 'Spark', 'Hadoop', 'Redshift', 'Scala', 'AWS', 'Ansible', 'Docker',
          'Kubernetes', 'Chef', 'Puppet', 'powerpoint', 'reporting', 'storytelling',
          'agile', 'scrum', 'azure', 'outlook', 'gcp', 'ssis', 'ssrs', 'mongoDB',
                   'ORC', 'parquet', 'Cassandra', 'json', 'informatica', 'pig', 'hive', 's3',
                   'Athena', 'html', 'git', 'pyspark', 'autoML']
skills_bigrams = ['structured data', 'unstructured data', 'relational database',
                  'Critical Thinking', 'Writing Skill', 'shell scripting', 'communication skill',
          'fast learner', 'problem solving', 'user centered', 'positive attitude', 'data modeling',
                  'hypothesis testing', 'Inferential statistics', 'Data Studio', 'pivot table',
                  'sql server', 'big query']
skills_trigrams = ['non relational database']

skills_unigrams = [item.lower() for item in skills_unigrams]
skills_bigrams = [item.lower() for item in skills_bigrams]
skills_trigrams = [item.lower() for item in skills_trigrams]

nlp_df = pd.read_csv('NLP_aggregated.csv')


def skill_counter(data):
    skill_counts = {}
    for skill in skills_unigrams:
        counter_skill = 0
        for description in data['descriptions']:
            description = description.lower().strip().replace('-', ' ').replace('/', ' ')
            if skill == 'r':
                if len(re.findall(' r ', description)) > 0:
                    counter_skill += 1
            elif skill == 'java':
                if len(re.findall('java ', description)) > 0:
                    counter_skill += 1
            elif skill == 'c':
                if len(re.findall(' c ', description)) > 0:
                    counter_skill += 1
            elif skill == 'orc':
                if len(re.findall(' orc ', description)) > 0:
                    counter_skill += 1
            elif skill == 'a/b':
                if (len(re.findall(' ab ', description)) > 0) or (len(re.findall(' a b ', description)) > 0):
                    counter_skill += 1
            elif skill == 'powerbi':
                if ('powerbi' in description) or ('power bi' in description):
                    counter_skill += 1
            elif skill == 'gcp':
                if ('gcp' in description) or ('google cloud platform' in description):
                    counter_skill += 1
            elif skill == 'automl':
                if ('automl' in description) or ('auto ml' in description):
                    counter_skill += 1
            elif skill in description:
                counter_skill += 1
        skill_counts[skill] = counter_skill

    for skill in skills_bigrams:
        counter_skill = 0
        for description in data['descriptions']:
            description = description.lower().replace('-', ' ')
            bigrams = list(ngrams(word_tokenize(description), 2))
            bigrams_joined = [' '.join(item).strip() for item in bigrams]
            if skill in bigrams_joined:
                counter_skill += 1
        skill_counts[skill] = counter_skill

    print(skill_counts)
    result = {}
    for key, value in skill_counts.items():
        if value != 0:
            result[key] = value
    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    result = {}
    for item in sorted_result:
        result[item[0]] = item[1]
    return result

# over_skill_counts = skill_counter(raw_data)
# df = pd.DataFrame(over_skill_counts.items(), columns=['skills', 'job counts'])
# df = df.sort_values(by=['job counts'], ascending=False)
# df.to_csv('Skills vs Number of Job Postings.csv')

## -------------------------------------------------
## skills per job type
## -------------------------------------------------

skills_per_position_segment = {}
for position_segment in raw_data['positions_segments'].value_counts().index:
    data_position_segment = raw_data[raw_data['positions_segments'] == position_segment]
    skills_per_position_segment[position_segment] = skill_counter(data_position_segment)



print(skills_per_position_segment)
df = pd.DataFrame(skills_per_position_segment.items())
df.columns = ['Position', 'Skills']
df.to_csv('skills per position segment.csv')
print(df)
























# def skill_segment(x):
#     if x in ['sql', 'excel', 'relational database']:
#         return 'Database'
#     elif x in []:
#         return 'Programming'

print(raw_data.shape)

