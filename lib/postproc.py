import os, re
import pandas as pd
###################################################################################################################

def append_one_file(main_folder, file_prefix, folder_prefix):
    merged_df = pd.DataFrame()

    # Loop through all subfolders in the main folder
    for subfolder_name in os.listdir(main_folder):

        subfolder_path = os.path.join(main_folder, subfolder_name)
        # Check if the subfolder name starts with "output_"
        if os.path.isdir(subfolder_path) and subfolder_name.startswith(folder_prefix):
            # Loop through all files in the subfolder
            for path, subdirs, files in os.walk(subfolder_path):
                for report_name in files:
                    file_path = os.path.join(path, report_name)
                    if str(report_name).startswith(file_prefix):
                        try:
                            df = pd.read_csv(file_path, encoding='latin1')
                            df['report_folder'] = path
                            # Append to the merged DataFrame
                            merged_df = pd.concat([merged_df, df], ignore_index=True)
                        except Exception as e:
                            # print(f"File {file_path} could not be read !")
                            print(str(e)+f" {file_path}")

    return merged_df

###################################################################################################################

def append_all_files(main_folder, file_prefix_list, folder_prefix):
    for file_prefix in file_prefix_list:
        merged_df = append_one_file(main_folder, file_prefix, folder_prefix)
        # Saving the merged DataFrame to a CSV file (optional)
        merged_df_path = os.path.join(main_folder, f'{file_prefix}_appended.xlsx')
        merged_df.to_excel(merged_df_path, index=False)

###################################################################################################################

def read_file(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding="latin-1")
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise("File extension should be CSV or XLSX")
    return df

###################################################################################################################

def write_file(df, file_path):
    if file_path.endswith('.csv'):
        df.to_csv(file_path, encoding="latin-1", index=False)
    elif file_path.endswith('.xlsx'):
        df.to_excel(file_path, index=False)
    else:
        raise("File extension should be CSV or XLSX")
    return df

###################################################################################################################

def detect_paths(input_string):
    # Regular expression to match Unix-like and Windows-like paths
    path_pattern = re.compile('(/[^\s]+|[A-Za-z]:\\\\[^\s]+)')
    if type(input_string) == str:
        paths = path_pattern.findall(input_string)
        paths = [item for sublist in paths for item in sublist if item]
        return paths
    else:
        return ['']

###################################################################################################################

def detect_first_path(input_string):
    # Regular expression to match Unix-like and Windows-like paths
    try:
        first_path = detect_paths(input_string)[0]
    except:
        first_path = input_string
    return first_path

###################################################################################################################
