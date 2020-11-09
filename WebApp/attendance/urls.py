from django.urls import path
from .views import LogsListView, LogsLectureView
from . import views


urlpatterns = [
    path('', LogsListView.as_view(), name='attendance-raw'),                    # home page - raw logs
    path('lecture/', LogsLectureView.as_view(), name='attendance-lecture'),     # home page - lecture logs
    path('upload/', views.upload_file, name='attendance-upload'),       # home page - upload logs    
    path('upload/success/', views.upload_success, name='attendance-upload-success'),       # home page - upload logs
    path('about/', views.about, name='attendance-about'),       # about page
]
