# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 22:34:06 2021

@author: Saeed Marzban
"""

import os
from public_functions import Public_functions
import pandas as pd
import numpy as np

class Find_SAS_Files:

    #############################################################################################
    #############################################################################################
    #############################################################################################
    def __init__(self,main_directory_sasfiles, main_directory_sastables,sas_table_row_limit,report_counter,output_directory):

        self.file_suffix = os.path.split(main_directory_sasfiles)[-1]
        self.main_directory_sasfiles = main_directory_sasfiles
        self.main_directory_sastables = main_directory_sastables
        self.sas_table_row_limit = sas_table_row_limit
        self.report_counter = report_counter
        self.output_directory = output_directory
        self.find_files()
        self.find_tables()

    #############################################################################################
    #############################################################################################
    #############################################################################################
    def find_files(self):
        
        # the output of this class is the list of sas files with their main folder
        #############################################################################################
        self.files_df = []
        self.files_detailes_df = []
        self.files_blocks_df = []
        self.files_hrd_code = []
        self.files_proc_lst = []

        # listing the main foders
        #############################################################################################
        self.main_folders = [name for name in os.listdir(self.main_directory_sasfiles)
                             if os.path.isdir(os.path.join(self.main_directory_sasfiles, name))]

        self.main_folders_fullpath = [os.path.join(self.main_directory_sasfiles,x) for x in self.main_folders]

        id_counter = 0
        
        # going through folders and subfolders and listing all sas files
        #############################################################################################
        for f in range(len(self.main_folders)):
            for path, subdirs, files in os.walk(self.main_folders_fullpath[f]):
                for name in files:
                    if name.endswith('.sas'):

                        try:
                            with open(os.path.join(path, name), 'r', encoding="latin_1", errors='ignore') as sasfile:

                                # Read contents of the file
                                #############################################################################################
                                contents_lst               = sasfile.readlines()
                                contents_str               = r"\n".join(a.strip() for a in contents_lst)
                                contents_lst, contents_str = Public_functions.clean_sas_code(contents_lst, contents_str)
                                lines_count                = len(contents_lst)
                                hrd_lst                    = Public_functions.find_hard_code(contents_str)

                                # # replace the space in hard-coded items with special characters
                                # spec_char = '-'
                                # for item in hrd_lst:
                                #     contents_str = contents_str.replace(item, item.replace(' ', spec_char))

                                filename_lst               = Public_functions.find_filename          (contents_str)
                                libname_lst                = Public_functions.find_libname           (contents_str)
                                let_lst                    = Public_functions.find_let               (contents_str)
                                mac_lst                    = Public_functions.find_macro             (contents_str)
                                inc_lst                    = Public_functions.find_include           (contents_str)
                                proc_lst                   = Public_functions.find_proc              (contents_str)
                                create_tbl_lst             = Public_functions.find_create_table      (contents_str)
                                select_from_tbl_lst        = Public_functions.find_select_from_table (contents_str)

                                # For the blocks we use the uncleaned code
                                blocks_lst                 = Public_functions.find_code_blocks       (contents_str)

                                # # replace the special charachters in hard-coded items with space
                                # contents_str = contents_str.replace(spec_char,' ')
                                #
                                # for lst in [filename_lst, libname_lst, let_lst, mac_lst, inc_lst, create_tbl_lst, select_from_tbl_lst]:
                                #     for item in lst:
                                #         item['original'] = item['original'].replace(spec_char, ' ')
                                #         item['key']      = item['key'].replace(spec_char, ' ')
                                #         item['value_0']  = [a.replace(spec_char, ' ') for a in item['value_0']]
                                #         item['value_1']  = [a.replace(spec_char, ' ') for a in item['value_1']]
                                #
                                # for item in proc_lst:
                                #     item = item.replace(spec_char, ' ')
                                #
                                # for item in blocks_lst:
                                #     item['block'] = [a.replace(spec_char, ' ') for a in item['block']]

                                # append the new lines
                                #############################################################################################
                                [self.files_hrd_code.append({'id':str(id_counter),'hrd_code':a}) for a in hrd_lst]
                                [self.files_proc_lst.append({'id':str(id_counter),'proc':a}) for a in proc_lst]

                                self.files_df.append({'id'               :str(id_counter),
                                                      'main'             : self.main_folders[f],
                                                      'path'             : path,
                                                      'fname'            : name,
                                                      'number_of_lines'  : lines_count,
                                                      'program_code'     : contents_str})

                                self.files_detailes_df.extend([{'id'        : str(id_counter),
                                                               'type'       : a['type'] if 'type' in a else '',
                                                               'original'   : a['original'] if 'original' in a else '',
                                                               'key'        : a['key'] if 'key' in a else '',
                                                               'value_0'    : a['value_0'] if 'value_0' in a else '',
                                                               'value_1'    : a['value_1'] if 'value_1' in a else '',
                                                               'index'      : a['index'] if 'index' in a else 0} for b in [inc_lst,
                                                                                              let_lst,
                                                                                              mac_lst,
                                                                                              libname_lst,
                                                                                              filename_lst,
                                                                                              create_tbl_lst,
                                                                                              select_from_tbl_lst] for a in b if b!=[]])

                                self.files_blocks_df.extend([{'id': str(id_counter),
                                                              'block': a['block'] if 'block' in a else '',
                                                              'block_idx': a['block_idx'] if 'block_idx' in a else 0} for a in blocks_lst if a!=[]])
                                id_counter += 1

                                #############################################################################################
                                if id_counter % self.report_counter == 0:
                                    print('{0} SAS programs were identified'.format(str(id_counter)))
                                    Public_functions.save_dict_to_csv(self.files_df, '{0}/sas_programs_main_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                      ['id', 'main', 'number_of_lines', 'path', 'fname','program_code'])
                                    Public_functions.save_dict_to_csv(self.files_detailes_df,
                                                                      '{0}/sas_programs_details_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                      ['id', 'type', 'original', 'key', 'value_0', 'value_1',
                                                                       'index'])
                                    Public_functions.save_dict_to_csv(self.files_blocks_df, '{0}/sas_programs_blocks_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                      ['id', 'block', 'block_idx'])
                                    Public_functions.save_dict_to_csv(self.files_hrd_code,
                                                                      '{0}/sas_programs_hard_coded_paths_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                      ['id', 'hrd_code'])
                                    Public_functions.save_dict_to_csv(self.files_proc_lst,
                                                                      '{0}/sas_programs_proc_list_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                      ['id', 'proc'])

                        except Exception as e:
                            print('Warning in reading SAS file!')
                            print('#############################################')
                            print(e)
                            print('#############################################')
                            print(r'\n')

            #############################################################################################
            print('SAS files under {0} are checked!'.format(self.main_folders[f]))

        #############################################################################################
        Public_functions.save_dict_to_csv(self.files_df,'{0}/sas_programs_main_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id', 'main','number_of_lines', 'path','fname'])
        Public_functions.save_dict_to_csv(self.files_detailes_df, '{0}/sas_programs_details_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id', 'type', 'original','key', 'value_0', 'value_1', 'index'])
        Public_functions.save_dict_to_csv(self.files_blocks_df, '{0}/sas_programs_blocks_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id', 'block','block_idx'])
        Public_functions.save_dict_to_csv(self.files_hrd_code,
                                          '{0}/sas_programs_hard_coded_paths_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id','hrd_code'])
        Public_functions.save_dict_to_csv(self.files_proc_lst,
                                          '{0}/sas_programs_proc_list_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id', 'proc'])
        print('SAS files were successfully identified!')

    #############################################################################################
    #############################################################################################
    #############################################################################################
    def find_tables(self):

        self.tables_df = []

        # listing the main foders
        #############################################################################################
        main_folders = [name for name in os.listdir(self.main_directory_sastables)
                        if os.path.isdir(os.path.join(self.main_directory_sastables, name))]
        main_folders_fullpath = [os.path.join(self.main_directory_sastables, x) for x in main_folders]

        id_counter = 0

        # going through folders and subfolders and listing all sas files
        #############################################################################################
        for f in range(len(main_folders)):
            for path, subdirs, files in os.walk(main_folders_fullpath[f]):
                for name in files:
                    if str(name).endswith('.sas7bdat'):

                        try:
                            # read the SAS tables
                            #############################################################################################
                            tb = pd.read_sas(os.path.join(path, name), chunksize=self.sas_table_row_limit)
                            data = tb.read()

                            file_stats = os.stat(os.path.join(path, name))

                            table_name        = name.split('.')[0]
                            table_size        = file_stats.st_size
                            number_of_columns = len(tb.column_names)
                            counted_cols      = min(50,number_of_columns)
                            column_names      = [tb.column_names[i] for i in range(counted_cols)]
                            column_types      = [data.dtypes[i]     for i in range(counted_cols)]
                            row_count         = tb.row_count
                            column_min        = [data[column_names[i]].min() for i in range(counted_cols) if column_types[i] in (float, int)]
                            column_max        = [data[column_names[i]].max() for i in range(counted_cols) if column_types[i] in (float, int)]
                            column_avg        = [data[column_names[i]].mean() for i in range(counted_cols) if column_types[i] in (float, int)]
                            column_std        = [np.std(data[tb.column_names[i]]) for i in range(counted_cols) if column_types[i] in (float, int)]
                            column_unq        = [data[column_names[i]].unique() for i in range(counted_cols)]
                            # column_min        = [[''] for i in range(counted_cols)]
                            # column_max        = [[''] for i in range(counted_cols)]
                            # column_avg        = [[''] for i in range(counted_cols)]
                            # column_std        = [[''] for i in range(counted_cols)]
                            # column_unq        = [[''] for i in range(counted_cols)]

                            # Add new line
                            #############################################################################################
                            self.tables_df.append({'id': str(id_counter),
                                                   'main': main_folders[f],
                                                   'path': path,
                                                   'tname': table_name,
                                                   'tsize': table_size,
                                                   'number_of_columns': str(number_of_columns),
                                                   'column_names': column_names,
                                                   'column_types': column_types,
                                                   'column_min' : column_min,
                                                   'column_max' : column_max,
                                                   'column_avg' : column_avg,
                                                   'column_std' : column_std,
                                                   'column_unq' : column_unq,
                                                   'number_of_rows': row_count})

                            id_counter += 1

                            tb.close()

                            #############################################################################################
                            if id_counter % self.report_counter == 0:
                                print('{0} SAS tables were identified'.format(str(id_counter)))
                                Public_functions.save_dict_to_csv(self.tables_df, '{0}/sas_tables_main_{1}.csv'.format(self.output_directory,self.file_suffix),
                                                                  ['id', 'main', 'path',
                                                                   'tname', 'tsize', 'number_of_columns',
                                                                   'number_of_rows', 'column_names',
                                                                   'column_types'])

                        except Exception as e:
                            print('Warning in loading {0}!'.format(os.path.join(path, name)))
                            print('#############################################')
                            print(e)
                            print('#############################################')
                            print(r'\n')

            #############################################################################################
            print('SAS tables under {0} are checked!'.format(main_folders[f]))

        #############################################################################################
        Public_functions.save_dict_to_csv(self.tables_df, '{0}/sas_tables_main_{1}.csv'.format(self.output_directory,self.file_suffix),
                                          ['id','main','path',
                                           'tname','tsize','number_of_columns',
                                           'number_of_rows','column_names',
                                           'column_types'])
        print('SAS tables were successfully identified!')