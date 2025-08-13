import os

def replace_string_in_files(directory, original_string, new_string):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sas') or file.endswith('.cfg'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as file:
                    content = file.read()

                content = content.replace(original_string, new_string)

                with open(file_path, 'w') as file:
                    file.write(content)

# Example usage
directory_path = r'C:\Users\hl63ejg\Desktop\Work\test\cfg'
original_string = '==============================================================='
new_string = 'ifrs9'

replace_string_in_files(directory_path, original_string, new_string)
