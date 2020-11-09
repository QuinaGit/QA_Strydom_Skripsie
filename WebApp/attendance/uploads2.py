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
list_of_sessions = None

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
                    print("--blank row--")
                    #? break # continue rather ?
                    continue
                print("---row:",row,"---")                     #remove after debug 
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
                        print("---field",i,":",field,"---")
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
                    print("device_info=",device_info)

#####
                    # check = Device.objects.filter(unit_name=device_info['unit_name']).first()
                    # if check == None:
                    #     device_info.save()
                    # else:
                    #     check.software_version = device_info['software_version']
                    #     check.last_update = format_date
                    #     check.save(update_fields=['software_version','last_update'])
#####
                # session table data
                elif data_mark == 1:
                    
                    # split data into object array 
                    i = 0
                    for field in fields:
                        if i >= len(fields):
                            break
                        session_data_row[i] = field
                        print("---field",i,":",field,"---")
                        i+=1

                    # for authentication of foreign key user
                    lec_us1 = session_data_row[5]
                    
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
                        lecturer     = None
                        )
                    print("session1=",session1)
#####
#                     try:
#                         user1 = User.objects.get(username=lec_us1) 
#                     except:
#                         print("user-",lec_us1,"-not found")
#                         continue
#                     session1['lecturer'] = user1

#                     # check if 
#                     check = Sessions.objects.filter(start_datetime=format_date1,end_datetime=format_date2,scan_count=session_data_row[3],session_id=session_data_row[4])
#                     if check.first() == None:
#                         session1.save()
#####
                # attendance logs table data
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

                    # save for authentication of foreign key session
                    sesh1 = attendence_data_row[3]

                    # format date string
                    dt = parse(attendence_data_row[1])
                    format_date = dt.strftime("%Y-%m-%d %H:%M:%S")

                    # save data to database
                    log1 = Attendance_Logs( 
                        usnumber    = attendence_data_row[0], 
                        date    = format_date,
                        name        = attendence_data_row[2],
                        session_id  = None
                        )
                    print("log1=",log1)
#####
                    # # authenticate foreign key session
                    # try:
                    #     session = Sessions.objects.get(session_id=sesh1)
                    # except:
                    #     print("session",sesh1,"not found")
                    #     continue
                    
                    # log1['session_id'] = session

                    # check = Attendance_Logs.objects.filter(usnumber=log1['usnumber'], date=log1['date'], name=log1['name'], session_id=log1['session_id'])
                    # if check.first() == None:
                    #     log1.save()
#####       
    except:
        return EXIT_FAILURE
    else:

    #Device
        check = Device.objects.filter(unit_name=device_info['unit_name']).first()
        if check == None:
            device_info.save()
        else:
            check.software_version = device_info['software_version']
            check.last_update = format_date
            check.save(update_fields=['software_version','last_update'])


    #Session
        try:
            user1 = User.objects.get(username=lec_us1) 
        except:
            print("user-",lec_us1,"-not found")
            continue
        session1['lecturer'] = user1

        # check if 
        check = Sessions.objects.filter(start_datetime=session1['start_datetime'],end_datetime=formsession1['end_datetime']at_date2,scan_count=session1['scan_count'],session_id=session1['session_id'])
        if check.first() == None:
            session1.save()


    # Attendance_Logs
        # authenticate foreign key session
        try:
            session = Sessions.objects.get(session_id=sesh1)
        except:
            print("session",sesh1,"not found")
        
        log1['session_id'] = session

        check = Attendance_Logs.objects.filter(usnumber=log1['usnumber'], date=log1['date'], name=log1['name'], session_id=log1['session_id'])
        if check.first() == None:
            log1.save()


        return EXIT_SUCCESS
