import argparse
import traceback
import os
from warnings import simplefilter
import time
import subprocess
import pandas as pd

simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=RuntimeWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--main_directory',type=str,default=r'C:\SAEED\SAS_Python')
args = parser.parse_args()

main_directory = args.main_directory

# listing the main foders
#############################################################################################
main_folders = [name for name in os.listdir(main_directory)
                if os.path.isdir(os.path.join(main_directory, name))]

main_folders_fullpath = [os.path.join(main_directory,x) for x in main_folders]

data = pd.DataFrame()
for item in [a for a in main_folders_fullpath]:
    for path, subdirs, files in os.walk(item):
        for f in files:
            #####################################################
            try:

                f_path = os.path.join(path,f)

                row = {'file': f_path,
                       'getctime': time.ctime(os.path.getctime(f_path)),
                       'getmtime': time.ctime(os.path.getmtime(f_path)),
                       'getatime': time.ctime(os.path.getatime(f_path)),
                       'size': os.path.getsize(f_path)}

                data = data.append(row, ignore_index=True)

                # Save the file after reading every 1000 files
                #####################################################
                if data.shape[0] % 100 == 0:
                    print('{0} files are checked!'.format(data.shape[0]))
                    data.to_csv('output_latest_access_time.csv')

            #####################################################
            except Exception as e:
                print('Warning! Could not read {0}!'.format(f))

# Save the output
#####################################################
data.to_csv('output_latest_access_time.csv')



