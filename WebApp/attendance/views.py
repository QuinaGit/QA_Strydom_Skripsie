from django.shortcuts               import render
from django.views.generic           import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins     import LoginRequiredMixin
from django.contrib                 import messages
from django.db.models               import Count
from .models                        import Logs, ClassList #, Sessions, Device
from .forms                         import UploadAttendanceFileForm, UploadClasslistFileForm

# function to handle an uploaded file.
from .uploads                       import handle_attendance_file, handle_classlist_file

class LogsListView(LoginRequiredMixin, ListView):
    template_name = 'attendance/attendance_logs_raw.html' #<app>/<moddel>_<viewtype>.html
    context_object_name = 'data'
    logs = Logs.objects.all().order_by('-date')
    mynames = ClassList.objects.all()
    queryset = {
            'logs': logs,
            'mynames': mynames
        }
    

class LogsLectureView(LoginRequiredMixin, ListView):
    template_name = 'attendance/attendance_logs_lecture.html'
    context_object_name = 'data'
    logs = Logs.objects.all().order_by('-date')
    mynames = ClassList.objects.all()
    sessioncnt = Logs.objects.values('session__session_id','session__lecturer') \
                    .annotate(session_count=Count('session__session_id')) \
                    .order_by('-session__session_id')
    queryset = {
            'logs': logs,
            'sessioncnt':sessioncnt,
            'mynames': mynames
        }


class ClassListView(LoginRequiredMixin, ListView):
    template_name = 'attendance/classlist.html' #<app>/<moddel>_<viewtype>.html
    context_object_name = 'data'
    combinedlist = ClassList.objects.all().order_by('usnumber')
    queryset = {
            'combinedlist': combinedlist
        }


@login_required
def upload_logs_file(request):
    if request.method == 'POST':
        form = UploadAttendanceFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, ' This is not a CSV file', "messages alert alert-warning" )
            else:
                if handle_attendance_file(csv_file):
                    messages.success(request, "Data saved to database", "messages alert alert-success" )
                else:
                    messages.error(request, "Upload failed! File might be corrupt.", "messages alert alert-danger" )
    else:
        form = UploadAttendanceFileForm()
    return render(request, 'attendance/attendance_logs_upload.html', {'form': form})


@login_required
def upload_logs_success(request):
    return render(request, 'attendance/attendance_logs_upload_success.html', {'title': 'Upload Success'})


@login_required
def upload_classlist_file(request):
    if request.method == 'POST':
        form = UploadClasslistFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, ' This is not a CSV file', "messages alert alert-warning" )
            else:
                if handle_classlist_file(csv_file):
                    messages.success(request, "Data saved to database", "messages alert alert-success" )
                else:
                    messages.error(request, "Upload failed! File might be corrupt.", "messages alert alert-danger" )
    else:
        form = UploadClasslistFileForm()
    return render(request, 'attendance/attendance_classlist_upload.html', {'form': form})


def about(request):
    return render(request, 'attendance/about.html', {'title': 'About'})