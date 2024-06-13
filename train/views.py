            
import base64
import pickle
import struct
import cv2
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os
from django.http import JsonResponse
from train.uploadToFirebase import Firebase
from . import unzip_extract
from . import train_model
import threading
import queue

from django.shortcuts import render
from django.http import HttpRequest

import easyocr



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')
ZIP_DIR = os.path.join(BASE_DIR, 'assets/zip')


from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

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
        create_time = request.data.get('create_time')
        
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

class RetrainModelAPI(APIView):
    def post(self, request):
        progress = 0
        status_text = 'waiting'
        file = request.FILES.get("file")
        create_time = request.data.get('create_time')
        
        data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkModel': '',
                'createAt': create_time,
            }
            # create in firebase project user:
        Firebase.setProcessModel(create_time ,data_send)

        # unzip file
        flagExport = unzip_extract.UploadAndUnzip.saveZipFile(
            file, 'retrain_' + str(create_time))

        if flagExport == 1:
            data_send = {
                'status': 'waiting',
                'progress': '0',
                'linkModel': '',
                'createAt': create_time,
            }
            Firebase.setProcessModel(
                create_time, data_send)
            response_data = {
                'message': 'Project created successfully',
                'data': ''
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Error when unzip file'}, status=status.HTTP_400_BAD_REQUEST)



class UploadAPI(APIView):
    def get(self, request):
        print(">>>DANG UP NE>>>>")
        file_path= 'D:/My Project/Django/DEPLOY/worker_deploy/assets/model/project_12-1.h5'
        file_name= 'vimmm'
        SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR,'client_secrets.json')
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        drive_service = build('drive', 'v3', credentials=credentials)


        folder_id = '1aAIkfZS-anf5E6M8uj5nUka5B8Iy4yQn'

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        if 'id' in file:
            file_id = file['id']
            file_url = "https://drive.google.com/file/d/" + file_id + "/view"
            # https://drive.google.com/file/d/15aZezP89eENIpUh5pQ-HjivtWXOj0uY_/view
            print("...up done...",file_url )
            return Response({"message": "done", "file_url": file_url}, status=status.HTTP_201_CREATED)
        else:
            print("...up fail..." )
            return Response({"message": "failed"}, status=status.HTTP_404_NOT_FOUND)
        

class RootAPI(APIView):
    def get(self, request):
        return JsonResponse({"message": "Hey this is my API running 🥳"})
    

class CheckAPI(APIView):
    def get(self, request):
        return Response({"message": "Hey this is my API running 🥳"}, status=status.HTTP_200_OK)
    

class TestOCR(APIView):
    def post(self, request):
        image_path = request.data.get('file')
        print('--->', image_path)
        
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_path)
        print('result ==> : ', result) 
        rs = [item[1] for item in result]


        return Response({"image_path": image_path, 'result': rs}, status=status.HTTP_200_OK)  

class ListFileAPI(APIView):
    def get(self, request):
        MEDIA_DIR = os.path.join(BASE_DIR, 'worker_deploy/media')
        all_files = os.listdir(MEDIA_DIR)
        print(all_files)

        return Response({"data": all_files}, status=status.HTTP_200_OK)  
    

class RealtimeAPI(APIView):
    def get(self,request):
        Firebase.setProject(10,4, {
            "user": "vinh"
        })
        return Response({"data": {
            "user": "vinh"
        }}, status=status.HTTP_200_OK)  
    
class StreamAPI(APIView):
    def get(self, request):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Đóng gói dữ liệu frame
            data = pickle.dumps(frame)
            data_length = len(data)
            data_packed = struct.pack("I", data_length) + data
            data_encoded = base64.b64encode(data_packed).decode('utf-8')
            # Gửi dữ liệu frame đến Firebase
            Firebase.updateImage(data_encoded)
            print("11")

           

        # Giải phóng tài nguyên
        cap.release()
        cv2.destroyAllWindows()

        return Response("Stream ended")