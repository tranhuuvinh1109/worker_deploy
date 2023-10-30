import os
import zipfile
from queue import Queue
import threading

from train.train_model import TrainModel
from train.uploadToFirebase import Firebase


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')
ZIP_DIR = os.path.join(BASE_DIR, 'assets/zip')
destination_dir = UNZIP_DIR
temp_queue = []

trainer = TrainModel()


class UnzipThread(threading.Thread):
    def run(self):
        while True:
            rar_file, project_id = unzip_queue.get()
            print(f"Unzipping project ---> {project_id}...")
            parts = project_id.split('_')[1].split('-')
            user_id  = parts[1]
            prj_id = parts[0]
            data_send = {
                'status': 'extracting',
                'progress': '0',
                'linkDrive': ''
            }
            Firebase.updateProject('user_'+user_id, prj_id, data_send)
            try:
                # Đảm bảo chỉ một luồng giải nén tại một thời điểm
                with unzip_lock:
                    unrar(rar_file, destination_dir +"/"+ temp_project_id)
                    # base_data_dir
                    base_data_dir = destination_dir 
                    print('export path => .....', base_data_dir + project_id)
                    os.remove(rar_file)
                    if temp_queue:
                        temp_queue.pop(0)
                    export_dir=project_id
                    trainer.start_training(export_dir=export_dir)
                    for temp_item in temp_queue:
                        temp_rar_file, temp_project_id = temp_item
                        unrar(temp_rar_file, destination_dir +"/"+ temp_project_id)
                    
                unzip_queue.task_done()
                
            except Exception as e:
                print(f'Failed to extract ZIP file for project {project_id}: {str(e)}')

unzip_queue = Queue()
unzip_lock = threading.Lock()
num_worker_threads = 1

class UploadAndUnzip():
    def saveZipFile(zip_file, project_id):
        project_dir = os.path.join(ZIP_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        zip_file_path = os.path.join(project_dir, project_id + '.zip')

        try:
            with open(zip_file_path, 'wb+') as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)
            print('...9999//.',zip_file_path)
        except: 
            print('>>>>>')
        
        print('...9999//.',zip_file_path)

        unzip_queue.put((zip_file_path, project_id))

        return 1

for i in range(num_worker_threads):
    worker = UnzipThread()
    worker.daemon = True
    worker.start()


def unrar( new_name, file_path):
    print('unzip ==>: ,',file_path , new_name)
    try:
        UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip/',new_name)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(UNZIP_DIR)
        return 1  
    except zipfile.BadZipFile:
        return 0
    except zipfile.LargeZipFile:
        return 0 
    except Exception as e:
        print(f"Error: {e}")
        return 0
