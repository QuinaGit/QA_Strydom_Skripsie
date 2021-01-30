#####################################################################
#   main.py                                                         #
#   Author: Quintin Strydom                                         #
#   Date Created: 13Aug2020                                         #
#   Created for: Skripsy Project                                    #
#       for Electronic- and Electrical Engineering                  #
#       at the University of Stellenbosch                           #
#   Under supervision of Prof. HdT Mouton                           #
#   Implemented on Raspberry Pi 3 Model A+                          #
#####################################################################
"""
    ----    ----    ----    ----    ----    ----    ----
   |    This application is run with the command:       |
   |          ./path/to/kivyrun path/to/main.py         |
    ----    ----    ----    ----    ----    ----    ----
"""

#####################################################################
#                             Imports                               #
#####################################################################
import datetime
import os
import sys
import subprocess
from time                   import time

from kivy.app               import App
from kivy.clock             import Clock
from kivy.config            import Config
from kivy.lang              import Builder
from kivy.properties        import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout   import FloatLayout
from kivy.uix.button        import Button
from kivy.uix.popup         import Popup
from kivy.uix.label         import Label

from sucsdb import Database
from rfidreader import SUCS_RFID
import settings as s
import rfid_auth_key as key




#####################################################################
##### # # # # #  #   #    Kivy GUI classes     #   #  # # # # # #####
#####################################################################



#####################################################################
#                     LectureLoginWindow class                      #
#####################################################################

class LectureLoginWindow(Screen):
    """ login window class
    RFID scanner activates on entry unless Settings.RFID_ENABLED = False.
    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    sc  = None     # SUCS_RFID onject
    
    # built-in kivy function: before entering the login window
    def on_pre_enter(self):
        s.APP_STATE = "LOGIN" 

        # activate rfid scanner
        #? if s.RFID_ENABLED: 
        #?     if self.sc:
        #?         print(type(self).__name__,"sc:",self.sc)                  #!Print
        #?     if not self.sc:
        #?         self.sc = SUCS_RFID(key=key.RFID_AUTH_KEY, block_addrs=key.RFID_BLOCK_ADDRS)
        #?         self.sc.start()
        #?         #self.sc.rfid_start_scan(scan_interval=s.RFID_READ_INTERVAL)
                
        #?         if self.sc:
        #?             print(type(self).__name__,"sc:",self.sc)                  #!Print

        #? # shedule event: check if a card has been scanned
        #? self.checkInfoSchedule = Clock.schedule_interval(self.checkInfo, s.SCAN_CHECK_INTERVAL)
        #? if not self.checkInfoSchedule.is_triggered:
        #?     self.checkInfoSchedule()
    
    # periodic routine: check if check if a card has been scanned
    def checkInfo(self, *args):
        info = self.sc.get_lastread_text()  #get (usnum, name) from database
        if not info == None:
            # test if valid lecturer
            if db.valid_lecturer(info[0]):
                # save data and go to main screen
                Clock.unschedule(self.checkInfo)
                s.ACTIVE_LECTURER = info
                self.loginBtn()
            else:
                self.popup_new_lecture()

    # login button is pressed or valid Lecturer card is scanned
    def loginBtn(self):
        if s.LOGIN_BYPASS:
            #? Clock.unschedule(self.checkInfo)
            s.ACTIVE_LECTURER = s.MANUAL_LECTURER

            # save data and go to main screen
            sm.current = "main"
            #? self.resetLogin()

    # popup: create new lecturer
    def popup_new_lecture(self):
        self.float_popup = FloatLayout()
        self.float_popup.add_widget(Label(        
            size_hint= [0.6, 0.4],
            text= "Do you want to register as a lecturer using this device?",
            font_size= 20,
            pos_hint= {"x":0.2, "top":1}
        ))
        self.float_popup.add_widget(Button(
            size_hint= [0.8, 0.2],
            text= "Yes",
            font_size= 35,
            pos_hint= {"x":0.1, "y":0.4},
            on_press=   lambda a:self.createNewLecrurer()
        ))
        self.float_popup.add_widget(Button(
            size_hint= [0.8, 0.2],
            text= "No",
            font_size= 35,
            pos_hint= {"x":0.1, "y":0.1},
            on_press=   lambda a:self.popupWindow.dismiss()
        ))
        self.popupWindow = Popup(content=self.float_popup, size_hint=(None,None), size=(400,400))
        self.popupWindow.open()

    # popup button method
    def createNewLecrurer(self, *args):
        if db.insert_lecturer(s.ACTIVE_LECTURER) < 0:
            print(type(self).__name__,"Failed to create new lecturer")                  #!Print
        else:
            print(type(self).__name__,"Successfully created lecturer:",s.ACTIVE_LECTURER)            #!Print
        self.popupWindow.dismiss()

    # log off application
    def logoffBtn(self):
        s.APP_STATE = "OFF"
        #? self.resetLogin()
        SUCSterminate()

    # reset class data
    def resetLogin(self):
        self.sc.rfid_stop_scan()
        print(type(self).__name__,"+++++Stop Scan")                     #!remove
        self.sc.close()
        self.sc = None


#####################################################################
#                         MainWindow class                          #
#####################################################################

class MainWindow(Screen):
    """ main window class
    Display application menu.

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    # username = ""
    # lecture_id = ""

    # widget variables for gui.kv 
    lbl_main_time   = ObjectProperty(None) 
    lbl_main_user   = ObjectProperty(None) 

    # built-in kivy function: before entering the main window
    def on_pre_enter(self, *args):
        s.APP_STATE = "MAIN"
        self.update_count = -1
        self.update_window()
        self.lbl_main_user.text = "Loged In: "+ str(s.ACTIVE_LECTURER)

        
        # shedule event: check if a card has been scanned
        self.updateWindowSchedule = Clock.schedule_interval(self.update_window, s.TIME_UPDATE_INTERVAL)
        if not self.updateWindowSchedule.is_triggered:
            self.updateWindowSchedule()

    # scan button method
    def scanBtn(self):
        sm.current = "scan"

    # list button method
    def listBtn(self):
        sm.current = "list"

    # scan button method
    def logoutBtn(self):
        sm.current = "login"

    # export button method
    def exportBtn(self):
        sm.current = "export"

    # method that keeps the time stamp updated 
    def update_window(self, *args):
        self.lbl_main_time.text = str(get_time())

#####################################################################
#                         ScanWindow class                          #
#####################################################################


class ScanWindow(Screen):
    """ main window class
    Activates rfid reader and stores scanned information to the database.

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    # widget variables for gui.kv 
    lbl_scan_count  = ObjectProperty(None)
    lbl_scan_time   = ObjectProperty(None)
    lbl_scan_msg    = ObjectProperty(None)
    btn_scan_back   = ObjectProperty(None)

    sc              = None     # SUCS_RFID onject

    # built-in kivy function: before entering the scan window
    def on_pre_enter(self, *args):
        s.APP_STATE = "SCAN"
        s.SESSION_ID = make_datetime_stamp()
        # save log session info
        self.session_start_time = get_datetime()
        # reset scan counter
        self.scan_counter = 0
        self.feedback = True

        # activate rfid reader in another thread
        if s.RFID_ENABLED:
            if self.sc:
                self.resetScan()
            self.sc = SUCS_RFID(key=key.RFID_AUTH_KEY, block_addrs=key.RFID_BLOCK_ADDRS)
            self.sc.start()
            self.sc.rfid_start_scan(scan_interval=s.RFID_READ_INTERVAL)
        
        # shedule event: update every TIME_UPDATE_INTERVAL seconds
        self.clkUpdateSchedule = Clock.schedule_interval(self.update_window_clk, s.TIME_UPDATE_INTERVAL)
        if not self.clkUpdateSchedule.is_triggered:
            self.clkUpdateSchedule()
        # shedule event: update every TIME_UPDATE_INTERVAL seconds
        self.cntUpdateSchedule = Clock.schedule_interval(self.update_window_cnt, s.COUNT_CHECK_INTERVAL)
        if not self.cntUpdateSchedule.is_triggered:
            self.cntUpdateSchedule()

        # update window on entry
        self.update_window_clk()
        self.update_window_cnt()

    # built-in kivy function: before leaving the scan window
    def on_pre_leave(self, *args):
        db.insert_session(s.SESSION_ID, s.ACTIVE_LECTURER, self.session_start_time, get_datetime())
        self.resetScan()

    # stop rfid scanning and clear thread object
    def resetScan(self):
        self.scan_counter = 0
        self.lbl_scan_count.text = str(self.scan_counter)
        self.lbl_scan_msg.text = ""
        self.feedback = False
        s.SCAN_ID     = None
        s.SCAN_TEXT   = None
        s.SCAN_SAVED  = 0
        s.SCAN_READ   = 0

        self.sc.rfid_stop_scan()
        self.sc = None
        Clock.unschedule(self.cntUpdateSchedule)
        Clock.unschedule(self.clkUpdateSchedule)

    # return to main window
    def backButton(self):

        sm.current = "main"

    # periodic routine: update time stamp
    def update_window_clk(self, *args):
        self.lbl_scan_time.text = str(get_time())

    # periodic routine: update count
    def update_window_cnt(self, *args):

        # if self.feedback == True:
        #     #self.lbl_scan_count.text = str(self.scan_counter)
        #     self.feedback = False

        if (s.SCAN_READ > s.SCAN_SAVED) and (not s.SCAN_ID == None):
            if s.SCAN_READ == s.SCAN_SAVED +1: 
                if not db.scanned_since(s.SCAN_TEXT, s.SESSION_ID):
                    print(type(self).__name__,"Looking for:",s.SCAN_TEXT, self.session_start_time, s.ACTIVE_LECTURER)
                    # save log
                    db.insert_log(s.SESSION_ID, get_datetime(), s.SCAN_TEXT)
                    # update window counter
                    self.scan_counter += 1
                    self.lbl_scan_count.text = str(self.scan_counter)
                    self.lbl_scan_msg.text = str(s.SCAN_TEXT)
                else:
                    self.lbl_scan_msg.text = str(s.SCAN_TEXT) + " already logged!"

                s.SCAN_SAVED += 1
                if s.SCAN_SAVED > 500:
                    s.SCAN_SAVED = 0
                    s.SCAN_READ = 0
            else:
                # error
                print(type(self).__name__,"Error: Last", s.SCAN_READ - s.SCAN_SAVED, "scans was not saved")
                self.lbl_scan_msg.text = "Tap again! Log nog saved"
                self.feedback = True
                s.SCAN_READ = s.SCAN_SAVED
                #todo: make this a popup


#####################################################################
#                       LogListWindow class                         #
#####################################################################

class LogListWindow(Screen):
    """ list window class
    Display a list of attendance logs from the database.

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """    
    lbl_list_num = ObjectProperty(None)
    lbl_list_name = ObjectProperty(None)
    btn_list_back = ObjectProperty(None)

    # built-in kivy function: before entering the log list window 
    def on_pre_enter(self, *args):
        s.APP_STATE = "LIST"
        self.lbl_list_num.text = ""
        self.lbl_list_name.text =""
        # loglist = db.get_student_nums_names()
        loglist = db.get_50_logs_nums_times(s.ACTIVE_LECTURER)
        if not loglist == None:
            i=0
            for item in loglist:
                if i > 40:
                    break
                # print(type(self).__name__,item)
                self.lbl_list_num.text += str(item[0]) + "\n"
                self.lbl_list_name.text += str(item[1]) + "\n"
                i +=1

    # # return to main window
    def backButton(self):
        sm.current = "main"

#####################################################################
#                        Settings variables                         #
#####################################################################
DIR_DEV     = '/dev/'       #?
DIR_MEDIA   = '/media/pi/'
DIR_DEV_SD = '/dev/sd??'    #?
# DIR_DEV_SDA = '/dev/sd'
CMD_LS      = 'ls '
CMD_TOUCH   = 'touch '      #?
CMD_ECHO    = 'echo '
CMD_UMOUNT  = 'umount '     #?
CMD_DF_SD   = 'df | grep /dev/sd'
CMD_EJECT   = 'eject -v '
CMD_EJECT_A = 'eject -v /dev/sd??'


#####################################################################
#                     ExportDataWindow class                        #
#####################################################################

class ExportDataWindow(Screen):
    """ export window class
    Export data from database to a mounted usb memory device.

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    btn_export_back     = ObjectProperty(None)
    lbl_export_message  = ObjectProperty(None)
    EXPORTDATA          = ""
    EXPORTFILENAME      = 'sucsexport001.csv'
    DEVICENAME          = ""

    # built-in kivy function: before entering the scan window
    def on_pre_enter(self, *args):
        s.APP_STATE = "EXPORT"
        self.exported = False
        self.media_pi_devs = []

    # return to main window
    def backButton(self):
        sm.current = "main"
        self.exported = False
        self.lbl_export_message.text = ""

    # button method safely removes all connected USB devices
    def ejectButton(self):
        if self.check_sd_mounted():
            output = os.popen(CMD_EJECT_A).read()  # eject -v /dev/sd??
            print(type(self).__name__,"Output:",output)
            if output == "":
                self.lbl_export_message.text = "Storage device safely removed" 
        else:
            self.lbl_export_message.text = "No device to remove"

    # return the list of media devices mounted in the /media/pi/ directory
    def get_media_dev_list(self):
        output = os.popen(CMD_LS+DIR_MEDIA).read()  # ls /media/pi/
        self.media_pi_devs = output.split('\n')
        print(type(self).__name__,"Media Devices:",self.media_pi_devs)
        if "No such file or directory" in output: 
            print(type(self).__name__,"Error:",CMD_LS+DIR_MEDIA, "No such file or directory")
            #TODO: Check for more tests
            #Todo: Create popup that say there is a problem with the file system
            return False    # No dir named /media/pi/
        elif ''.join(output.split()) == '':
            print(type(self).__name__,"DEBUG: no files in",CMD_LS,DIR_MEDIA)
            #Todo: Create popup that say there is no usb device mounted
            return False    # No files in /media/pi/
        else:
            return True     # Found device(s) mounted in /media/pi/

    # check if usb storage device is mounted 
    def check_sd_mounted(self):
        output = os.popen(CMD_DF_SD).read()   # df | grep /dev/sd
        if output == None:
            print(type(self).__name__,":", "No mounted storage device")
            return False    # Did not find mounted device(s)
        else:
            print(type(self).__name__,"Mounted Devices:",output)
            return True     # Found mounted device(s)

    # button method to export data to a mounted storage device
    def exportButton(self):
        if self.exported:
            return

        if self.check_sd_mounted():
            self.get_media_dev_list()
            self.popup_pick()
        else:
            self.lbl_export_message.text = "No device found"

    # create a popup that gives user toe option to choose a device
    def popup_pick(self):
        self.float_popup = FloatLayout()
        self.float_popup.add_widget(Label(        
            size_hint= [0.6, 0.2],
            text= "You will export the data to a \nUSB device",
            font_size= 20,
            pos_hint= {"x":0.2, "top":1}
        ))
        self.float_popup.add_widget(Button(
            size_hint= [0.8, 0.2],
            text= "Go Back",
            font_size= 35,
            pos_hint= {"x":0.1, "y":0.1},
            on_press=   lambda a:self.popupWindow.dismiss()
        ))
        count = 0
        for i in self.media_pi_devs:
            if (not i == '') and count<2:
                # print(type(self).__name__,"-----i:",i)
                btn = Button(
                    text=       i, 
                    size_hint=  [0.8,0.20], 
                    pos_hint=   {"x":0.1, "y":0.32+1.2*count},
                    font_size=  30#,
                    # on_press=   lambda a:self.popup_pick_device(count)
                    )
                if count==0:
                    btn.bind(on_press=self.popup_pick_device0)
                elif count==1:
                    btn.bind(on_press=self.popup_pick_device1)
                self.float_popup.add_widget(btn)
                count+=1
        self.popupWindow = Popup(content=self.float_popup, size_hint=(None,None), size=(400,400))
        self.popupWindow.open()

    #Popup Button methods
    def popup_pick_device0(self, *args):
        self.DEVICENAME = self.media_pi_devs[0]
        # print(type(self).__name__,"----The Device picked:",self.media_pi_devs[0])
        self.popupWindow.dismiss()
        self.save_to_usb()
    def popup_pick_device1(self, *args):
        self.DEVICENAME = self.media_pi_devs[1]
        # print(type(self).__name__,"----The Device picked:",self.media_pi_devs[1])
        self.popupWindow.dismiss() 
        self.save_to_usb()

    # Save data to usb
    def save_to_usb(self):
        loglist = db.get_logs_data(s.ACTIVE_LECTURER)
        sessionlist = db.get_sessions_data(s.ACTIVE_LECTURER)
        # print(type(self).__name__,loglist)

        # Check if there is data in the database
        if loglist == None or sessionlist == None:
            print(type(self).__name__,'Nothing to export')
            self.lbl_export_message.text = "Nothing to export"
        else:
            self.EXPORTFILENAME = 'sucsexport'+s.SUCS_UNIT_NAME+make_datetime_stamp()+'.csv'
            self.lbl_export_message.text = "Export In Progress"
            export_success = True

            # write stamp to .csv
            self.EXPORTDATA = str(s.SUCS_UNIT_NAME)+","+str(s.SUCS_SOFTWARE_VERSION) +","+str(s.SUCS_LAST_UPDATE) + "\n"
            output = os.popen(CMD_ECHO+'"'+self.EXPORTDATA+'" >> "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')    # echo "data" >> "media/pi/DEVICENAME/ECXPORTFILENAME"
            # Check once if command is successful
            if "Permission denied" in output:
                print(type(self).__name__,'Error: Permission Denied for "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')
                #TODO: Check for more tests   
                self.lbl_export_message.text = "Permission Denied"
                export_success = False
                return
 
            # write session data to .csv line by line
            for line in sessionlist:
                self.EXPORTDATA = str(line[0])+","+str(line[1])+","+str(line[2])+","+str(line[3])    # data = 20200831100212,20123456,2020-08-31 10:13:28,2020-08-31 10:33:28
                output = os.popen(CMD_ECHO+'"'+self.EXPORTDATA+'" >> "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')    # echo "data" >> "media/pi/DEVICENAME/ECXPORTFILENAME"

            # write a line break     
            output = os.popen(CMD_ECHO+'"" >> "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')    # echo "data" >> "media/pi/DEVICENAME/ECXPORTFILENAME"
                   
            # write logs data to .csv line by line
            for line in loglist:
                self.EXPORTDATA = str(line[0])+","+str(line[1])+","+str(line[2])                 # data = 20200831100212,20123456,2020-08-31 10:13:28
                output = os.popen(CMD_ECHO+'"'+self.EXPORTDATA+'" >> "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')    # echo "data" >> "media/pi/DEVICENAME/ECXPORTFILENAME"
                
            if export_success:
                self.lbl_export_message.text = "Export Successful"

class WindowManager(ScreenManager):
    pass

#####################################################################
#                Functions available for global use                 #
#####################################################################
# #
# validation functions
# #
def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

# #
# Auxiliary functions
# #
def get_time():
    #return str(datetime.datetime.now()).split(" ")[1] #fix
    now = datetime.datetime.now()
    return now.strftime('%H:%M')
def get_date():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d')
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')
def make_datetime_stamp():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M%S')
def SUCSterminate():
    #todo: Save data
    db.close_connection()
    sys.exit()


#####################################################################
#                             GUI Setup                             #
#####################################################################

#sc = None
kv = Builder.load_file("gui.kv")
sm = WindowManager()

# create database connection
db = Database(s.DATABASE_PATH)

#todo: hide the mouse cursor
Config.set('graphics','show_cursor',0)

screens = [
    LectureLoginWindow(name="login"), 
    MainWindow(name="main"), 
    ScanWindow(name="scan"), 
    LogListWindow(name="list"), 
    ExportDataWindow(name="export")
]
for screen in screens:
    sm.add_widget(screen)
sm.current = "login"

class MyMainApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    MyMainApp().run()
