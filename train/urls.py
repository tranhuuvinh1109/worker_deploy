from django.urls import path
from . import views

urlpatterns = [
    path('train/', views.ReceiveAPI.as_view(), name='train'),
    path('upload/', views.UploadAPI.as_view(), name='train'),
]
