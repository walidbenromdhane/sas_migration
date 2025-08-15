import os
import re
import csv
import json


###################################################################################################
# Global Parameters
###################################################################################################

LOG_ENABLED     = True
LOG_SHOW_ALL    = False


###################################################################################################
# Import the list of patterns
###################################################################################################
filepath = os.path.dirname(os.path.abspath(__file__))
filename = 'data_model_extractor_patterns.json'
with open(os.path.join(filepath,filename), 'r') as f:
    block_definition_dict = json.load(f)


###################################################################################################
# iterate over all directories and subdirectories in the directory path and populate 'input_file_paths'
###################################################################################################

def get_files(folder, extension):

    paths = []
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(extension):
                paths.append(os.path.join(dirpath, filename))

    return(paths)


###################################################################################################
# Output the results in a CSV file
###################################################################################################

def put_csv(output_file, header, content):

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Output Data header 
        for row in header:
            writer.writerow(row)

        # Output Data content
        for row in content:
            writer.writerow(row)


###################################################################################################
# Output the results in a CSV file
###################################################################################################

def put_log(content, type):

    if (LOG_ENABLED):
        if (LOG_SHOW_ALL):
            print(content)
        else:
            if(type=="EXEC_STATUS"):
                print(content)


###################################################################################################
# Normalize text
###################################################################################################

def normalize_text(text):
    
    # Transform to Uppercase
    text = text.upper()

    # Remove Comments between /* and */
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    
    # One-line comments ..
    #text = re.sub(r"\n\*.*",'',text,flags=re.DOTALL)

    # Removing all non-printable characters; replacing them with spaces (to keep the seperation between words)
    text = re.sub(r'[^\x20-\x7E]', ' ', text)

    return(text)


###################################################################################################
# Scan the file content and get all blocks
###################################################################################################

def get_blocks(content):

    #content = ' ' + content
    blocks = []

    for block_definition in block_definition_dict:
        
        # For each Block structure, find all Blocks within the file that matches that Block structure
        block_regex = r'(\s*'+block_definition['delimeters']['start']+'.*?'+block_definition['delimeters']['end']+')'
        block_pattern = re.compile(block_regex, re.DOTALL)
        blocks_content = block_pattern.findall(content)

        #put_log(blocks_content, "EXEC_STATUS")


        for block_content in blocks_content:
            block = {
                "type"              : block_definition['type'],
                "content"           : block_content
            }
            
            #put_log(block, "EXEC_STATUS")

            blocks.append(block)

    return(blocks)


###################################################################################################
# Extract Dependencies from a Block
###################################################################################################

def extract_dependencies(id_counter,block):

    # LOG OUTPUT
    put_log("\n######\n", "EXEC_LOG")
    put_log("> Block type \t\t: " + block['type'], "EXEC_LOG")

    # Add white space before the start of the block to act as a separator for the Tokenization step
    block['content'] = ' ' + block['content']
    block['content'] = block['content'].replace(";", " ")

    #put_log(block, "EXEC_STATUS")

    # LOG OUTPUT
    put_log("\n> Bloc content \t: \n" + block['content'], "EXEC_LOG")

    # Get the block definition from block_definition_dict
    block_definition = [block_definition for block_definition in block_definition_dict if block_definition["type"] == block['type']][0]

    #put_log(block_definition, "EXEC_STATUS")

    # Initialize dependencies content for the current Block
    dependencies_output = {
        "id"                : str(id_counter),
        "statement"         : "",
        "table"             : "",
        "columns"           : "",
        "tables_source"     : "",
        "join_type"         : "",
        "join_table"        : "",
        "join_conditions"   : "",
        "filters"           : ""
    }

    # Tokenize the Block content: Extract Clauses   
    pattern     = '|'.join(map(re.escape, [key + ' ' for key in block_definition['keys']])) # Create a regex pattern from the separators list
    parts       = re.split(pattern, block['content'], flags=re.IGNORECASE)
    
    #put_log(parts, "EXEC_STATUS")

    # LOG OUTPUT
    put_log("\n> Pattern \t\t: \n" + pattern, "EXEC_LOG")
    put_log("\n> Parts \t\t:" + '\n'.join(parts), "EXEC_LOG")


    tokens = []
    for i in range(1, len(parts)):
        sep = re.findall(pattern, block['content'], flags=re.IGNORECASE)[i-1]
        token = sep + parts[i]
        token_normalized = re.sub(r"\s+", " ", token.replace('\n', '').strip()) # Removing all multiple spaces, line-breakers and leading/post spaces
        tokens.append(token_normalized)

    # LOG OUTPUT
	put_log("\n> Tokens \t\t: \n" + '\n'.join(tokens), "EXEC_LOG")

    
    # Processing each token depending the associated Key to extract useful information
    for token in tokens:
        pattern = r"({})\s*(.*)".format("|".join(map(re.escape, block_definition['keys'])))
        clause = re.match(pattern, token, flags=re.IGNORECASE)
        if clause:
            #dependencies_output = process_clause(block['type'], clause, dependencies_output)
            process_clause(block['type'], clause, dependencies_output)

    # Remove ; by the end of every clause, if any
    for key in dependencies_output:
        dependencies_output[key] = dependencies_output[key].rstrip(';')
        
    put_log("", "EXEC_LOG")

    # Return dependencies of the current Block
    return(dependencies_output)

    



###################################################################################################
# Clause Processors for different types of Blocks
###################################################################################################

def process_clause(block_type, clause, dependencies_output):    

    # Add the Statement type to the current Block's dependencies
    dependencies_output['statement'] = block_type

    # Identify Clause Key and Clause Content
    clause_key      = clause.group(1)
    clause_content  = clause.group(2).rstrip(';QUIT').rstrip(';')

    tables_source_array = []

    ##############
    # PROC SQL
    ##############
    if (block_type=="PROC SQL"): 

        # CLAUSE : CREATE TABLE .. (AS)
        if clause_key.upper()=="CREATE TABLE":
            # INFORMATION : table
            try:
                dependencies_output['table'] = re.match(r'(.+?)(?:\s+AS)?$', clause_content).group(1)
            except AttributeError:
                dependencies_output['table'] = ''

            # INFORMATION : columns (If found)
            columns_definition_string = re.search(r'\((.*?)\)', clause_content)
            if columns_definition_string:
                dependencies_output['table'] = dependencies_output['table'][:dependencies_output['table'].find('(')] # Update Table name to remove the column definitoin part that follows '(' 
                columns_array = [element.strip().split()[0] for element in columns_definition_string.group(1).split(',')]
                
                #put_log(columns_array, "EXEC_STATUS")

                #removing table alias
                columns_array = [ column.split('.')[1] for column in columns_array if '.' in column]
            
            
                #keep just column name
                #columns_array = [ column.split(' ')[0] for column in columns_array if ' ' in column] 

                dependencies_output['columns'] = ', '.join(columns_array)

        # CLAUSE : INSERT INTO, INTO
        elif clause_key.upper()=="INTO":
            # INFORMATION : table
            dependencies_output['table'] = clause_content
            
        # CLAUSE : SELECT
        elif clause_key.upper()=="SELECT":
            # INFORMATION : columns
            columns_array = [element.strip() for element in clause_content.split(',')]

            #removing table alias
            columns_array = [ column.split('.')[1] for column in columns_array if '.' in column]

            #put_log(columns_array, "EXEC_STATUS")

            #keep just column name
            #columns_array = [ column.split(' ')[0] for column in columns_array if ' ' in column]

            dependencies_output['columns'] = ', '.join(columns_array)

        # CLAUSE : LIKE
        elif clause_key.upper()=="LIKE":
            # INFORMATION : table_sources
            tables_source_array = [element.strip() for element in clause_content.split(',')] ## Oumaima: Output into Column 'Table Source'
            
            #removing table alias
            tables_source_array = [ table.split(' ')[0] for table in tables_source_array if ' ' in table]

            dependencies_output['tables_source'] = ', '.join(tables_source_array)

        # CLAUSE : FROM (Account for multiple SELECT FROM)
        elif clause_key.upper()=="FROM":
            # INFORMATION : table_sources 
            for element in clause_content.split(','):
                tables_source_array.append(element.strip()) ## Oumaima: Output into Column 'Table Source'
            
            #removing table alias
            tables_source_array = [ table.split(' ')[0] for table in tables_source_array if ' ' in table]

            if (len(dependencies_output['tables_source'])==0):
                dependencies_output['tables_source'] = ', '.join(tables_source_array)
            else:
                dependencies_output['tables_source'] += ', ' + ', '.join(tables_source_array)

        # CLAUSE : JOIN
        elif clause_key.upper() in ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "SELF JOIN"]:
            # INFORMATION : join_type
            dependencies_output['join_type'] = clause_key 
            # INFORMATION : join_table
            dependencies_output['join_table'], join_conditions_raw = clause_content.split(' ON ', 1) ## Oumaima: Output into Column 'Table Source (from Join)'
            # INFORMATION : join_conditions

            #removing table alias
            if ' ' in dependencies_output['join_table']:
                dependencies_output['join_table'] = dependencies_output['join_table'].split(' ')[0]

            join_conditions_array = [element.strip() for element in join_conditions_raw.split(' AND ')]
            
            dependencies_output['join_conditions'] = ', '.join(join_conditions_array)

        # CLAUSE : WHERE
        elif clause_key.upper()=="WHERE":
            # INFORMATION : filters
            filters_array = [element.strip().rstrip(';') for element in clause_content.split(' AND ')]
            dependencies_output['filters'] = ', '.join(filters_array)

    
    ##############
    # DATA STEP
    ##############
    if (block_type=="DATA STEP"): 

        # CLAUSE : DATA
        if clause_key.upper()=="DATA":
            # INFORMATION : table
            dependencies_output['table'] = re.split(r'[ (]', clause_content)[0]

        # CLAUSE : SET
        elif clause_key.upper()=="SET":
            # INFORMATION : tables_source
            clause_content = re.split(r'[;]', clause_content)[0]
            clause_content_parts = clause_content.split('(WHERE=(', 1)
            tables_source_array = [element.strip() for element in clause_content_parts[0].split(',')]
            dependencies_output['tables_source'] = ', '.join(tables_source_array)

            # INFORMATION : filters
            if len(clause_content_parts)>1:
                where_statement = clause_content_parts[1]
                where_statement = re.split(r'[;]', where_statement)[0]
                if (where_statement[len(where_statement)-2:len(where_statement)] == '))'):
                    where_statement = where_statement[:-2]
                filters_array = [element.strip() for element in where_statement.split(' AND ')]
                dependencies_output['filters'] = ', '.join(filters_array)

        # CLAUSE : MERGE
        elif clause_key.upper()=="MERGE":
            # INFORMATION : tables_source
            clause_content = re.split(r'[;]', clause_content)[0]
            tables_source_array = [element.strip() for element in clause_content.split(' ')]
            dependencies_output['tables_source'] = ', '.join(tables_source_array)

        # CLAUSE : WHERE
        elif clause_key.upper()=="WHERE":
            # INFORMATION : filters
            clause_content = re.split(r'[;]', clause_content)[0]
            filters_array = [element.strip() for element in clause_content.split(' AND ')]
            dependencies_output['filters'] = ', '.join(filters_array)
    return dependencies_output
    
################################################################################################

folder_path = r'C:\Users\NW538RY\OneDrive - EY\Desktop\Work\test\model_extractor'

# Define the output CSV file path
output_csv_path = r"C:\Users\NW538RY\OneDrive - EY\Desktop\Work\test\model_extractor\dependencies_output.csv"
    
# Define the file extension to look for
file_extension = ".sas"  # Change this as per your needs (e.g., .sql, .sas)

# Get all file paths with the specified extension in the given folder
file_paths = get_files(folder_path, file_extension)

# Placeholder for CSV header and content
header = [["id", "statement", "table", "columns", "tables_source", "join_type",
           "join_table", "join_conditions", "filters","file_path"]]
csv_content = []
# Loop through each file and extract dependencies
for file_path in file_paths:
    with open(file_path, 'r') as f:
            content = f.read()
    # The extract_dependencies function must be adapted based on your actual data model
    # print(file_path)
    # content = normalize_text(content)
    blocks = get_blocks(content)
    for id_counter,block in enumerate(blocks):
        dependencies_output = extract_dependencies(id_counter,block)
        dependencies_output['file_path'] = file_path
        csv_content.append(dependencies_output)


# print(csv_content)
# Write the extracted data to a CSV file
put_csv(output_csv_path, header, csv_content)

print(f"Dependencies extracted and written to {output_csv_path}")