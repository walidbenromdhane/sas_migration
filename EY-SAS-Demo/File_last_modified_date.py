import os
import time
from datetime import date
import pandas as pd
import numpy as np
from fnmatch import fnmatch
import subprocess

filelist = []
root = '/home/magnim.farouh@ca.ey.com/' # change here to match your directory #
pattern = "*.csv" # change here to match the format you are interested in #

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            filelist.append(os.path.join(path,name))

### With os.path

df = pd.DataFrame(index = np.arange(len(filelist)), columns=np.arange(4))
for j in range(0,len(filelist)):
    df.iat[j,0]=filelist[j]
    df.iat[j,1]=time.ctime(os.path.getctime(filelist[j]))
    df.iat[j,2]=time.ctime(os.path.getmtime(filelist[j]))
    df.iat[j,3]=time.ctime(os.path.getatime(filelist[j]))

df

df1 = df.rename(columns={0: "file_name", 1: "creation_date", 2: "last_modified_date", 3: "last_access_date"})

df1.to_csv("/home/magnim.farouh@ca.ey.com/results.csv", index=False)
SAS.df2sd(df1, 'work.result1')


### With os.stat

df = pd.DataFrame(index = np.arange(len(filelist)), columns=np.arange(4))
for j in range(0,len(filelist)):
    df.iat[j,0]=filelist[j]
    df.iat[j,1]=time.ctime(os.stat(filelist[j]).st_ctime)
    df.iat[j,2]=time.ctime(os.stat(filelist[j]).st_mtime)
    df.iat[j,3]=time.ctime(os.stat(filelist[j]).st_atime)

df2 = df.rename(columns={0: "file_name", 1: "creation_date", 2: "last_modified_date", 3: "last_access_date"})

df2.to_csv("/home/magnim.farouh@ca.ey.com/results1.csv", index=False)
SAS.df2sd(df2, 'work.result2')

### With Linux command stat

df = pd.DataFrame(index = np.arange(len(filelist)), columns=np.arange(4))
for j in range(0,len(filelist)):
    df.iat[j,0]=filelist[j]
    process = subprocess.run(['stat', filelist[j]], stdout=subprocess.PIPE)
    A = process.stdout.split()
    df.iat[j,1]=A[26].decode("utf-8")  +" "+ A[27].decode("utf-8")
    df.iat[j,2]=A[30].decode("utf-8")  +" "+ A[31].decode("utf-8")
    df.iat[j,3]=A[34].decode("utf-8")  +" "+ A[35].decode("utf-8")


df3 = df.rename(columns={0: "file_name", 1: "last_access_date", 2: "last_content_modified_date", 3: "last_change_date"})

df3.to_csv("/home/magnim.farouh@ca.ey.com/results2.csv", index=False)
SAS.df2sd(df3, 'work.result3')