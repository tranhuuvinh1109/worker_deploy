import zipfile
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')


def unzip_and_extract(file_path, current_name, new_name):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(UNZIP_DIR)
        extracted_folder = os.path.join(UNZIP_DIR, current_name)
        new_extracted_folder = os.path.join(UNZIP_DIR, new_name)
        os.rename(extracted_folder, new_extracted_folder)
        return 1  
    except zipfile.BadZipFile:
        return 0
    except zipfile.LargeZipFile:
        return 0 
    except Exception as e:
        print(f"Error: {e}")
        return 0
