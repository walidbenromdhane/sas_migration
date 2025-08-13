from code_migration import CodeMigrationExecution

# Define input and output folders
input_dir_list = ['/sasdata/a66/EY/state0/1018-PME/']
output_dir_list = ['/sasdata/a66/EY/state1/1022-PME/TEST/']

# input_dir_list = ['C:\\Users\\hl63ejg\\Desktop\\Work\\test\\server\\input\\darp_octroi']
# output_dir_list = ['C:\\Users\\hl63ejg\\Desktop\\Work\\test\\server\\output\\state1\\0806\\darp_octroi']

# Define the mapping folder
path_mapping_file = 'path_mappings_pre.csv'

cme = CodeMigrationExecution(input_dir_list, output_dir_list, path_mapping_file)
# cme = CodeMigrationExecution()
