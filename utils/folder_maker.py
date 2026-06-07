import os

def create_data_folders(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path + "/"