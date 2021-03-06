#####################################################################
#                        Settings variables                         #
#####################################################################

SUCS_UNIT_NAME = "pi001"
SUCS_LAST_UPDATE = "2020-11-03"
SUCS_SOFTWARE_VERSION = "1.0"

DATABASE_PATH = r"/home/pi/kivy_venv/sucs_pi_db.db"
EXPORT_DIR = "~/kivy_venv/export/"

RFID_READ_INTERVAL = 0.2
TIME_UPDATE_INTERVAL = 20
SCAN_CHECK_INTERVAL = 1
COUNT_CHECK_INTERVAL = 1

APP_STATE = "OFF"   #LOGIN, SCAN, MAIN, EXPORT, LIST
ACTIVE_LECTURER = None
SESSION_ID = None

#debug purposes
RFID_ENABLED = True
MANUAL_LECTURER = 12345678 #(10000000)
LOGIN_BYPASS = True

SCAN_ID     = None
SCAN_TEXT   = None
SCAN_SAVED  = 0
SCAN_READ   = 0