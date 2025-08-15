from detect_schemas import *
import chardet, os
import pandas as pd

##############################################################################################################################

def fix_file_encoding(filepath):
    with open(filepath, 'rb') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        detection = chardet.detect(line)
        try:
            lines[i] = line.decode('utf8')
        except:
            try:
                lines[i] = line.decode('ISO-8859-1')
            except:
                lines[i] = line.decode(detection['encoding'])

    # Write the content to a new file in UTF-8 encoding
    with open(filepath, mode='w', newline='', encoding='utf8') as f:
        f.writelines(lines)

##############################################################################################################################

def extract_table_name(statement, library_name):
    if "create table" in statement.lower():
        match = re.search(r"create table\s+(?:\w+\.)?(\w+)", statement, re.IGNORECASE)
    else:
        # match = re.search(fr"{library_name}\.([a-zA-Z0-9_]+)", statement, re.IGNORECASE)
        match = re.search(fr"{library_name}\.([^ ]+)", statement, re.IGNORECASE)
    table = match.group(1) if match else None
    return table

##############################################################################################################################

def get_list_of_libnames(input_directory):

    results = detect_schemas_and_libraries(input_directory)
    schemas_and_libraries = pd.DataFrame(results, columns=['file_path', 'libname_statement', 'schema', 'libname', 'line'])
    # Create a list with a list of all detected library names and schemas
    schemas = set(schemas_and_libraries[~schemas_and_libraries.schema.isnull()]['schema'])
    libname = set(schemas_and_libraries[~schemas_and_libraries.libname.isnull()]['libname'])
    libnames_etc = set([l.upper() for l in libname.union(schemas)])

    return libnames_etc

##############################################################################################################################

def extract_input_output_tables_from_library_occurrences(library_occurrences, library_name):

    db_out_operations = ["create table", "insert into", "delete from"]
    db_in_operations = ["select", "from", "join"] # Assuming common read operations

    input_tables = []
    output_tables = []

    for occurrence in library_occurrences:
        occurrence = occurrence.split(":",1)[1]
        if occurrence.strip().lower().startswith("data") or any(op in occurrence.lower() for op in db_out_operations):
            table = extract_table_name(occurrence, library_name)
            if table:
                output_tables.append(table)
        elif any(op in occurrence.lower() for op in db_in_operations):
            table = extract_table_name(occurrence, library_name)
            if table:
                input_tables.append(table)
    input_tables = ', '.join(input_tables)
    output_tables = ', '.join(output_tables)
    return input_tables, output_tables

##############################################################################################################################

def extract_input_output_tables_from_one_file(file_path, libnames_etc):

    db_out_operations = ["create table", "insert into", "delete from"]
    db_in_operations = ["select", "from", "join"] # Assuming common read operations
	data = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for library_name in libnames_etc:
        # print("§ The library is:",library_name)
        library_occurrences = []
        for line_number, line in enumerate(lines):
            if ' '+library_name.lower()+'.' in line.lower():
                library_occurrences.append(f'line{line_number}: {line.strip()}')

        #for lo in library_occurrences: print("    ",lo)
        input_tables, output_tables = extract_input_output_tables_from_library_occurrences(library_occurrences, library_name)
		library_occurrences = '\n'.join(library_occurrences)
        if library_occurrences != '':
            data.append((file_path, library_name, input_tables, output_tables, library_occurrences))
    df = pd.DataFrame(data=data, columns=['file_path', 'library_name', 'input_tables', 'output_tables', 'library_occurrences'])
    # print("*** Inputs:",input_tables)
    # print("*** Outputs:",output_tables)

    return df

########################################################################################################

def get_all_file_paths(directory_path):
    file_paths = []
    # Recursively collect all source files and their names
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_paths.append(file_path)
    return file_paths

########################################################################################################

def extract_input_output_tables_from_folder(directory_path, csv_output_path=None):

    data = []
    file_paths = get_all_file_paths(directory_path)
    ''' To avoid rebuilding the list of libnames for a directory when the code goes through all the files in that directory,
    we create a dictionary containing the list of libnames and schemas for every directory. The list is created when the
    code processes the first file and then it does not to create it again.
    '''
    directory_libname = {}
    for file_path in file_paths:
        try:
            fix_file_encoding(file_path)
            input_directory = os.path.dirname(file_path)
            libnames_etc = directory_libname.get('input_directory',None) #If the list of libnames for that directory exists, use it...
            if libnames_etc is None: # ... If not ...
                libnames_etc = get_list_of_libnames(input_directory) # ... create it ...
                directory_libname['input_directory'] = libnames_etc # ... and add it to the dictionary.
            df = extract_input_output_tables_from_one_file(file_path, libnames_etc)
            data_to_append = df.iloc[:].values.tolist()
            data.extend(data_to_append)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    header = df.columns
    df = pd.DataFrame(data, columns=header)
    df.to_csv(csv_output_path, encoding='utf-8', index=False)
    return df

##############################################################################################################################

directory_path = r"C:\Users\h163ejg\Desktop\Work\extract_schemas_and_tables\test_schema_1"
output_csv = r"C:\Users\h163ejg\Desktop\Work\extract_schemas_and_tables\test_schema_1\input_output.csv"
df = extract_input_output_tables_from_folder(directory_path, csv_output_path=output_csv)
