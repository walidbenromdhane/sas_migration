

import os
import pandas as pd

root = r'C:\SAEED\Optum\downloads\02--Quantitative Assessment\02--Output of SAS Content Assessment Tool\EPI\all'

filelist = []
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.endswith('.sas7bdat'):
            filelist.append(os.path.join(path,name))


for item in filelist:
    try:
        tb = pd.read_sas(item)
        tb.to_csv(item.replace('.sas7bdat','.csv'))
    except Exception as e:
        print('Error in reading the SAS table!')
        print(e)