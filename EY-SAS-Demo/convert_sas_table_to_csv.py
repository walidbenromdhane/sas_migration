
import argparse
import pandas as pd
import os



parser = argparse.ArgumentParser()
parser.add_argument('--main_directory',type=str,default=r'')
parser.add_argument('--sas_tables',type=str, default='')
parser.add_argument('--csv_tables',type=str, default=' ')
args = parser.parse_args()

main_directory = args.main_directory
sas_tables = [a.strip() for a in args.sas_tables.split(',')]
csv_tables = [a.strip() for a in args.csv_tables.split(',')]

print(sas_tables)

for ii in range(len(sas_tables)):
    try:
        tb = pd.read_sas(os.path.join(main_directory, sas_tables[ii] + ".sas7bdat"))
        tb.to_csv(os.path.join(main_directory, csv_tables[ii] + ".csv"))
    except Exception as e:
        print('Error in reading the SAS table!')
        print(e)