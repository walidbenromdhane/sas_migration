# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 11:11:11 2023

@author: EY283FA
"""

import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pandas as pd
import re


df = pd.read_parquet(r'C:\SAEED\Sun Life\Demo Sample Sets\Set 1\Sample Data Sets/{0}.parquet'.format('tbl_newstafftable'))
import boto3
import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from io import BytesIO
aws_access_key_id= ''
aws_secret_access_key=''
bucket_name = 'sunlifeproposal'
s3 = boto3.resource('s3',
aws_access_key_id= aws_access_key_id,
aws_secret_access_key=aws_secret_access_key,verify=False)
obj = s3.Object(bucket_name,'set1/tbl_newstafftable.parquet')
parquet_bytes=obj.get()['Body'].read()
parquet_file = BytesIO(parquet_bytes)
df = pd.read_parquet(parquet_file)
print(df)


file_pathsas = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/ponctualite_voyageur_v2.sas7bdat"
parquet_file_pathsas = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/testsas.parquet"

file_pathcsv = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/test1.csv"
parquet_file_pathcsv = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/testcsv.parquet"

file_pathxlsx = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/test1.xlsx"
parquet_file_pathxlsx = "C:/Users/ey283fa/OneDrive - EY/Bureau/Magnim files/SAS/testxlsx.parquet"


# Decoding the df
def decode_string(x):
    if isinstance(x, bytes):
        return x.decode('latin-1')
    else:
        return x


def convert_to_parquet(file_path, parquet_file_path):
    # Convert sas file
    if file_path.split(".", 1)[1] == 'sas7bdat':
        df = pd.read_sas(file_path)
        # Decoding the df
        df[df.columns] = df[df.columns].applymap(decode_string)
        df.to_parquet(parquet_file_path)

    # Convert csv file
    if file_path.split(".", 1)[1] == 'csv':
        df = pd.read_csv(file_path)
        df.to_parquet(parquet_file_path)

    # Convert xlsx file
    if file_path.split(".", 1)[1] == 'xlsx':
        df = pd.read_excel(file_path)
        df.to_parquet(parquet_file_path)

f_name = 'wdamt1_m'
convert_to_parquet(r'C:\SAEED\Sun Life\Demo Sample Sets\Set 2/{0}.sas7bdat'.format(f_name),
                   r'C:\SAEED\Sun Life\Demo Sample Sets\Set 2/{0}.parquet'.format(f_name))
