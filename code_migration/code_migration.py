
import csv, os, re, datetime, shutil, chardet


########################################################################################
# Static functions
########################################################################################

def is_a_file(path):
    """Detects whether a given path corresponds to a file or not."""
    pattern = r'\.[a-zA-Z0-9]{1,9}$'
    if re.search(pattern, path):
        return True
    else:
        return False
		
########################################################################################

def fix_file_encoding(filepath):
    with open(filepath, 'rb') as f:
        data = f.readlines()

    for count, line in enumerate(data):
        detection = chardet.detect(line)
        try:
            data[count] = line.decode('utf8')
        except:
            try:
                data[count] = line.decode('ISO-8859-1')
            except:
                data[count] = line.decode(detection['encoding'])

    # Write the content to a new file in UTF-8 encoding
    with open(filepath, mode='w', newline='', encoding='utf8') as f:
        f.writelines(data)

#########################################################################################

def substring_in_quotes(string):
    """Extracts the substring within quotes from a given string"""
    path_regex = r"(['\"])(.*?)\1"
    matches = re.findall(path_regex, string)
    substring = ''
    if len(matches)>0:
        # substring = matches[0][1]
        substring = [match[1] for match in matches]

	return substring

#########################################################################################

def get_paths_from_line(line, command_regex):
    """Extracts the path from a given line string"""
    paths = []
    matches = re.findall(command_regex, line)
    for match in matches:
        if match:
            if len(match)==2:
                _ , detected_path = match
            else:
                detected_path = match
            # print(detected_path)
            # # If the detected path contains quotes, 
            if ('"' in detected_path) or ("'" in detected_path):
                # get the substring in quotes from the detected path 
                detected_paths = substring_in_quotes(detected_path)
                # print('detected_paths',detected_paths)
                for detected_path in detected_paths: 
                    # Test if the path corresponds to a file and get the folder that contains it.
                    if is_a_file(detected_path):
                        old_path = os.path.dirname(detected_path)
                    else:
                        old_path = detected_path

                    # If the path contains / or \, add it to the list
                    if ('/' in old_path) or ('\\' in old_path) or ('&' in old_path):
                        paths.append(old_path)
            else:
                paths = detect_paths_without_quotes(detected_path)

		# if not '&' in detected_path:
			# If the detected path does not contain quotes, it's not a real path.
			# Example: Assume the code contains a comment like: /* This part contains filename reference names: */
			# Here the algorithm detects the syntax 'filename reference names' and thinks that 'names' is a path, but it's not.
    return paths

########################################################################################

def detect_paths_without_quotes(input_string):
    # Regular expression pattern to detect Unix and Windows file paths
    pattern = r"((?:/[^\s,:\"'()]+)+|(?:\\\\[^\s,:\"'()]+)+)"
    
    # Find all matches in the input string
    # print(input_string)
    matches = re.findall(pattern, input_string)
	
    return matches

########################################################################################

def contains_comment(line):
    if "/*" in line or "*/" in line:
        return "Yes"
    else:
        return "No"

########################################################################################

def get_macro_var_from_path(path):
    """Detects the macro variable used in the path"""
    # Regex to find '&', followed by one or more word characters.
    # This regex still captures a sequence of word characters following an ampersand but uses 
    # a positive lookahead to ensure that the sequence is followed by either a non-word character 
    # (excluding the underscore) or the end of the string. This helps in scenarios where macro 
    # variables are followed by punctuation or are at the end of a string without a non-word delimiter. 

    pattern = r'&(\w+)(?=[^A-Za-z0-9_]|$)'
    # Search for the pattern
    match = re.search(pattern, path)
    # If a match is found, return the first group (the macro-variable name)
    if match:
        return match.group(1)
    else:
        return None

########################################################################################

def get_sas_files(root, input_dir, files):
    # Determine the relative path from the current directory to each SAS file
    relative_path = os.path.relpath(root, input_dir)
    # Exclude the current directory when creating subfolders in the output directory
    if relative_path == '.':
        relative_path = ''
    # Filter the files based on the extension
    sas_files = [f for f in files if f.endswith((".sas",".cfg",".ksh"))]
    return sas_files

########################################################################################


def parse_linux_command(command):
    # Regex pattern to split the command into command type, options, and parameters
    # ^(\S+) - Matches the command type (the first word)
    # ((?:\s+-\S+)*) - Matches options (group of items starting with a hyphen)
    # (.*) - Matches the remaining part, typically the parameters
    pattern = r'^(\S+)((?:\s+-\S+)*)\s*(.*)'

    match = re.match(pattern, command.strip())
    if match:
        command_type = match.group(1)
        options = match.group(2).strip().split()  # Split options into a list, remove leading/trailing spaces
        parameters = match.group(3).strip()  # Remove leading/trailing spaces from parameters
        parameters = re.split(r'[ \t]+', parameters) # Split using delimiter = ' ' or '\t'
        return command_type, options, parameters
    else:
        return None, None, None

########################################################################################

def replace_macro_variables(input_string):
    modified_string = ""
    i = 0
    found = 0
    while i < len(input_string):
        if input_string[i] == "&":
            found = 1
            flag = 0
            macro_variable = ""
            z=i
            i += 1
            while i < len(input_string) and (input_string[i].isalnum() or input_string[i] == "_"):
                macro_variable += input_string[i]
                i += 1
			if z==0:
				modified_string += "SAS.symget('" + macro_variable + "')+r'"
            if i==len(input_string):
                modified_string += "'"+"+SAS.symget('" + macro_variable + "')"
                flag = 1
            elif z!=0 and z!=len(input_string):
                modified_string += "'"+"+SAS.symget('" + macro_variable + "')+r'"
		else:
            modified_string += input_string[i]
            i += 1
    if input_string[len(input_string)-1]!=")" and found == 1 and flag == 0:
        modified_string=modified_string+"'"
    return modified_string


########################################################################################
# The PathMapper class
########################################################################################

class PathMapper:
    def __init__(self, csv_file_path):
        """
        Initializes the PathMapper object and loads path mappings from a CSV file.
	
        Args:
        csv_file_path (str): The path to the CSV file containing path mappings.
        """
        self.csv_file_path = csv_file_path 
        self.mapping_dict = self.read_path_mappings(csv_file_path)

    ########################################################################################

    def read_path_mappings(self, csv_file_path):
        """
        Reads the path mappings from a CSV file and returns a dictionary.
	
        Args:
        csv_file_path (str): The path to the CSV file.
	
        Returns:
        dict: A dictionary with old paths as keys and new paths as values.
        """
        mapping = {}
        with open(csv_file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                old_path, new_path = row
                mapping[old_path.strip()] = new_path.strip()
        return mapping

    ########################################################################################

    def get_new_path(self, old_path):
        """
        Returns what the old path should be replaced with. It could be a new path, the 
        old path with a comment or just the old path.
        """
        old_path = old_path.strip()
        new_path = self.mapping_dict.get(old_path, old_path)
        if "no_migration" in new_path:
            new_path = f"/*EY comment: {new_path}*/ {old_path}\n"
        return new_path
        # return self.mapping_dict.get(old_path, "_unmapped_path_")
		
########################################################################################
# The ReportGenerator class
########################################################################################

class ReportGenerator:

    def __init__(self, report_path, fieldnames):
        self.entries = []
        self.report_path = report_path 
        self.fieldnames = fieldnames

    def add_entry(self, entry):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.entries.append(entry+[timestamp])


    def export_to_csv(self):
        """
        Exports the worksheet to a CSV file.

        Args:
        file_path (str): The path where the CSV file will be saved.
        """
        with open(self.report_path, mode='w', newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            writer.writerow(self.fieldnames)
            writer.writerows(self.entries)

        # with open(self.report_path, 'w', newline='') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
        #     writer.writeheader()
        #     writer.writerows(self.report)

########################################################################################
# The SasProcessor class
########################################################################################

class SasProcessor:

    regex = {
        'let'        : r"(?i)%let\s+(\w+)\s*=\s*(.*?);",
        'filename'   : r"(?i)filename\s+(\S+)\s+([^;]+);?",
        'filename1'  : r"(?i)filename\((\S+),(\S+)\);?",
        'libname'    : r"(?i)libname\s+(\S+)\s+([^;]+);?",
        'include'    : r"(?i)%include\s+([^;]+);?",
        'export'     : r"(?i)proc export\s+([^;]+);?",
        'proc sql'   : r"(?i)proc sql\s+([^;]+);?",
        'import'     : r"(?i)proc import\s+([^;]+);?",
        'printto'    : r"(?i)proc printto\s+([^;]+);?",
        'sasautos'   : r"(?i)\bsasautos\s*=([^;]+)\s*;?",
        'infile'     : r"(?i)infile\s+([^;]+);?",
        'call symput': r'\bcall\s+symputx?\s*(.*)',
    }


    ########################################################################################

    def __init__(self, input_dir, output_dir, path_mapper, report, report_x):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.report = report
        self.report_x = report_x
        self.path_mapper = path_mapper
        self.xcommand_category = {
            'aclget' : 'Category1',
            'echo'   : 'Category1',
            'find'   : 'Category1',
            'ls'     : 'Category1',
            'lsuser' : 'Category1',
            'scp'    : 'Category1',
            'sftp'   : 'Category1',
            'ln'     : 'Category1',
            'unzip'  : 'Category2',
            'cat'  	 : 'Category2',
            'chgrp'  : 'Category2',
            'chmod'  : 'Category2',
            'cp'     : 'Category2',
            'delete' : 'Category2',
            'get'    : 'Category2',
            'gunzip' : 'Category2',
            'gzip' 	 : 'Category2',
            'mkdir'  : 'Category2',
            'mv'     : 'Category2',
            'put'    : 'Category2',
            'rm'     : 'Category2',
            'tar'    : 'Category2',
            'cd'     : 'Category3',
            'umask'  : 'Category3',
            'kill'   : 'Category3',
        }

########################################################################################

	def get_lines_from_file(self, file_path):
		with open(file_path, 'r', encoding='utf8') as f:
			self.lines = f.readlines()

########################################################################################

	def get_macro_definitions(self):
		"""Creates a dictionary with the definitions of the macro variables"""
		macro_definitions = {}
		macro_regex = self.regex['let'] #Regex to find "let" statement
		for line in self.lines:
			matches = re.findall(macro_regex, line)
			for match in matches:
				macro_var = match[0]
				macro_value = match[1]
				if (macro_var in macro_definitions.keys()):
					if (macro_value not in macro_definitions[macro_var]):
						macro_definitions[macro_var].append(macro_value)
				else:
					macro_definitions[macro_var] = [macro_value]
		return macro_definitions

########################################################################################

	def process_sas_file_paths(self, sas_input_path, sas_output_path):
		commands = ["libname", "include", "export", "import", "infile", "proc sql", "printto", 
					"sasautos", "filename", "filename1", "let", "call symput"]
		modified_lines = list(self.lines)
		for command in commands:
			modified_lines = self.process_sas_file_paths_one_command(modified_lines, sas_input_path, sas_output_path, command)
		return modified_lines

########################################################################################

	def process_sas_file_paths_one_command(self, modified_lines, sas_input_path, sas_output_path, command):
		command_regex = self.regex[command]

		# Extracting definitions of macro variables
		macro_definitions = self.get_macro_definitions()

		# Process each line in the SAS script
		for i, line in enumerate(modified_lines):
			modified_lines = self.process_line(modified_lines, line, i, command_regex, sas_input_path, sas_output_path, command, macro_definitions)

		return modified_lines

#########################################################################################

	def process_line(self, modified_lines, line, line_index, command_regex, sas_input_path, sas_output_path, command, macro_definitions):
		paths_from_line = get_paths_from_line(line, command_regex)
		# if paths_from_line:
			# print(line.strip(),'\n',paths_from_line,'\n\n')
		# print("paths_from_line",line_index,":",paths_from_line)
		for path in paths_from_line:
			if ('&' in path) and (command != 'printto'):
				# print(path)
				modified_lines = self.process_macro_path(modified_lines, path, line_index, sas_input_path, sas_output_path, command, macro_definitions)
				# intermediate_output = f'C:/Users/hl63ejg/Desktop/Work/git/sas_migration/code_migration/data/output/intermediate_{line_index}.sas'
				# self.export_sas_output(intermediate_output, modified_lines)
			else:
				# print(path)
				modified_lines = self.process_hardcoded_path(modified_lines, line, line_index, path, sas_input_path, sas_output_path, command)
				line = modified_lines[line_index]
				# intermediate_output = f'C:/Users/hl63ejg/Desktop/Work/git/sas_migration/code_migration/data/output/intermediate_{line_index}.sas'
				# self.export_sas_output(intermediate_output, modified_lines)
		return modified_lines

########################################################################################

	def process_macro_path(self, modified_lines, path, line_index, sas_input_path, sas_output_path, command, macro_definitions):
		macro_var = get_macro_var_from_path(path)
		for j, let_line in enumerate(modified_lines):
            if (r'%let' in let_line.lower()) and (macro_var in let_line):
				try:
					old_paths = macro_definitions[macro_var]
					let_line_new = self.update_macro_definition(let_line, old_paths, sas_input_path, sas_output_path, command, line_index, j)
					modified_lines[j] = let_line_new
				except KeyError:
					has_comment = contains_comment(let_line)
					self.add_unmapped_entry(sas_input_path, sas_output_path, command, line_index, j, let_line, macro_var, has_comment)
		return modified_lines

########################################################################################

	def update_macro_definition(self, let_line, old_paths, sas_input_path, sas_output_path, command, line_index, let_line_index):
		let_line_new = let_line
		for old_path in old_paths:
			if old_path in let_line:
				new_path = self.path_mapper.get_new_path(old_path)
				let_line_new = let_line_new.replace(old_path, new_path)
				has_comment = contains_comment(let_line_new)
				self.add_report_entry(sas_input_path, sas_output_path, command, line_index, let_line_index, let_line, old_path, new_path, has_comment)
		return let_line_new

########################################################################################

	def process_hardcoded_path(self, modified_lines, line, line_index, path, sas_input_path, sas_output_path, command):
	
		new_path = self.path_mapper.get_new_path(path)
		new_line = line.replace(path, new_path)
		modified_lines[line_index] = new_line
		has_comment = contains_comment(new_line)
		self.add_report_entry(sas_input_path, sas_output_path, command, line_index, line_index, line, path, new_path, has_comment)
		return modified_lines

########################################################################################

	def add_report_entry(self, sas_input_path, sas_output_path, command, line_index, let_line_index, line, old_path, new_path, has_comment):
		path = os.path.dirname(sas_input_path)
		name = os.path.basename(sas_input_path)
		row = [
			self.path_mapper.csv_file_path, path, name, sas_input_path, sas_output_path, command,
			line_index + 1, let_line_index + 1, line.strip(), old_path, new_path, 'No' if new_path == old_path else 'Yes', has_comment
		]
		self.report.add_entry(row)

#########################################################################################

	def add_unmapped_entry(self, sas_input_path, sas_output_path, command, line_index, let_line_index, line, macro_var, has_comment):
		path = os.path.dirname(sas_input_path)
		name = os.path.basename(sas_input_path)
		old_path = macro_var
		new_path = "_unmapped_path_"
		row = [
			self.path_mapper.csv_file_path, path, name, sas_input_path, sas_output_path, command,
			line_index + 1, let_line_index + 1, line.strip(), old_path, new_path, 'No', has_comment
		]
		self.report.add_entry(row)

#########################################################################################

	# Process detected Xcommand
	def process_x_command_one_line(self, xcommand, sas_input_path, sas_output_path, line_number):
        # matches = re.findall(r'["\']([^"\']+)["\']', xcommand)
        # matches = [xcommand.strip('x ').strip()]
		matches = re.findall(r'[xX]\s+["\']?(.*?)["\']?\s*;', xcommand)
		if len(matches) == 1:
			# try:
			commands = matches[0].split(";") # The linux commands (without the x). There might be more than one.
			if len(commands) == 1: # The x-command is a simple linux command
				command = commands[0]
				command_type, options, parameters = parse_linux_command(command)
				new_command = self.get_new_command(command, command_type, options, parameters)
				xcommand_category = self.xcommand_category.get(command_type, "Undefined")
			else: # The x-command contains a combination of several linux commands
				command = matches[0]
				new_command = self.get_new_command_from_combination(command)
				xcommand_category = 'Mixed'
				command_type = 'Mixed'
			path = os.path.dirname(sas_input_path)
			name = os.path.basename(sas_input_path)

			has_comment = contains_comment(matches[0])
			row = [self.path_mapper.csv_file_path, path, name, sas_input_path, sas_output_path,
					command_type, command, xcommand_category, line_number, new_command, has_comment] # TODO add a colum "Replaced"
			
			self.report_x.add_entry(row)
			return new_command
			# except:
			# 	#TODO Use logging instead of prints
			# print("###########################################################")
			# print("sas_input_path :",sas_input_path)
			# print("line_number :",line_number)
			# print("xcommand :",xcommand)
			# print("command :",command)
			# print("command_type :",command_type)
			# print("options :",options)
			# print("parameters :",parameters)

#########################################################################################

	def replace_path(self, path):
		list_keys = list(self.path_mapper.mapping_dict.keys())
		for key in list_keys:
			old = key
			new = self.path_mapper.mapping_dict[key]
			path = path.replace(old, new)
		return path
		

#########################################################################################

	def get_new_command(self, command, command_type, options, parameters):
		if command_type == 'scp':
			source = parameters[0]
			destination = parameters[1]
			new_destination = self.replace_path(destination)
			if new_destination != destination:
				new_command = f'/*X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ \nx "scp {source} {new_destination}";\n'
			else:
				new_command = f'/*X "{command}"; /* EY COMMENT: Command commented because path mapping was not found */\n'

		elif command_type in ['cd', 'umask', 'kill', 'chmod']:
			new_command = f'/*X "{command}"; /* EY COMMENT: Command was commented as per project requirement.*/\n'

		elif command_type == 'zip':
			destination = parameters[0]
			source = parameters[1]
			filename = source.split('/')[-1]
			new_command = f'''/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ \nfilename xfile "{source}" recfm=n;
filename zfile zip "{destination}.gz" compression=9 member="{filename}" recfm=n;
%let rc = %sysfunc(fcopy(xfile, zfile));\n
'''
		elif command_type == 'gzip':
			source = parameters[0]
			filename = source.split('/')[-1]
			new_command = f'''/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ 
filename xfile "{source}" recfm=n;
filename zfile zip "{source}" compression=9 member="{filename}" recfm=n;
%let rc = %sysfunc(fcopy(xfile, zfile));\n
'''
		elif command_type == 'unzip':
			match = re.search(r'unzip\b.*?\s([^\s]+)\s+-d\s+([^\s]+)', command)
			zip_file_name = match.group(1)
			target_path = match.group(2)

			if '/' in zip_file_name:
				zip_file_name = zip_file_name.rsplit('/', 1)[1]

			new_command = f'/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ \n%unzip_files({target_path}, {zip_file_name});\n'
			
#        destination = parameters[0]
#        source = parameters[1]
#        unzipped_file = destination.split('/')[-1]
#        new_command = f'''%let upath = {destination};
#        %let path = {source};

# filename xl "&upath";
# filename zfile zip "&path" member="{unzipped_file}" recfm=n;

# data _null_;
#     infile zfile lrecl=256 recfm=F length=length eof=eof unbuf;
#     file xl lrecl=256 recfm=N;
#     input;
#     put _infile_ $varying256. length;
#     return;
# eof:
#     stop;
# run;\n
#'''
#		elif command_type == 'tar':
#        destination = parameters[0]
#        source = parameters[1]
#        filename = source.split('/')[-1]
#        new_command = f'''filename xfile "{source}" recfm=n;
#        filename zfile zip "{destination}" compression=9 member="{filename}" recfm=n;
#        %let rc = %sysfunc(fcopy(xfile, zfile));\n
#'''
			elif command_type == 'mkdir':
				newfolder = parameters[0]
				new_command = f'''/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ 
%let folder_name = {newfolder};
%let folder_path = %sysfunc(pathname(.));
%let rc = %sysfunc(dcreate(&folder_name, &folder_path));\n
'''
			elif command_type == 'cp':
				source = parameters[0].rsplit('/',1)[0]
				filename = parameters[0].rsplit('/',1)[1]
				destination = parameters[0].rsplit('/',1)[1]
				destination = self.replace_path(destination)
				new_command = f'/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/ %copy_files({source}, {destination}, {filename});\n'
		
#			        source = parameters[0]
#					destination = parameters[1]
#        			new_destination = self.replace_path(destination)
#     				new_command = f'''filename source "{source}";
# filename trgt "{new_destination}";
# %let rc = %sysfunc(fcopy(source, trgt));\n
# '''		

			elif command_type == 'mv':
				source = parameters[0]
				destination = parameters[1]
				new_destination = self.replace_path(destination)
				new_command = f'''/* X "{command}"; /* EY COMMENT: Command was replaced with the following:*/
filename source "{source}";
filename trgt "{new_destination}";
%let rc = %sysfunc(fcopy(source, trgt));
%let rc1 = %sysfunc(fdelete(source));\n
'''
			else:
				new_command = f'/* X "{command}"; /* EY comment: X command not handled! */\n'

			return new_command

#########################################################################################

	def get_new_command_from_combination(self, command):
		if 'cd' in command and 'zip' in command:
			cd_command = command.split(";")[0]
			zip_command = command.split(";")[1]
			_, _, cd_param = parse_linux_command(cd_command)
			_, _, zip_param = parse_linux_command(zip_command)
			dest_folder = cd_param[0]
			destination = zip_param[0]
			source = zip_param[1]
			new_command = f'''filename xfile "{dest_folder}/{source}" recfm=n;
filename zfile zip "{dest_folder}/{destination}.zip" member="{source}" recfm=n;
%let rc = %sysfunc(fcopy(xfile, zfile));\n'''
		else:
			new_command = "/* Unhandled command /*{command}*/\n"
		return new_command

#########################################################################################

	def export_sas_output(self, output_file, lines):
		try:
			with open(output_file, 'w', encoding="utf8") as file:
				file.writelines(lines)
		except: pass
		# print(f"New SAS file at: {output_file}")

#########################################################################################

	def run_one(self, sas_input_path, sas_output_path, replace=False):
		
		print(sas_input_path)
		fix_file_encoding(sas_input_path)
		self.get_lines_from_file(sas_input_path)

		# Process statements with path assignment
		modified_lines = self.process_sas_file_paths(sas_input_path, sas_output_path)
		modified_lines = self.process_x_commands(modified_lines, sas_input_path, sas_output_path)

		output_file_exists = os.path.exists(sas_output_path)
		if (not output_file_exists) or (output_file_exists & replace):
			# Create the corresponding subfolders in the output directory
			out_dir = os.path.dirname(sas_output_path)
			os.makedirs(out_dir, exist_ok=True)
			self.export_sas_output(sas_output_path, modified_lines)

#########################################################################################

    def process_x_commands(self, modified_lines, sas_input_path, sas_output_path):
        # Process statements with x commands
        for line_number, line in enumerate(modified_lines):
            # Extract the command, source file, and destination from the Xcommand column
            # xcommand = line.lower()

            if line.strip().startswith(('x ', 'X ')):
                new_command = self.process_x_command_one_line(line, sas_input_path, sas_output_path, line_number)
                # new_command = 'A command that replaces the x command \n and contains a carriage return'
                modified_lines[line_number] = new_command
        return modified_lines

#########################################################################################

	def run_all(self, replace=True):
			# Create the output folder if it doesn't exist
			if os.path.isdir(self.output_dir):
				print(f"The path {self.output_dir} already exists.")
			else:
				try:
					os.makedirs(self.output_dir)
				except:
					print(f"Could not create path {self.output_dir}")

			# Run through the current folder and all subfolders
			for root, dirs, files in os.walk(self.input_dir):
				# print(root)
				sas_files = get_sas_files(root, self.input_dir, files)
				for sas_file in sas_files:
					sas_input_path = os.path.join(root, sas_file)
					# print(sas_input_path)
					file_relative_path = os.path.relpath(sas_input_path, self.input_dir)
					sas_output_path = os.path.join(self.output_dir, file_relative_path)
					if "autoexec" in sas_file.lower():
						target_directory = os.path.dirname(sas_output_path)
						if not os.path.exists(target_directory):
							os.makedirs(target_directory)
						shutil.copy(sas_input_path, sas_output_path)
					else:
						self.run_one(sas_input_path, sas_output_path, replace)
						
#########################################################################################
# The Code Migration Execution class
#########################################################################################

class CodeMigrationExecution():

    def __init__(self, input_dir_list=None, output_dir_list=None, path_mapping_file=None):

		current_dir = os.path.dirname(os.path.realpath(__file__))

        if input_dir_list == None:
            self.input_dir_list = [os.path.join(current_dir, 'data', 'input')]
            self.output_dir_list = [os.path.join(current_dir, 'data', 'output')]
            self.path_mapping_file = os.path.join(current_dir, 'data', 'path_mappings.csv')

        else:
            self.input_dir_list = input_dir_list
            self.output_dir_list = output_dir_list

			self.path_mapping_file = os.path.join(current_dir, 'mappings', path_mapping_file)

        self.run()

    def run(self):
	
        for i in range(len(self.input_dir_list)):
            input_dir = self.input_dir_list[i]
            output_dir = self.output_dir_list[i]
            report_path = os.path.join(output_dir, 'execution_report_path.csv')
            report_path_x = os.path.join(output_dir, 'execution_report_x_command.csv')
            fieldnames = ['mapping_file', 'path', 'name', 'sas_input_path', 'sas_output_path',
                          'command', 'command_line', 'path_line', 'line', 'hrd_coded_path',
                          'new_path', 'changed', 'has_comment', 'timestamp']
            fieldnames_x = ['mapping_file', 'path', 'name', 'sas_input_path', 'sas_output_path', 'command_type', 'xcommand', 
							'xcommand_category', 'line_number', 'new_command', 'has_comment', 'timestamp']

            path_mapper = PathMapper(self.path_mapping_file)
            report = ReportGenerator(report_path, fieldnames)
            report_x = ReportGenerator(report_path_x, fieldnames_x)
            sas_processor = SasProcessor(input_dir, output_dir, path_mapper, report, report_x)
            sas_processor.run_all()
            sas_processor.report.export_to_csv()
            sas_processor.report_x.export_to_csv()
            self.filter(report)


    def filter(self, report):
        import pandas as pd
        report_path = report.report_path
        df = pd.read_csv(report_path, encoding='latin-1')
        df = df[
            (df.has_comment == 'No') &
            (~df.line.str.contains('&path_')) &
            (~df.line.str.contains('&PATH_')) &
            (~df.line.str.contains('&sys_')) &
            (~df.line.str.contains('&app_')) &
            (~df.line.str.contains('sysfunc')) &
            (~df.line.str.contains('/source2')) &
            (df.hrd_coded_path != 'l') &
            (df.hrd_coded_path != '_prefix') &
            (df.hrd_coded_path != '/') &
            (df.hrd_coded_path != 'liste') &
            (df.hrd_coded_path != 'instant') &
            (df.hrd_coded_path.str.len() > 6) &
            (~df.hrd_coded_path.astype(str).str.contains('\.'))
        ]

        df.to_csv(report_path.replace('.csv', '_filtered.csv'), encoding='latin-1', index=False)


