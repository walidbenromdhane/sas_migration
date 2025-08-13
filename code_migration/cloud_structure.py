import os, csv
import shutil

class CloudStructure():
	
    def __init__(self, source_path, target_path, structure_mapping_file) -> None:
        self.source_path = source_path
        self.target_path = target_path
        self.structure_mapping_file = structure_mapping_file
        self.get_structure_map()
        self.run()


    def get_structure_map(self):
        self.structure_map = {}
        with open(self.structure_mapping_file, newline='', encoding='latin-1') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                old_path, new_path = row
                old_path_full = os.path.join(self.source_path, old_path.strip())
                new_path_full = os.path.join(self.target_path, new_path.strip())
                self.structure_map[old_path_full] = new_path_full

    def run(self):
        for root, dirs, files in os.walk(self.source_path):
            dirs = [d for d in dirs]
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                files = os.listdir(dir_path)
                try:
                    cloud_path = self.structure_map[dir_path]
                    for file in files:
                        file_path = os.path.join(dir_path, file)
                        print(file_path)
                        file_cloud_path = os.path.join(cloud_path, file)

                        # Ensure the destination directory exists, but only create it if it does not exist
                        destination_dir = os.path.dirname(file_cloud_path)
                        if not os.path.exists(destination_dir):
                            os.makedirs(destination_dir)

                        shutil.copy2(file_path, file_cloud_path)
                # except Exception as e:
                #     print(f"{e}")
                except: pass



