import pyrebase
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from time import sleep
import os
import threading
import random
import shutil

from train.uploadToFirebase import Firebase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNZIP_DIR = os.path.join(BASE_DIR, 'assets/unzip')
ZIP_DIR = os.path.join(BASE_DIR, 'assets/zip')
MODEL_DIR = os.path.join(BASE_DIR, 'assets/model')

base_data_dir = UNZIP_DIR
img_width, img_height = 128, 128
batch_size = 32

img_width, img_height = 128, 128
batch_size = 32

user_id = ''
project_id = ''
projects_name = []
index_start = 0

class TrainModel:
    def train(self, train_data_dir):
        global user_id, project_id, index_start
        user_id_training = 'user_' + user_id
        project_id_training = project_id
        data_send = {
                'status': 'training',
                'progress': '0',
                'linkDrive': ''
            }
        print(user_id_training, project_id_training, data_send)
        
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(img_width, img_height, 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        epochs = 3

        for epoch in range(epochs):
            progress = (epoch + 1) / epochs * 100
            data_send = {
                'status': 'training',
                'progress': progress,
'linkDrive': ''
            }
            Firebase.updateProject(user_id_training, project_id_training, data_send)
            model.fit(train_generator, epochs=1)
        save_name = 'project_'+project_id+'-'+user_id
        
        file_save_dir = os.path.join(MODEL_DIR, save_name+'.h5')
        
        # file_name = f'D:/Django/CNN/docker-cnn/model/{save_name}.h5'
        model.save(file_save_dir)
        # upload to Drive
        data_send = {
                'status': 'push to drive',
                'progress': '100',
                'linkDrive': ''
            }
        Firebase.updateProject(user_id_training, project_id_training, data_send)
        
        folder_container_train = base_data_dir + '/' + save_name
        
        # upload to firebase
        data_send = {
                'status': 'done',
                'progress': '100',
                'linkDrive': 'ssss'
            }
        Firebase.updateProject(user_id_training, project_id_training, data_send)
        print('done', index_start)
        index_start += 1

    def start_training(self, export_dir):
        parts = export_dir.split('_')[1].split('-')
        train_data_dir = os.path.join(base_data_dir, export_dir, 'train')
        global user_id, project_id, projects_name
        project_id = parts[0]
        user_id = parts[1]
        self.train(train_data_dir)

        print("All training completed.")

trainer = TrainModel()
