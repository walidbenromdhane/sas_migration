import os, re, platform
import pandas as pd


def extract_tables(file_path, schemas, libnames):

    results = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            for schema in schemas:
                table_pattern = re.compile(rf'(?<!//)\b{schema}\.([a-zA-Z_][a-zA-Z0-9_]*)\b', re.IGNORECASE)
                matches = table_pattern.findall(line)
                for table in matches:
                    results.append((file_path, schema, None, table, line_number, line.strip()))
            for libname in libnames:
                table_pattern = re.compile(rf'(?<!//)\b{libname}\.([a-zA-Z_][a-zA-Z0-9_]*)\b', re.IGNORECASE)
                matches = table_pattern.findall(line)
                if matches:
                    for table in matches:
                        results.append((file_path, None, libname, table, line_number, line.strip()))

    return results


def process_schemas(df, input_dir):
    all_results = []
    schemas = [s.upper() for s in df.schema.unique()]
    libnames = [l.upper() for l in df.libname.unique()]
    libnames = list(set(libnames).difference(set(schemas)))
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.sas','.cfg')):
                file_path = os.path.join(root, file)
                print(file_path)
                if os.path.exists(file_path):
                    results = extract_tables(file_path, schemas, libnames)
                    all_results.extend(results)

return all_results


def save_results_to_csv(results, output_file):
    df = pd.DataFrame(results, columns=['file_path', 'schema', 'libname', 'table', 'line_number', 'line_content']).drop_duplicates()
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Results saved to {output_file}")


if __name__ == "__main__":

    if platform.system() == "Windows":
        schemas_file = "./content_assessment/schemas_detected.csv"
        output_file = "./content_assessment/schemas_and_tables.csv"
        input_directory = r"C:\Users\h163ejg\Desktop\test_schema"

    if platform.system() == "Linux":
        schemas_file = '/home/c9009a3t/sas_migration/content_assessment/schemas_detected.csv'
        output_file = '/home/c9009a3t/sas_migration/content_assessment/schemas_and_tables.csv'
        input_directory = r"/sasdata/a66/EY/replica_93/"

    if os.path.exists(schemas_file):
        schemas_df = pd.read_csv(schemas_file)
        results = process_schemas(schemas_df, input_directory)
        if results:
            save_results_to_csv(results, output_file)
        else:
            print("No tables found for the detected schemas.")
    else:
        print(f"Schema file '{schemas_file}' not found. Run the first script to generate it.")
