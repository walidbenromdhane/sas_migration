from public_functions import Public_functions
import os, traceback


class ContentAssessment:

    def __init__(self, main_directory_sasfiles, main_directory_sastables, sas_table_row_limit, report_counter, output_directory):
        self.file_suffix = os.path.split(main_directory_sasfiles)[-1]
        self.main_directory_sasfiles = main_directory_sasfiles
        self.main_directory_sastables = main_directory_sastables
        self.sas_table_row_limit = sas_table_row_limit
        self.report_counter = report_counter
        self.output_directory = output_directory
        self.initialize_data_structures()
        self.process_all_files()

    ######################################################################################################################

    def initialize_data_structures(self):
        self.files_df = []
        self.files_detailes_df = []
        self.files_blocks_df = []
        self.files_hrd_code = []
        self.files_proc_lst = []
        self.files_relationships = []
        self.number_of_files = dict()
        self.number_of_files_with_incompatibilities = dict()
        self.main_folders = [name for name in os.listdir(self.main_directory_sasfiles)
                             if os.path.isdir(os.path.join(self.main_directory_sasfiles, name))]
        self.main_folders_fullpath = [os.path.join(self.main_directory_sasfiles, x) for x in self.main_folders]

    ######################################################################################################################

    def process_all_files(self):
        id_counter = 0
        for path, subdirs, files in os.walk(self.main_directory_sasfiles):
            for name in files:
                if name.endswith(('.sas','.cfg','.ksh')):
                    try:
                        self.process_sas_file(path, name, id_counter)
                        id_counter += 1
                        if id_counter % self.report_counter == 0:
                            self.save_intermediate_data(id_counter)
                    except Exception as e:
                        self.handle_file_reading_exception(e)

        self.save_data()
        print('SAS files were successfully identified!')

    ######################################################################################################################
	
    def process_sas_file(self, path, name, id_counter):
        input_file = os.path.join(path, name)
        subdir = path.split('/')[-1]
        self.update_file_counts(subdir)

        with open(input_file, 'r', encoding="latin-1", errors='ignore') as sasfile:
            contents_lst, contents_str = self.read_and_clean_sas_file(sasfile)
            lines_count = len(contents_lst)

            hrd_lst                  = Public_functions.find_hard_code(contents_str)
            filename_lst             = Public_functions.find_filename(contents_str)
            libname_lst              = Public_functions.find_libname(contents_str)
            let_lst                  = Public_functions.find_let(contents_str)
            mac_lst                  = Public_functions.find_macro(contents_str)
            inc_lst                  = Public_functions.find_include(contents_str)
            proc_lst                 = Public_functions.find_proc(contents_str)
            create_tbl_lst           = Public_functions.find_create_table(contents_str)
            select_from_tbl_lst      = Public_functions.find_select_from_table(contents_str)
            x_command_lst            = Public_functions.find_x_commands(contents_str)
            blocks_lst               = Public_functions.find_code_blocks(contents_str)
            table_relationships_lst  = Public_functions.find_table_relationships(id_counter, input_file)

        self.append_file_data(id_counter, input_file, path, name, lines_count, contents_str,
                              hrd_lst, proc_lst, table_relationships_lst, filename_lst,
                              libname_lst, let_lst, mac_lst, inc_lst, create_tbl_lst,
                              select_from_tbl_lst, x_command_lst, blocks_lst)
        self.update_incompatibilities_count(subdir, hrd_lst)

    ######################################################################################################################

    def read_and_clean_sas_file(self, sasfile):
        contents_lst = sasfile.readlines()
        contents_str = r"\n".join(a.strip() for a in contents_lst)
        contents_lst, contents_str = Public_functions.clean_sas_code(contents_lst, contents_str)
        return contents_lst, contents_str

    ######################################################################################################################

    def update_file_counts(self, subdir):
        if subdir in self.number_of_files.keys():
            self.number_of_files[subdir] += 1
        else:
            self.number_of_files[subdir] = 1

    ######################################################################################################################
	
    def update_incompatibilities_count(self, subdir, hrd_lst):
        if subdir in self.number_of_files_with_incompatibilities.keys():
            if len(hrd_lst) > 0:
                self.number_of_files_with_incompatibilities[subdir] += 1
            else:
                self.number_of_files_with_incompatibilities[subdir] = 0

    ######################################################################################################################

    def append_hrd_code(self, id_counter, path, name, input_file, hrd_lst):
        self.files_hrd_code.extend([{
            'id'        : str(id_counter),
            'path'      : path,
            'name'      : name,
            'input_file': input_file,
            'hrd_code'  : a
        } for a in hrd_lst])

    ######################################################################################################################

    def append_proc_list(self, id_counter, path, name, input_file, proc_lst):
        self.files_proc_lst.extend([{
            'id'        : str(id_counter),
            'path'      : path,
            'name'      : name,
            'input_file': input_file,
            'proc'      : a,
        } for a in proc_lst])

    ######################################################################################################################

    def append_files_df(self, id_counter, path, name, input_file, lines_count, contents_str):
        self.files_df.append({
            'id'              : str(id_counter),
            'path'            : path,
            'name'            : name,
            'input_file'      : input_file,
            'main'            : self.main_directory_sasfiles,
            'number_of_lines' : lines_count,
            'program_code'    : contents_str
        })

    ######################################################################################################################

	def append_files_relationships(self, table_relationships_lst):
        self.files_relationships.extend([{
            "id"               : line['id'],
            "statement"        : line['statement'],
            "table"            : line['table'],
            "columns"          : line['columns'],
            "tables_source"    : line['tables_source'],
            "join_type"        : line['join_type'],
            "join_table"       : line['join_table'],
            "join_conditions"  : line['join_conditions'],
            "filters"          : line['filters']
        } for line in table_relationships_lst])

    ######################################################################################################################

    def append_files_details_df(self, id_counter, path, name, input_file, filename_lst,
                                libname_lst, let_lst, mac_lst, inc_lst, create_tbl_lst,
                                select_from_tbl_lst, x_command_lst):
        self.files_detailes_df.extend([{
            'id'       : str(id_counter),
            'path'     : path,
            'name'     : name,
            'input_file': input_file,
            'type'     : a['type']     if 'type' in a else '',
            'original' : a['original'] if 'original' in a else '',
            'key'      : a['key']      if 'key' in a else '',
            'value_0'  : a['value_0']  if 'value_0' in a else '',
            'value_1'  : a['value_1']  if 'value_1' in a else '',
            'index'    : a['index']    if 'index' in a else 0
        } for a in b if a != [] for b in [filename_lst, libname_lst, let_lst, mac_lst, inc_lst,
                                          create_tbl_lst, select_from_tbl_lst, x_command_lst]])

    ######################################################################################################################

    def append_files_blocks_df(self, id_counter, path, name, input_file, blocks_lst):
        self.files_blocks_df.extend([{
            'id'        : str(id_counter),
            'path'      : path,
            'name'      : name,
            'input_file': input_file,
            'block'     : a['block']    if 'block' in a else '',
            'block_idx' : a['block_idx'] if 'block_idx' in a else 0
        } for a in blocks_lst if a != []])

    ######################################################################################################################

	    def append_file_data(self, id_counter, input_file, path, name, lines_count,
                         contents_str, hrd_lst, proc_lst, table_relationships_lst,
                         filename_lst, libname_lst, let_lst, mac_lst, inc_lst,
                         create_tbl_lst, select_from_tbl_lst, x_command_lst, blocks_lst):

        self.append_hrd_code(id_counter, path, name, input_file, hrd_lst)
        self.append_proc_list(id_counter, path, name, input_file, proc_lst)
        self.append_files_df(id_counter, path, name, input_file, lines_count, contents_str)
        self.append_files_blocks_df(id_counter, path, name, input_file, blocks_lst)
        self.append_files_details_df(id_counter, path, name, input_file, filename_lst,
                                     libname_lst, let_lst, mac_lst, inc_lst, create_tbl_lst,
                                     select_from_tbl_lst, x_command_lst)
        self.append_files_relationships(table_relationships_lst)

    ######################################################################################################################

    def save_intermediate_data(self, id_counter):
        print(f'{id_counter} SAS programs were identified')
        self.save_data()

    ######################################################################################################################

    def save_data_to_csv(self, data, filename, columns):
        Public_functions.save_dict_to_csv(data, f'{self.output_directory}/{filename}', columns)

    ######################################################################################################################

    def save_data(self):
        self.save_data_to_csv(self.files_df,
                              'sas_programs_main.csv',
                              ['id', 'path', 'name', 'input_file', 'main', 'number_of_lines'])
        self.save_data_to_csv(self.files_detailes_df,
                              'sas_programs_details.csv',
                              ['id', 'path', 'name', 'input_file', 'type', 'original', 'key',
                               'value_0', 'value_1', 'index'])
        self.save_data_to_csv(self.files_relationships,
                              'sas_programs_table_relationships.csv',
                              ['id', 'statement', 'table', 'columns', 'tables_source',
                               'join_type', 'join_table', 'join_conditions', 'filters'])
        self.save_data_to_csv(self.files_blocks_df,
                              'sas_programs_blocks.csv',
                              ['id', 'path', 'name', 'input_file', 'block', 'block_idx'])
        self.save_data_to_csv(self.files_hrd_code,
                              'sas_programs_hard_coded_paths.csv',
                              ['id', 'path', 'name', 'input_file', 'hrd_code'])
        self.save_data_to_csv(self.files_proc_lst,
                              'sas_programs_proc_list.csv',
                              ['id', 'path', 'name', 'input_file', 'proc'])

    ######################################################################################################################

	    def handle_file_reading_exception(self, e):
        print('Warning in reading SAS file!')
        print('############################################################')
        print(e)
        print('############################################################')
        print(r'\n')

    ######################################################################################################################

class ContentAssessementExecution():

    def __init__(self, main_directory_sasfiles_list, main_output_directory):

        self.report_counter = 100
        self.sas_table_row_limit = 100
        self.main_directory_sasfiles_list = main_directory_sasfiles_list
        self.main_output_directory = main_output_directory

    ######################################################################################################################

    def run(self):

        for main_directory_sasfiles in self.main_directory_sasfiles_list:

            report_counter = self.report_counter
            main_directory_sastables = main_directory_sasfiles
            file_suffix = main_directory_sasfiles.replace('/','_').replace('\\','_').replace(':','')
            output_directory = os.path.join(self.main_output_directory,'outputs_{0}'.format(file_suffix))
            sas_table_row_limit = self.sas_table_row_limit

            if os.path.exists(output_directory) == False:
                os.makedirs(output_directory)

            CA = None

            try:
                CA = ContentAssessment(main_directory_sasfiles, main_directory_sastables,
                                       sas_table_row_limit, report_counter, output_directory)

            except Exception as e:
                logfile_path = "{0}/exceptions_loadfiles_{1}.log".format(output_directory,file_suffix)
                with open(logfile_path, "a") as logfile:
                    traceback.print_exc(file=logfile)
                print('Error in finding .sas files!')
                print('############################################################')
                print(e)
                print('############################################################')
                print(r'\n')
                raise

            print('Folder {0} finished successfully!'.format(main_directory_sasfiles))
