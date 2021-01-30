from attendance.models                  import Logs, Sessions, Device, ClassList
from django.contrib.auth.models         import User
from django.contrib.auth                import authenticate
from django.core.files.uploadhandler    import FileUploadHandler
from django.utils                       import timezone

from datetime                           import datetime
from dateutil.parser                    import parse
import re

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

def handle_attendance_file(f):

    try:
        device_name = None
        data_mark = 0
        print("---handle_uploaded_file---")
        for chunk in f.chunks():
            data_set = chunk.decode('UTF-8')
            rows = re.split('\r?\n',data_set)
            line_count = 0
            
            #print("---data_set:",data_set,"---")
            #print("---rows:",rows,"---")

            for row in rows:
                if row == "":
                    data_mark +=1
                    #? break # continue rather ?
                    continue
                line_count += 1
                fields = re.split(';|,',row) #? or ';' ??

                #! attendance device info 
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

                    # save device name for later
                    device_name = device_data_row[0]

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

                #! session table data
                elif data_mark == 1:
                    
                    # split data into object array 
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        session_data_row[i] = field
                        
                        print("---field",i,":",field,"---")
                        i+=1

                    # authenticate foreign key user
                    lec_us1 = session_data_row[1]
                    try:
                        user1 = User.objects.get(username=lec_us1) 
                    except:
                        continue
                    
                    # authenticate foreign key device
                    try:
                        dev1 = Device.objects.get(unit_name=device_name) 
                    except:
                        continue

                    # format start date string
                    dt = parse(session_data_row[2])
                    format_date1 = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # format end date string
                    dt = parse(session_data_row[3])
                    format_date2 = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # save data to database
                    session1 = Sessions(
                        start_datetime  = format_date1,
                        end_datetime    = format_date2,
                        session_id      = session_data_row[0],
                        lecturer        = user1,
                        device          = dev1
                        )
                    print("--session1=",session1)

                    # check if entry exists
                    check = Sessions.objects.filter(
                        end_datetime    =session1.end_datetime,
                        session_id      =session1.session_id
                        )
                    print("--session:")
                    print(session1.start_datetime)
                    print(session1.end_datetime)
                    print(session1.session_id)
                    print(session1.lecturer)
                    print(session1.device)

                    if check.first() == None:
                        session1.save()
                    print("--after save", check.first())

                #! attendance logs table data
                elif data_mark == 2:
                    print("--data_mark",data_mark,": fields:",fields,"---")      #!only for debug
                    
                    # split data into object array  
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        attendence_data_row[i] = field
                        print("---field",i,":",field,"---")      #!only for debug
                        i+=1

                    # authenticate foreign key session
                    sesh1 = attendence_data_row[0]
                    try:
                        session = Sessions.objects.get(session_id=sesh1)
                    except:
                        continue

                    # format date string
                    dt = parse(attendence_data_row[2])
                    format_date = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # save data to database
                    log1 = Logs( 
                        usnumber    = attendence_data_row[1], 
                        date        = format_date,
                        session     = session
                        )
                    print("log1=",log1)
                    
                    check = Logs.objects.filter(
                        usnumber    =log1.usnumber, 
                        session  =log1.session_id
                        )
                    if check.first() == None:
                        log1.save()

        return EXIT_SUCCESS
    except:
        return EXIT_FAILURE

def handle_classlist_file(f):

    try:
        print("---handle_classlist_file---")

        for chunk in f.chunks():
            data_set = chunk.decode('UTF-8')
            #rows = data_set.split('\n')
            line_count = 0
            
            print("---data_set:",data_set,"---")
            #print("---rows:",rows,"---")

            print("---split_rows:",re.split('\r?\n+',data_set))

            for row in re.split('\r?\n+',data_set):
                if row == "":
                    continue
                line_count += 1
                fields = re.split(';|,',row) #? or ';' ??
                print("---fields:",fields,"---")

                print("---fields[0]:",fields[0],"---")
                print("---fields[1]:",fields[1],"---")

                #validate us number
                regex = re.compile('^([0-9]{8})$', re.I)
                match = regex.match(str(fields[0]))
                if not bool(match):
                    continue

                #validate name
                regex = re.compile('^([A-Za-z -]{2,50})$', re.I)
                match = regex.match(str(fields[1]))
                if not bool(match):
                    continue
            
                # save data to database
                student_info = ClassList(
                    usnumber    = fields[0],
                    name           = fields[1]
                    )
                print("student_info:",student_info)

                check = ClassList.objects.filter(usnumber=fields[0]).first()
                if check == None:
                    student_info.save()
                else:
                    check.name = fields[1]
                    check.last_modified = timezone.now
                    check.save(update_fields=['name','last_modified'])

        return EXIT_SUCCESS
    except:
        return EXIT_FAILURE