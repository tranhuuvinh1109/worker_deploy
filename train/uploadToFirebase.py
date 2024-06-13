import pyrebase

config = {
    "apiKey": "AIzaSyDXPvGl3y_IWGpU7GvixTL9uEuF0WAyNCk",
    "authDomain": "realtime-cnn.firebaseapp.com",
    "databaseURL": "https://realtime-cnn-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "realtime-cnn",
    "storageBucket": "realtime-cnn.appspot.com",
    "messagingSenderId": "856972582342",
    "appId": "1:856972582342:web:d4f6747a958fe848b7e6c7"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()

class Firebase:
    def setProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).set(data)
    def setProcessModel(create_at, data):
        database.child("vcare").child(create_at).set(data)
        
    def updateProject(user_id, project_id, data):
        database.child("data").child(user_id).child(project_id).update(data)
    def updateImage( data):
        database.child("image").set(data)