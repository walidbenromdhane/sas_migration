import pandas as pd
from postproc import *
import os

class PathMappingManager():

    def __init__(self, execution_report_path        = None,
                       execution_report_xcommand   = None,
                       ca_hard_coded_paths         = None,
                       ca_programs_main            = None,
                       use_case_mapping            = None):
        self.execution_report_path     = self.get_input_path('execution_report_path'        , input_path = execution_report_path)
        self.execution_report_xcommand = self.get_input_path('execution_report_xcommand'    , input_path = execution_report_xcommand)
        self.ca_hard_coded_paths       = self.get_input_path('ca_hard_coded_paths'          , input_path = ca_hard_coded_paths)
        self.ca_programs_main          = self.get_input_path('ca_programs_main'             , input_path = ca_programs_main)
        # self.use_case_mapping          = self.get_input_path('use_case_mapping'             , input_path = use_case_mapping)
        self.hrd_coded_consolidated = pd.DataFrame()

    ###################################################################################################################

    def get_input_path(self, attr = '', input_path = None):
        attr_to_filename = {'execution_report_path'     : 'execution_report_path_appended.xlsx',
                            'execution_report_xcommand' : 'execution_report_x_command_appended.xlsx',
                            'ca_hard_coded_paths'       : 'sas_programs_hard_coded_paths_appended.xlsx',
                            'ca_programs_main'          : 'sas_programs_main_appended.xlsx',
                            # 'use_case_mapping'          : 'use_case_mapping.csv'
                            }
        if input_path == None:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            file_name = attr_to_filename[attr]
            input_path = os.path.join(current_dir,'data','input','Both',file_name)
            return input_path
        else:
            return input_path

    ###################################################################################################################

    def read_input(self):
        '''Reads input defined in __init__ and created dataframes'''
        self.df_execution_report_path     = read_file(self.execution_report_path)
        self.df_execution_report_xcommand = read_file(self.execution_report_xcommand)
        self.df_ca_hard_coded_paths       = read_file(self.ca_hard_coded_paths)
        self.df_ca_programs_main          = read_file(self.ca_programs_main)
        # self.df_use_case_mapping          = read_file(self.use_case_mapping)

    ###################################################################################################################

    def folder_from_path(self, path):
        '''Checks if a given path correponds to a folder or a file.
        If it corresponds to a folder, it is returned as is.
        If not, the path of the folder is returned.'''
        number_of_slashes = path.count('/')+path.count('\\')
        if number_of_slashes==1:
            return path
        else:
            if os.path.splitext(path)[1]:
                return os.path.dirname(path)
            else:
                return path

    ###################################################################################################################

    def process_execution_report_path(self):
        '''Extracts what is needed from the paths execution report
        and does the necessary transformations'''
        df = self.df_execution_report_path
        # Add a column to indicate that the path comes from the execution report
        df['source'] = 'execution_report_path'
        # Drop the 'path' column because it corresponds to the path of the SAS program,
        # which is not what we want here. What we want is 'hrd_coded_path' to be 'path'
        df = df.drop(columns='path').rename(columns = {'hrd_coded_path':'path'})
        # Get only the needed columns
        df = df[['path','source']]
        # Keep only folder names
        df['path'] = df['path'].apply(detect_first_path)
        df['path'] = df['path'].apply(self.folder_from_path)
        df = df.drop_duplicates()
        self.df_execution_report_path = df
        write_path = self.execution_report_path.replace('input','output').replace('csv','xlsx')
        write_file(df, write_path)
        os.startfile(write_path)

    ###################################################################################################################

    def process_execution_report_xcommand(self):
        '''Extracts what is needed from the xcommand execution report
        and does the necessary transformations'''
        df = self.df_execution_report_xcommand
        # Drop the 'path' column because it corresponds to the path of the SAS program,
        # which is not what we want here.
        df = df.drop(columns='path')
        # Get the paths from the xcommands
        df['path'] = df['xcommand'].apply(detect_paths)
        all_paths = set(path for sublist in df['path'] for path in sublist)
        unique_paths = list(all_paths)
        df = pd.DataFrame({'path':unique_paths, 'source':'execution_report_xcommand'})
        df['path'] = df['path'].apply(self.folder_from_path)
        df = df[['path','source']]
        df = df.drop_duplicates()
        self.df_execution_report_xcommand = df
        write_path = self.execution_report_xcommand.replace('input','output').replace('csv','xlsx')
        write_file(df, write_path)
        os.startfile(write_path)

    ###################################################################################################################

    def process_ca_hard_coded_paths(self):
        '''Extracts what is needed from the content assessment report
        and does the necessary transformations'''
        df = self.df_ca_hard_coded_paths
        # Add a column to indicate that the path comes from the execution report
        df['source'] = 'ca_hard_coded_paths'
        # Drop the 'path' column because it corresponds to the path of the SAS program,
        # which is not what we want here. What we want is 'hrd_coded_path' to be 'path'
        df = df.drop(columns='path').rename(columns = {'hrd_code':'path'})
        df = df[['path','source']]
        df['path'] = df['path'].apply(self.folder_from_path)
        df = df.drop_duplicates()
        write_path = self.ca_hard_coded_paths.replace('input','output').replace('csv','xlsx')
        write_file(df, write_path)
        os.startfile(write_path)
        self.df_ca_hard_coded_paths = df

    ###################################################################################################################

    def process_ca_programs_main(self):
        '''Get the paths of the programs that will be migrated.'''
        df = self.df_ca_programs_main
        # Add a column to indicate that the path comes from
        df['source'] = 'ca_programs_main'
        df = df[['path','source']]
        df = df.drop_duplicates()
        write_path = self.ca_programs_main.replace('input','output').replace('csv','xlsx')
        write_file(df, write_path)
        os.startfile(write_path)
        self.df_ca_programs_main = df

    ###################################################################################################################

    def consolidate_paths(self, write_path):
        '''Calls the pre-processing methods and appends the results'''
        self.process_execution_report_path()
        self.process_execution_report_xcommand()
        self.process_ca_hard_coded_paths()
        self.process_ca_programs_main()
        df = pd.concat([self.df_execution_report_path,
                        self.df_execution_report_xcommand,
                        self.df_ca_hard_coded_paths,
                        self.df_ca_programs_main
                        ])
        self.consolidated_paths = df
        write_file(df, write_path)
        # os.startfile(write_path)

    ###################################################################################################################
