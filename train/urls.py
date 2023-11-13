from django.urls import path
from . import views

urlpatterns = [
    path('train/', views.CreateProjectAPI.as_view(), name='train'),
    path('upload/', views.UploadAPI.as_view(), name='train'),
    path('check/', views.CheckAPI.as_view(), name='train'),
    path('ocr/', views.TestOCR.as_view(), name='train'),
    path('list/', views.ListFileAPI.as_view(), name='ListFileAPI'),
    path('realtime/', views.RealtimeAPI.as_view(), name='ListFileAPI'),
]
