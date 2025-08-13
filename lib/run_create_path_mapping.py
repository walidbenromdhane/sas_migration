from create_path_mapping import PathMappingManager

root = r'/sasdata/a66/EY/state0/1018-PME/path_test/'
write_path = r"/sasdata/a66/EY/state0/1018-PME/path_test_output/paths_to_map.csv"

execution_report_path     = f'{root}/execution_report_path.csv'
execution_report_xcommand = f'{root}/execution_report_x_command.csv'
ca_hard_coded_paths       = f'{root}/sas_programs_hard_coded_paths.csv'
ca_programs_main          = f'{root}/sas_programs_main.csv'

pmm = PathMappingManager(execution_report_path,
                         execution_report_xcommand,
                         ca_hard_coded_paths,
                         ca_programs_main)

pmm.read_input()
pmm.consolidate_paths(write_path)
