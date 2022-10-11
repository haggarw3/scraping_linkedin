import pandas as pd
import ast
import os
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

data = pd.read_csv('skills per position segment.csv')
# data.head()

path = os.getcwd()
counter = 0
for i in data['Skills']:
    x = pd.DataFrame(ast.literal_eval(i).items())
    x.columns = ['Skill', 'Count']
    segment = data['Position'][counter].replace(' ', '_').replace('/', '_')
    counter += 1
    x.to_csv(path+'/'+segment+"_skill_counts.csv")

