from cloud_structure import CloudStructure

source_path = '//sasdata/a43/prod/program/001_darc/'
# target_path = 'C:\\Users\\hl63ejg\\Desktop\\Work\\test\\server\\output\\state2\\0726'
target_path = '//sasdata/a66/EY/state1/001_darc/'
structure_mapping_file = r'//sasdata/a66/EY/accelerators/code_migration/mappings/structure_mapping.csv'

cs = CloudStructure(source_path, target_path, structure_mapping_file)
