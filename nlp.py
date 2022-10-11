import pandas as pd
import re
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk import everygrams, word_tokenize, FreqDist
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
nltk.data.path.append('/Users/himanshuaggarwal/PycharmProjects/pythonProject/nltk_data')

# WORD CLOUD FOR EACH POSITION SEGMENT
nlp_df = pd.read_csv('NLP_aggregated.csv')
nlp_df = nlp_df.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
positions_segments = nlp_df['positions_segments'].unique()
stopwords_wordcloud = list(set(STOPWORDS))
stop_words_spanish = list(set(stopwords.words('spanish')))
stop_words = stopwords_wordcloud + stop_words_spanish
stop_words = stop_words + ['re', 'let', 'us', 'much', 'will']


keywords_per_segment = {}
description_words_per_segment = {}
for segment in positions_segments:
    segment_keywords_series = nlp_df[nlp_df['positions_segments'] == segment]['keywords']
    segment_description_series = nlp_df[nlp_df['positions_segments'] == segment]['descriptions']
    keywords_list = []
    for row in segment_keywords_series:
        for item in re.findall('\w+', row):
            if item.lower() not in stop_words:
                keywords_list.append(item.lower())
    keywords_per_segment[segment] = keywords_list

    descriptions_list = []
    for row in segment_description_series:
        for item in row.split():
            if item.lower() not in stop_words:
                descriptions_list.append(item.lower())
    description_words_per_segment[segment] = descriptions_list


# for key in description_words_per_segment.keys():
#     plt.close()
#     comment_words = ''
#     comment_words += " ".join(description_words_per_segment[key]) + " "
#     wordcloud = WordCloud(width=800, height=800,
#                           background_color='white',
#                           stopwords=stop_words,
#                           min_font_size=10).generate(comment_words)
#     plt.figure(figsize=(8, 8), facecolor=None)
#     plt.imshow(wordcloud)
#     plt.axis("off")
#     plt.tight_layout(pad=0)
#     plt.show()


for key in keywords_per_segment.keys():
    plt.close()
    comment_words = ''
    comment_words += " ".join(keywords_per_segment[key]) + " "
    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stop_words,
                          min_font_size=10).generate(comment_words)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()

# skill_list = ['']