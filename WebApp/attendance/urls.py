from django.urls import path
from .views import LogsListView, LogsLectureView, ClassListView
from . import views


urlpatterns = [
    path('', LogsListView.as_view(), name='attendance-raw'),                        # home page - raw logs
    path('lecture/', LogsLectureView.as_view(), name='attendance-lecture'),         # home page - lecture logs
    path('classlist/', ClassListView.as_view(), name='classlist'),                  # home page - classlist
    path('upload-logs/', views.upload_logs_file, name='attendance-upload'),         # home page - upload logs    
    path('upload-logs/success/', views.upload_logs_success, name='attendance-upload-success'),       # home page - upload logs
    path('upload-classlist/',views.upload_classlist_file, name='classlist-upload'), # home page - upload class list
    path('about/', views.about, name='attendance-about'),                           # about page
]
