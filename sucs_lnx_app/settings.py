#####################################################################
#                        Settings variables                         #
#####################################################################
DATABASE_PATH = r"../sucs_pi_db.db"
EXPORT_DIR = "~/kivy_venv/export/"

#debug purposes
RFID_ENABLED = True
MANUAL_LECTURER = (12345678,"Hdt Mouton") #10000000
ACTIVE_LECTURER = None
LOGIN_BYPASS = True    

RFID_READ_INTERVAL = 0.2
TIME_UPDATE_INTERVAL = 20
SCAN_CHECK_INTERVAL = 1

def get_database_path():
    return DATABASE_PATH

def get_export_dir():
    return EXPORT_DIR

def get_avtive_lecturer():
    return ACTIVE_LECTURER

def set_avtive_lecturer(lecturer_num):
    ACTIVE_LECTURER = lecturer_num

def get_manual_lecturer():
    return MANUAL_LECTURER

def set_manual_lecturer(lecturer_num):
    MANUAL_LECTURER = lecturer_num

def check_rfid_enabled():
    return RFID_ENABLED

def check_login_bypass():
    return LOGIN_BYPASS

