# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 23:43:28 2021

@author: Saeed Marzban
"""

from find_sas_files import Find_SAS_Files
from find_similarities import Find_Similarities
from find_table_similarities import Find_table_similarities
from public_functions import Public_functions
import argparse
import traceback
import os
from warnings import simplefilter
import re

simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=RuntimeWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--main_directory_sasfiles',type=str)
parser.add_argument('--main_directory_sastables',type=str)
parser.add_argument('--report_counter',type=int,default=100)
parser.add_argument('--max_similarity_matrix_size',type=int,default=100) # The similarity matrix would be of size N * N, e.g. N = 1000
parser.add_argument('--max_table_similarity_matrix_size',type=int,default=100) # The similarity matrix would be of size N * N, e.g. N = 1000
parser.add_argument('--sas_table_row_limit',type=int,default=20)
args = parser.parse_args()

main_directory_sasfiles_list = [a.strip() for a in args.main_directory_sasfiles.split(',')]

for main_directory_sasfiles in main_directory_sasfiles_list:

    report_counter = args.report_counter 
    main_directory_sastables = main_directory_sasfiles
    file_suffix = os.path.split(main_directory_sasfiles)[-1]
    output_directory = 'outputs_{0}'.format(file_suffix)
    max_similarity_matrix_size = args.max_similarity_matrix_size
    max_table_similarity_matrix_size = args.max_table_similarity_matrix_size
    sas_table_row_limit = args.sas_table_row_limit


    # load all files and the main folders
    ##################################################################
    ##################################################################
    ###
    
    if os.path.exists(output_directory) == False:
        os.makedirs(output_directory)

    ORG = None

    try:
        ORG = Find_SAS_Files(main_directory_sasfiles,main_directory_sastables,sas_table_row_limit,report_counter,output_directory)

    except Exception as e:
        with open("{0}/exceptions_loadfiles_{1}.log".format(output_directory,file_suffix), "a") as logfile:
                traceback.print_exc(file=logfile)
        print('Error in finding .sas files!')
        print('#############################################')
        print(e)
        print('#############################################')
        print(r'\n')
        raise

    # Find similarities of SAS codes
    ##################################################################
    ##################################################################

    try:
        Find_Similarities(ORG, main_directory_sasfiles, report_counter, max_similarity_matrix_size, output_directory)
        print('SAS programs similarities were successully identified!')

    except Exception as e:
        with open("{0}/exceptions_findsimilarities_{1}.log".format(output_directory,file_suffix), "a") as logfile:
            traceback.print_exc(file=logfile)
        print('Error in finding similarities!')
        print('#############################################')
        print(e)
        print('#############################################')
        print(r'\n')


    # Find similarities of SAS tables
    ##################################################################
    ##################################################################

    try:
        Find_table_similarities(ORG, main_directory_sasfiles, report_counter, max_table_similarity_matrix_size, output_directory)
        print('SAS tables similarities were successully identified!')

    except Exception as e:
        with open("{0}/exceptions_findtablesimilarities_{1}.log".format(output_directory,file_suffix), "a") as logfile:
            traceback.print_exc(file=logfile)
        print('Error in finding tables similarities!')
        print('#############################################')
        print(e)
        print('#############################################')
        print(r'\n')

    print('Folder {0} finished successfully!'.format(main_directory_sasfiles))