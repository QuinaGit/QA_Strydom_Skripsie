from attendance.models                  import Attendance_Logs, Sessions, Device
from django.contrib.auth.models         import User
from django.contrib.auth                import authenticate
from django.core.files.uploadhandler    import FileUploadHandler

from datetime                           import datetime
from dateutil.parser                    import parse

# attendence_data_row = { 
#   'usnumber'      :None, 
#   'datetime'      :None,
#   'name'          :None,
#   'session_id'    :None
#   }

# session_data_row = { 
#   'id'                :None,
#   'start_datetime'    :None,
#   'end_datetime'      :None,
#   'scan_count'        :None,
#   'session_id'        :None, 
#   'lecturer'       :None
#   }

# device_data_row = { 
#   'unit_name'         :None,
#   'software_version'  :None,
#   'last_update'       :None 
#   }

attendence_data_row = [None,None,None,None]
session_data_row    = [None,None,None,None,None,None]
device_data_row       = [None,None,None]
EXIT_SUCCESS        = True
EXIT_FAILURE        = False

def handle_uploaded_file(f):
    try:
        data_mark = 0
        for chunk in f.chunks():
            data_set = chunk.decode('UTF-8')
            rows = data_set.split('\n')
            line_count = 0

            for row in rows:
                if row == "":
                    data_mark +=1
                    #? break # continue rather ?
                    continue
                line_count += 1
                fields = row.split(',') #? or ';' ??

                # attendance device info
                if data_mark == 0:
                    
                    # split data into object array 
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        device_data_row[i] = field
                        i+=1

                    # format date string
                    dt = parse(device_data_row[2])
                    format_date = dt.strftime("%Y-%m-%d")

                    # save data to database
                    device_info = Device(
                        unit_name           = device_data_row[0], 
                        software_version    = device_data_row[1], 
                        last_update         = format_date
                        )

                    check = Device.objects.filter(unit_name=device_data_row[0]).first()
                    if check == None:
                        device_info.save()
                    else:
                        check.software_version = device_data_row[1]
                        check.last_update = format_date
                        check.save(update_fields=['software_version','last_update'])

                # session table data
                elif data_mark == 1:
                    
                    # split data into object array 
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        session_data_row[i] = field
                        i+=1

                    # authenticate foreign key user
                    lec_us1 = session_data_row[5]
                    try:
                        user1 = User.objects.get(username=lec_us1) 
                    except:
                        continue

                    # format start date string
                    dt = parse(session_data_row[1])
                    format_date1 = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # format end date string
                    dt = parse(session_data_row[2])
                    format_date2 = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # save data to database
                    session1 = Sessions(
                        start_datetime  = format_date1,
                        end_datetime    = format_date2,
                        scan_count      = session_data_row[3],
                        session_id      = session_data_row[4],
                        lecturer     = user1
                        )
                    

                    # check if 
                    check = Sessions.objects.filter(end_datetime=session1.end_datetime,session_id=session1.session_id)
                    if check.first() == None:
                        session1.save()

                # attendance logs table data
                elif data_mark == 2:
                    # split data into object array  
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        attendence_data_row[i] = field
                        i+=1

                    # authenticate foreign key session
                    sesh1 = attendence_data_row[3]
                    try:
                        session = Sessions.objects.get(session_id=sesh1)
                    except:
                        continue

                    # format date string
                    dt = parse(attendence_data_row[1])
                    format_date = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # save data to database
                    log1 = Attendance_Logs( 
                        usnumber    = attendence_data_row[0], 
                        date    = format_date,
                        name        = attendence_data_row[2],
                        session_id  = session
                        )
                    
                    check = Attendance_Logs.objects.filter(usnumber=log1.usnumber, session_id=log1.session_id)
                    if check.first() == None:
                        log1.save()

        return EXIT_SUCCESS
    except:
        return EXIT_FAILURE


