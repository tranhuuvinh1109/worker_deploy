from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import os
from PIL import Image
import shutil
from train.uploadToFirebase import Firebase
from train.uploadAutoDrive import UploadAuto

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
                'linkModel': '',
                'createAt': project_id,
            }
        
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
                'linkModel': '',
                'createAt': project_id,
            }
            print('--78', project_id_training)
            Firebase.setProcessModel(project_id_training, data_send)
            model.fit(train_generator, epochs=1)
        save_name = 'project_'+project_id
        
        file_save_dir = os.path.join(MODEL_DIR, save_name+'.h5')
        
        model.save(file_save_dir)
        # upload to Drive
        data_send = {
                'status': 'saving model',
                'progress': progress,
                'linkModel': '',
                'createAt': project_id,
            }
        Firebase.setProcessModel( project_id_training, data_send)
        print('93--', project_id_training)
        # upload to firebase
        data_send = {
                'status': 'done',
                'progress': '100',
                'linkModel': os.path.join(MODEL_DIR, save_name+'.h5'),
                'createAt': project_id,
            }
        print('100--', project_id_training)
        Firebase.setProcessModel( project_id_training, data_send)
        index_start += 1

    def start_training(self, dataset_dir):
        parts = dataset_dir.split('_')[1]
        child_folder = os.listdir(os.path.join(base_data_dir, dataset_dir))[0]
        train_data_dir = os.path.join(base_data_dir, dataset_dir, child_folder,'train')
        global user_id, project_id, projects_name
        project_id = parts
        self.train(train_data_dir)

        print("All training completed.")

trainer = TrainModel()
