import chardet
import pandas as pd
import os

class ConvertSasCodeUtf:
    """
    This class helps convert SAS code files to UTF-8 encoding and detect the original encoding.
    """
    def __init__(self, path, output):
        """
        Initializes the class with file path, filename, and output path.

        Args:
            path: Path to the SAS code file.
            filename: Name of the SAS code file.
            output: Path to save the converted file (optional).
        """
        self.path = path
        self.output = output

    def run(self):
        """
        Runs the encoding detection and conversion process.
        """

        self.filename= self.get_sas_filenames()
        print(self.filename)

        dict_encoding={"item":[],"input_format":[],"output_format":[]}
        df = pd.DataFrame.from_dict(dict_encoding)

        for file in self.filename:
            print(self.path + "\\\\" + file)
            encoding= self.detect_encoding(file = file )
            print(encoding)
            self.convert_sas_file(file, encoding, file )

            encoding_out = self.detect_encoding(file = file )
            print(encoding_out)

            dict_encoding={"item":[file], "input_format":[encoding],"output_format":[encoding_out]}
            df_temp = pd.DataFrame.from_dict(dict_encoding)
            df = pd.concat([df, df_temp])

        return df


    @staticmethod
    def convert_sas_file(source_file, encoding, target_file):
        """This function converts a SAS code file from Latin-1 encoding to UTF-8 encoding.
        Args: source_file: Path to the source file in Latin-1 encoding.
              target_file: Path to save the converted file in UTF-8 encoding."""
        
        with open(source_file, 'r', encoding=encoding) as source:
            sas_code = source.read()
        print(target_file)
        # Write the content to a new file in UTF-8 encoding
        with open(target_file, 'w', encoding='utf-8') as target:
            target.write(sas_code)


    def get_sas_filenames(self):
        """Gets all filenames with the .sas extension from a specified directory.
        Args:
            folder_path: Path to the directory containing SAS files.
        Returns:
            A list of filenames (strings) with the .sas extension."""
        sas_filenames = []
        for filename in os.listdir(self.path):
            if filename.lower().endswith(".sas"): # Check for lowercase .sas extension
                print(filename)
            if filename.lower().endswith(".cfg"): # Check for lowercase .sas extension
                sas_filenames.append(filename)
        for root, dirs, files in os.walk(self.path):
            dirs = [d for d in directories]
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                for filename in os.listdir(dir_path):
                    if filename.lower().endswith((".sas",".cfg",".ksh")):
                        file_path = os.path.join(dir_path, filename)
                        print(file_path)
                        sas_filenames.append(file_path)
            files = os.listdir(self.path)
            for filename in files:
                if filename.lower().endswith((".sas",".cfg",".ksh")):
                    file_path = os.path.join(self.path, filename)
                    print(file_path)
                    sas_filenames.append(file_path)
        return sas_filenames

    @staticmethod
    def detect_encoding(file):
        """
        This function attempts to detect the encoding of a file using chardet library.
        Args:
            filename: Path to the SAS code file.
        Returns:
            The detected encoding if successful, None otherwise.
        """

        with open(file, 'rb') as f:
            rawdata = f.read()
        return chardet.detect(rawdata)['encoding']






