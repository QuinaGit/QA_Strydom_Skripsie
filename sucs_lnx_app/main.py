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


#####################################################################
#                        Settings variables                         #
#####################################################################
DIR_DEV     = '/dev/'
DIR_MEDIA   = '/media/pi/'
DIR_DEV_SDA = '/dev/sda*'
CMD_LS      = 'ls '
CMD_TOUCH   = 'touch '
CMD_ECHO    = 'echo '
CMD_UMOUNT  = 'umount '

#####################################################################
#                         Kivy GUI classes                          #
#####################################################################

class LectureLoginWindow(Screen):
    """log in window to app

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    dinge = "Yes"
    valid =1
    lecturer_info = None
    sc=None
    
    def on_pre_enter(self):
        if s.RFID_ENABLED:
            if not self.sc:
                self.sc = SUCS_RFID()
            self.sc.start()
            self.sc.rfid_start_scan(scan_interval=s.RFID_READ_INTERVAL)

        self.checkInfoSchedule = Clock.schedule_interval(self.checkInfo, s.SCAN_CHECK_INTERVAL)
        if not self.checkInfoSchedule.is_triggered:
            self.checkInfoSchedule()

    def checkInfo(self, *args):
        info = self.sc.get_usnum_name()  #get (usnum, name) from database
        if not info == None:
            self.lecturer_info = info
            self.loginBtn()


    def loginBtn(self):
        # self.lecturer_id = self.lecturer_info[0]
        if s.LOGIN_BYPASS:
            Clock.unschedule(self.checkInfo)
            s.ACTIVE_LECTURER = s.MANUAL_LECTURER
            sm.current = "main"
            self.resetLogin()
        else:
            if db.valid_lecturer(self.lecturer_info[0]):        #test valid lecturer according to database 
                Clock.unschedule(self.checkInfo)
                db.set_active_lecturer(self.lecturer_info[0])
                s.ACTIVE_LECTURER = self.lecturer_info
                sm.current = "main"
                self.resetLogin()
            else:
                self.popup_new_lecture()

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
    #Popup Button method
    def createNewLecrurer(self, *args):
        if db.insert_lecturers(self.lecturer_info[0],self.lecturer_info[1]) < 0:
            print(type(self).__name__,"Failed to create new lecturer")
        else:
            print(type(self).__name__,"Successfully created lecturer:",self.lecturer_info)
        self.popupWindow.dismiss()

    def logoffBtn(self):
        self.resetLogin()
        SUCSterminate()

    def resetLogin(self):
        self.sc.rfid_stop_scan()
        self.sc = None


class MainWindow(Screen):
    """display app menu

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    username = ""
    lecture_id = ""
    lbl_main_time = ObjectProperty(None) #make this work
    lbl_main_user = ObjectProperty(None) #make this work

    def logOut(self):
        sm.current = "login"

    def on_pre_enter(self, *args):
        self.update_count = -1
        self.update_window()
        self.lbl_main_user.text = "Loged In: "+ str(s.ACTIVE_LECTURER[1])
        # name = "Username!"                                      #todo: Get from databases

    def scanBtn(self):
        sm.current = "scan"

    def listBtn(self):
        sm.current = "list"

    def logoutBtn(self):
        sm.current = "login"

    def exportBtn(self):
        sm.current = "export"

    def update_window(self, *args):
        if self.update_count < 0:
            self.lbl_main_time.text = str(get_time())
            self.update_count = 30
        self.update_count -= 1


class ScanWindow(Screen):
    """activates rfid reader and stores scanned information to the database

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """
    nowtime = ""#get_time()
    testnum = 20346534
    lbl_scan_count = ObjectProperty(None) #make this work
    lbl_scan_time = ObjectProperty(None) #make this work
    btn_scan_back = ObjectProperty(None)
    log_counter = 0
    last_scan_time = time()
    button_press_time = 0.1

    sc=None

    def on_pre_enter(self, *args):
        # activate rfid reader in another thread
        if s.RFID_ENABLED:
            if self.sc:
                self.resetScan()
            self.sc = SUCS_RFID(key=[0xF0,0x1E,0x01,0xD0,0x1C,0x01], block_addrs=[4,5,6])
            self.sc.start()
            self.sc.rfid_start_scan(scan_interval=s.RFID_READ_INTERVAL)
        
        # schedule window to update every TIME_UPDATE_INTERVAL seconds
        self.winUpdateSchedule = Clock.schedule_interval(self.update_window, s.TIME_UPDATE_INTERVAL)
        if not self.winUpdateSchedule.is_triggered:
            self.winUpdateSchedule()
        
        # update window on entry
        self.update_window()


    def on_pre_leave(self, *args):
        # built-in function: before leaving the scan window
        self.resetScan()

    def resetScan(self):
        # stop rfid scanning and clear thread object
        self.sc.rfid_stop_scan()
        self.sc = None

    def backButton(self):
        # return to main window
        sm.current = "main"

    def update_window(self, *args):
        self.lbl_scan_time.text = str(get_time())
        self.lbl_scan_count.text = str(0)   #todo: get this from the database


class LogListWindow(Screen):
    """display a list of attendance logs from the database

    Args:
        Screen (Screen): kivy.uix.screenmanager
    """    
    lbl_list_num = ObjectProperty(None)
    lbl_list_name = ObjectProperty(None)
    btn_list_back = ObjectProperty(None)
    
    def on_pre_enter(self, *args):
        loglist = db.get_student_nums_names()
        if not loglist == None:
            for item in loglist:
                self.lbl_list_num.text += str(item[0]) + "\n"
                self.lbl_list_name.text += str(item[1]) + "\n"

    def backButton(self):
        sm.current = "main"


class ExportDataWindow(Screen):
    """export data from database to a mounted usb memory device

    Args:
        Screen (Screen): kivy.uix.screenmanager

    Todo:
        Create button to safely unmount usb device
    """
    btn_export_back = ObjectProperty(None)
    lbl_export_message = ObjectProperty(None)
    EXPORTDATA  = ""
    EXPORTFILENAME    = 'sucsexport001.csv'
    DEVICENAME = ""
    def on_pre_enter(self, *args):
        self.exported = False
        self.media_pi_devs = []

    def backButton(self):
        sm.current = "main"
        self.exported = False
        self.lbl_export_message.text = ""

    def unmoutButton(self):
        if self.check_sda_mounted():
            output = os.popen(CMD_UMOUNT+DIR_MEDIA+'*').read()  # ls /media/pi/
            print(type(self).__name__,"Output:",output)
            if output == "":
                self.lbl_export_message.text = "Storage device safely removed" 
        else:
            self.lbl_export_message.text = "No device to remove"

    def check_sda_mounted(self):
        # check if usb device is plugged in 
        #todo:  mount | grep /dev/sda
        #?      /dev/sda1 on /media/pi/QUINTIN16GB type vfat (rw,nosuid,nodev,relatime,uid=1000,gid=1000,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,showexec,utf8,flush,errors=remount-ro,uhelper=udisks2)

        #todo:  df -x squashfs
        #?      Filesystem     1K-blocks    Used Available Use% Mounted on
                # ...
                # ...
                # /dev/sda1       15712192      88  15712104   1% /media/pi/QUINTIN16GB

        #todo:  df -x squashfs | grep sda
        #?      # /dev/sda1       15712192      88  15712104   1% /media/pi/QUINTIN16GB
 
        pipe = subprocess.Popen(CMD_LS+DIR_DEV_SDA, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   # ls /dev/sda*
        out, err = pipe.communicate()
        print(type(self).__name__,"Media Devices:",out,err)
        if "No such file or directory" in str(out):
            print(type(self).__name__,"Error:",CMD_LS+DIR_DEV_SDA, "No such file or directory")
            #TODO: Check for more tests
            return False    # No sda found in /dev/ - no usb plugged in
        else:
            # USB device found
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
                

    def exportButton(self):
        if self.exported:
            return

        if self.check_sda_mounted():
            self.popup_pick()
        else:
            self.lbl_export_message.text = "No device found"

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
                print("-----i:",i)
                print("-----c:",count)
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
        print(type(self).__name__,"----The Device picked:",self.media_pi_devs[0])
        self.popupWindow.dismiss()
        self.save_to_usb()
    def popup_pick_device1(self, *args):
        self.DEVICENAME = self.media_pi_devs[1]
        print(type(self).__name__,"----The Device picked:",self.media_pi_devs[1])
        self.popupWindow.dismiss() 
        self.save_to_usb()

    # Save data to usb
    def save_to_usb(self):
        loglist = db.get_student_nums_names()
        print(type(self).__name__,loglist)
        if not loglist == None:
            self.EXPORTFILENAME = 'sucsexport'+get_date_stamp()+'.csv'
            for item in loglist:
                self.DEVICENAME = str(item[0])+","+str(item[1]) + "\n"

                output = os.popen(CMD_ECHO+'"'+self.EXPORTDATA+'" >> "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')    # echo "data" >> "media/pi/DEVICENAME/ECXPORTFILENAME"
                if "Permission denied" in output:
                    print(type(self).__name__,'Error: Permission Denied for "'+DIR_MEDIA+self.DEVICENAME+'/'+self.EXPORTFILENAME+'"')
                    #TODO: Check for more tests   
                else:
                    return

                self.lbl_export_message.text = "Export Successfull"
        else:
            print(type(self).__name__,'Nothing to export')
            self.lbl_export_message.text = "Nothing to export"


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
# Auxiliry functions
# #

def get_time():
    #return str(datetime.datetime.now()).split(" ")[1] #fix
    now = datetime.datetime.now()
    return now.strftime('%H:%M')
def get_date():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d')
def get_date_stamp():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d')

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

#db.insert_lecturers(10000000, "MM Visser")


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
