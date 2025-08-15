import os, re, platform
import pandas as pd


def extract_libname_schemas(file_path):

    # libname_pattern_1 = re.compile(r'LIBNAME\s+(\w+).*?SCHEMA\s*=\s*(\w+)', re.IGNORECASE)
    # libname_pattern_2 = re.compile(r"LIBNAME\s+(\w+)", re.IGNORECASE)

    results = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if line.upper().strip().startswith('LIBNAME'):
                libname_statement = line.strip()
                comp = [x.strip() for x in libname_statement.strip().split(' ') if x!='']
                libname = comp[1]
                schema = None
                if len(comp)>3:
                    for c in comp:
                        if c.upper().startswith('SCHEMA'): schema = c.split('=')[1].strip()
                        #TODO Add other syntaxes for the libname statement
                results.append((file_path, libname_statement, schema, libname, line_number))

    return results

def detect_schemas_and_libraries(directory):
    all_results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.sas'):
                file_path = os.path.join(root, file)
                print(file_path)
                all_results.extend(extract_libname_schemas(file_path))

    return all_results

def save_results_to_csv(results, output_file):
    df = pd.DataFrame(results, columns=['file_path', 'libname_statement', 'schema', 'libname', 'line'])
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Results saved to {output_file}")

if __name__ == "__main__":

    if platform.system() == "Windows":
        input_directory = r"C:\Users\h163ejg\Desktop\Work\extract_schemas_and_tables\test_schema_1"
        output_file = r'C:\Users\h163ejg\Desktop\Work\extract_schemas_and_tables\test_schema_1\schemas_detected.csv'

    if platform.system() == "Linux":
        input_directory = r"/sasdata/a66/EY/replica_93/"
        output_file = '/home/c9009a3t/sas_migration/content_assessment/schemas_detected.csv'

    schemas_and_libraries = detect_schemas_and_libraries(input_directory)
    if schemas_and_libraries:
        save_results_to_csv(schemas_and_libraries, output_file)
    else:
        print("No LIBNAME statements with SCHEMA found.")
