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
            parts = project_id.split('_')[1]
            create_at  = parts
            print('--25', create_at)
            data_send = {
                'status': 'extracting',
                'progress': '0',
                'linkModel': '',
                'createAt': create_at,
            }
            Firebase.setProcessModel(create_at, data_send)
            print(f"Unzipping project ---> {project_id}...", data_send,  os.path.join(BASE_DIR, 'assets/zip'))
            try:
                with unzip_lock:
                    ZIP_DIR2 = os.path.join(BASE_DIR, 'assets/zip', project_id, project_id+'.zip')
                    unzip(project_id, ZIP_DIR2)
                    if temp_queue:
                        temp_queue.pop(0)
                    trainer.start_training(project_id)
                    for temp_item in temp_queue:
                        temp_rar_file, temp_project_id = temp_item
                        ZIP_DIR3 = os.path.join(BASE_DIR, 'assets/zip', temp_project_id, temp_project_id+'.zip')
                        unzip(temp_project_id, ZIP_DIR3)
                    
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
            unzip_queue.put((zip_file_path, project_id))
        except: 
            return {
                "massage": "Error could not find zip file"
            }

        return 1

for i in range(num_worker_threads):
    worker = UnzipThread()
    worker.daemon = True
    worker.start()


def unzip( save_name, file_path):
    try:
        UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip/', save_name)
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
