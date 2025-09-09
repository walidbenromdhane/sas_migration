import pandas as pd
import os


df = pd.DataFrame()

file_path = r'C:\SAEED\Optum\downloads\02--Quantitative Assessment\02--Output of SAS Content Assessment Tool\Analysis\HEOR'


########################################################
########################################################
########################################################
# Issues
########################################################
for path, subdirs, files in os.walk(file_path):
    for name in files:
        if '_issues' in name and name.endswith('.csv'):
            f = os.path.join(path, name)
            df = df.append(pd.read_csv(f)).reset_index(level=[0], drop=True)


for item in df.columns:
    try:
        df[item] = df[item].str.replace("b'",'')
        df[item] = df[item].str.replace("'",'')
        df[item] = df[item].str.replace('b"','')
        df[item] = df[item].str.replace('"','')
        print('Column {0} is cleaned up!'.format(item))
    except:
        print('Warning for column {0}!'.format(item))

df['team_name'] = df['pgm_name'].str.split('/',expand=True)[1]
df['disck_name'] = df['pgm_name'].str.split('/',expand=True)[2]
df['project_year'] = df['pgm_name'].str.split('/',expand=True)[3]
df['project_name'] = df['pgm_name'].str.split('/',expand=True)[4]
df['project_role'] = df['pgm_name'].str.split('/',expand=True)[5]
df['project_role_sub'] = df['pgm_name'].str.split('/',expand=True)[6]

df.to_csv(file_path+'/ALL_issues.csv', index=False)



########################################################
########################################################
########################################################
# Elemagg
########################################################
df = pd.DataFrame()

for path, subdirs, files in os.walk(file_path):
    for name in files:
        if '_elemagg' in name and name.endswith('.csv'):
            f = os.path.join(path, name)
            df = df.append(pd.read_csv(f)).reset_index(level=[0], drop=True)


for item in df.columns:
    try:
        df[item] = df[item].str.replace("b'",'')
        df[item] = df[item].str.replace("'",'')
        df[item] = df[item].str.replace('b"','')
        df[item] = df[item].str.replace('"','')
        print('Column {0} is cleaned up!'.format(item))
    except:
        print('Warning for column {0}!'.format(item))

df['team_name'] = df['pgm_name'].str.split('/',expand=True)[1]
df['disck_name'] = df['pgm_name'].str.split('/',expand=True)[2]
df['project_year'] = df['pgm_name'].str.split('/',expand=True)[3]
df['project_name'] = df['pgm_name'].str.split('/',expand=True)[4]
df['project_role'] = df['pgm_name'].str.split('/',expand=True)[5]
df['project_role_sub'] = df['pgm_name'].str.split('/',expand=True)[6]

df.to_csv(file_path+'/ALL_elemagg.csv', index=False)


########################################################
########################################################
########################################################
# Steps
########################################################
df = pd.DataFrame()

for path, subdirs, files in os.walk(file_path):
    for name in files:
        if '_steps' in name and name.endswith('.csv'):
            f = os.path.join(path, name)
            df = df.append(pd.read_csv(f)).reset_index(level=[0], drop=True)


for item in df.columns:
    try:
        df[item] = df[item].str.replace("b'",'')
        df[item] = df[item].str.replace("'",'')
        df[item] = df[item].str.replace('b"','')
        df[item] = df[item].str.replace('"','')
        print('Column {0} is cleaned up!'.format(item))
    except:
        print('Warning for column {0}!'.format(item))

df.to_csv(file_path+'/ALL_steps.csv', index=False)