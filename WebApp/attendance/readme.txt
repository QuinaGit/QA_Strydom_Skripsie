# Activate Virtual environment in VS Code:

C:\Users\Quintin\Documents\Quintin_S\Universiteit\448_Skripsie\WebApp\sucs_web_env\Scripts\activate
python manage.py runserver



> python manage.py shell

>>> from attendance.models import Attendance_Logs, Sessions          # import objects
>>> from django.contrib.auth.models import User
>>> from users.models import Profile

>>> User.objects.all()                                               # see all instances in object
<QuerySet [<User: 12345678>, <User: 10000000>]>

>>> User.objects.filter(username='12345678').first()
<User: 12345678>

>>> user = User.objects.get(id=1)
>>> user
<User: 12345678>
>>> user.username
'12345678'


sesh = Sessions(start_datetime='2020-08-31 12:51:11', end_datetime='2020-08-31 13:01:11', scan_count = 3, session_id = '20200831125000', lecturer=user)
sesh.save()

>>> log_1 = Attendance_Logs(name='P Pienaar', usnumber='20123456', date='2020-08-31 12:52:11', session_id=sesh)
>>> log_1.save()
>>> log_2 = Attendance_Logs(name='P Zietsman', usnumber='20123457', date='2020-08-31 12:53:11', session_id=sesh)
>>> log_2.save()
>>> log_3 = Attendance_Logs(name='A Strydom', usnumber='20123458', date='2020-08-31 12:54:11', session_id=sesh)
>>> log_3.save()
                                                   
?>>> sesh.attendance_logs_set.create(name='P Pienaar', usnumber='20123456', date='2020-08-31 12:52:11')                    # make post through an attribute



----------------------------------------------------------------------------------------
----------Import using JSON----(old)---------------------------------------------------------

$ python manage.py shell
>>>import json
>>>from attendance.models import Lecturer, Attendance_Logs 
>>>with open('attendance/logs.json') as f:
... logs_json = json.load(f)
...
>>>for logs in logs_json:
... logs = Attendance_Logs(name=logs['name'], usnumber=logs['usnumber'], module=logs['module'], lecturer_id=logs['lecturer_id'])
... logs.save()
...
>>> exit()