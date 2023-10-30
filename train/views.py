# from rest_framework.response import Response
# from rest_framework.views import APIView
# import os
# from . import unzip_extract
# from . import train_model

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')
# ZIP_DIR = os.path.join(BASE_DIR, 'assets/zip')

# class TrainAPI(APIView):
#     def post(self, request):
#         # unzip
#         if request.method == 'POST' and request.data.get('file'):
#             print('===========================')
#             user_id = request.data['user_id']
#             project_id = request.data['project_id']
#             file = request.data.get('file')
#             new_name = 'project_' + str(project_id) + '-' + str(user_id)
            
#             if file.content_type == 'application/zip':
#                 file_path = os.path.join(ZIP_DIR, new_name+'.zip')
#                 with open(file_path, 'wb') as destination:
#                     for chunk in file.chunks():
#                         destination.write(chunk)
#                 print('>>', file)     
#                 result = unzip_extract.unzip_and_extract(file_path, new_name)
#                 if result == 1:
#                     print('unzip success')
#                     return Response({'message': 'successfuly'}, status=200)
#                 else:
#                     print('unzip fail')
#                     return Response({'message': 'fail'}, status=400)
            
            
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os

from train.uploadToFirebase import Firebase
from . import unzip_extract
from . import train_model
import threading
import queue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')
ZIP_DIR = os.path.join(BASE_DIR, 'assets/zip')

class TrainAPI(APIView):
    def post(self, request):
        if request.method == 'POST' and request.data.get('file'):
            user_id = request.data['user_id']
            project_id = request.data['project_id']
            file = request.data.get('file')
            new_name = 'project_' + str(project_id) + '-' + str(user_id)
            
            if file:
                file_path = os.path.join(ZIP_DIR, new_name + '.zip')
                
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                task_queue = queue.Queue()
                task_queue.put((file_path, new_name))
                processing_thread = threading.Thread(target=self.process_queue, args=(task_queue,))
                processing_thread.start()
                return Response({'message': 'File uploaded and processing has started.',  'user_id': user_id}, status=200)
    
    def process_queue(self, task_queue):
        while not task_queue.empty():
            file_path, new_name = task_queue.get()
            result = unzip_extract.unzip_and_extract(file_path, new_name)
            if result == 1:
                print(f'Unzip successful for {new_name}')
            else:
                print(f'Unzip failed for {new_name}')
            task_queue.task_done()
class CreateProjectAPI(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        project_id = request.data.get('project_id')
        progress = 0
        status_text = 'waiting'
        link_drive = ''
        file = request.FILES.get("file")
        name = request.data.get("name")
        create_time = '2023'
        
        data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkDrive': '',
                'createAt': create_time,
                'name':name
            }
            # create in firebase project user:
        Firebase.setProject('user_1', project_id ,data_send)

        # unzip file
        flagExport = unzip_extract.UploadAndUnzip.saveZipFile(
            file, 'project_' + str(project_id) + '-' + str(user_id))

        if flagExport == 1:
            data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkDrive': '',
                'createAt': create_time,
                'name': name,
            }
            # create in firebase project user:
            Firebase.setProject(
                'user_'+user_id, project_id, data_send)
            response_data = {
                'message': 'Project created successfully',
                'data': ''
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Error when unzip file'}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({'message': 'Error when unzip file'}, status=status.HTTP_201_CREATED)
