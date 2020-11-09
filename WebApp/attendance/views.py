from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Attendance_Logs, Sessions
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
from .uploads import handle_uploaded_file

class LogsListView(LoginRequiredMixin, ListView):
    template_name = 'attendance/attendance_logs_raw.html' #<app>/<moddel>_<viewtype>.html
    context_object_name = 'data'
    logs = Attendance_Logs.objects.all().order_by('-date')[0:200]
    queryset = {
            'logs': logs
        }

class LogsLectureView(LoginRequiredMixin, ListView):
    template_name = 'attendance/attendance_logs_lecture.html'
    context_object_name = 'data'
    logs = Attendance_Logs.objects.all().order_by('-date')
    session = Sessions.objects.all().order_by('-start_datetime')

    queryset = {
        'session': session,
        'logs': logs
    }


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, ' This is not a CSV file', "messages alert alert-warning" )
            else:
                if handle_uploaded_file(csv_file):
                    messages.success(request, "Data saved to database", "messages alert alert-success" )
                else:
                    messages.error(request, "Upload failed! File might be corrupt.", "messages alert alert-danger" )
    else:
        form = UploadFileForm()
    return render(request, 'attendance/attendance_logs_upload.html', {'form': form})

@login_required
def upload_success(request):
    return render(request, 'attendance/attendance_logs_upload_success.html', {'title': 'Upload Success'})

def about(request):
    return render(request, 'attendance/about.html', {'title': 'About'})