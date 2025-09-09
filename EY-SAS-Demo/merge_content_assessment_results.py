import os
import pandas as pd
import numpy as np
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=RuntimeWarning)

root = r'C:\SAEED\Optum\downloads\02--Quantitative Assessment\01--Output of python script\LSRD_EPI'

sas_programs = pd.DataFrame()
sas_programs_details = pd.DataFrame()
sas_programs_blocks = pd.DataFrame()
sas_programs_hard_coded_paths = pd.DataFrame()
sas_programs_proc_list = pd.DataFrame()
sas_programs_sim = pd.DataFrame()
sas_tables = pd.DataFrame()
sas_tables_sim = pd.DataFrame()

print('################################################')
print('sas_programs')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_'):
            if 'sas_programs_blocks' not in name and \
                    'sas_programs_details' not in name and \
                    'sas_programs_hard_coded_paths' not in name and \
                    'sas_programs_proc_list' not in name and \
                    'sas_programs_sim' not in name:
                print(name)
                df = pd.read_csv(os.path.join(path,name),encoding='latin1')
                df['prefix'] = path.split("\\")[-1]
                sas_programs = sas_programs.append(df)

print('################################################')
print('sas_programs_details')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_details_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_programs_details = sas_programs_details.append(df)

print('################################################')
print('sas_programs_blocks')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_blocks_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_programs_blocks = sas_programs_blocks.append(df)

print('################################################')
print('sas_programs_hard_coded_paths')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_hard_coded_paths_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_programs_hard_coded_paths = sas_programs_hard_coded_paths.append(df)

print('################################################')
print('sas_programs_proc_list')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_proc_list_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_programs_proc_list = sas_programs_proc_list.append(df)

print('################################################')
print('sas_programs_sim')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_programs_sim_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_programs_sim = sas_programs_sim.append(df)

print('################################################')
print('sas_tables')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_tables_'):
            if 'sas_tables_sim' not in name:
                print(name)
                df = pd.read_csv(os.path.join(path,name),encoding='latin1')
                df['prefix'] = path.split("\\")[-1]
                sas_tables = sas_tables.append(df)

print('################################################')
print('sas_tables_sim')
print('################################################')
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.startswith('sas_tables_sim_'):
            print(name)
            df = pd.read_csv(os.path.join(path,name),encoding='latin1')
            df['prefix'] = path.split("\\")[-1]
            sas_tables_sim = sas_tables_sim.append(df)


sas_programs_details = sas_programs_details.merge(sas_programs, left_on=['id','prefix'], right_on=['id','prefix'], how='left')
sas_programs_blocks = sas_programs_blocks.merge(sas_programs, left_on=['id','prefix'], right_on=['id','prefix'], how='left')
sas_programs_hard_coded_paths = sas_programs_hard_coded_paths.merge(sas_programs, left_on=['id','prefix'], right_on=['id','prefix'], how='left')
sas_programs_proc_list = sas_programs_proc_list.merge(sas_programs, left_on=['id','prefix'], right_on=['id','prefix'], how='left')

sas_programs.to_csv(root + '/sas_programs.csv')
sas_programs_details.to_csv(root + '/sas_programs_details.csv')
sas_programs_blocks.to_csv(root + '/sas_programs_blocks.csv')
sas_programs_hard_coded_paths.to_csv(root + '/sas_programs_hard_coded_paths.csv')
sas_programs_proc_list.to_csv(root + '/sas_programs_proc_list.csv')
sas_programs_sim.to_csv(root + '/sas_programs_sim.csv')
sas_tables.to_csv(root + '/sas_tables.csv')
sas_tables_sim.to_csv(root + '/sas_tables_sim.csv')