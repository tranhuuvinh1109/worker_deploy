from django.urls import path
from . import views

urlpatterns = [
    path('train/', views.CreateProjectAPI.as_view(), name='train'),
    path('upload/', views.UploadAPI.as_view(), name='train'),
]
