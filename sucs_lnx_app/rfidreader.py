#!/usr/bin/env python
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522   
from mfrc522 import MFRC522
from kivy.clock import Clock
import threading
import string
import multiprocessing as mp
from sucsdb import Database
DATABASE_PATH = r"../sucs_pi_db.db"

class SUCS_RFID(mp.Process):

    # KEY = #! Confidential
    # self.BlockAddr =  #! Confidential


    def __init__(self, active_lecturer=None, key=[0xFF,0xFF,0xFF,0xFF,0xFF,0xFF], block_addrs=[8, 9, 10]):
        super(SUCS_RFID, self).__init__()
        self.active_lecturer = active_lecturer
        self.KEY = key
        self.BLOCK_ADDRS = block_addrs
        self.BlockAddr = 5
        self.listen_state = False
        self.data_flag = True
        self.card_id = None
        self.card_text = None
        self.rfidScanSchedule = None
        self.scan_counter = 0
        self.READER = MFRC522(bus=1, device=0, pin_rst=37)
        self.db = Database(DATABASE_PATH)
        if active_lecturer:
            self.db.set_active_lecturer(active_lecturer)

#################################################################
#                     RFID global functions                     #
#################################################################

    def is_scanning(self):
        return self.rfidScanSchedule.is_triggered

    def data_waiting(self):
        return self.data_flag
            
    def get_data(self):
        return self.card_id, self.card_text
    
    def get_usnum_name(self):
        if not self.card_text == None:
            data = self.card_text.split(',')
            usnum = data[0]
            name = data[1]
            return usnum, name

    def set_data_received(self):
        self.data_flag = False

    def rfid_start_scan(self, scan_interval=0.2):
        self.scan_interval = scan_interval
        self.rfidScanSchedule = Clock.schedule_interval(self._listen_once, self.scan_interval)
        if not self.is_scanning():
            self.rfidScanSchedule()

    def rfid_stop_scan(self):
        if not self.rfidScanSchedule:
            return
        if self.is_scanning():
            self.rfidScanSchedule.cancel()
        self.db.close_connection()

### 
#   stop_reading: Set listen_state to False (only when read_tag() has been called)
###
    def stop_reading(self):
        self.listen_state = False
        self.READER.Close_MFRC522()

### 
#   read_tag: Set listen_state to True and call _read()
###
    def read_tag(self):
        try:
                self.listen_state = True
                id, text = self._read()
                return text
        finally:
                GPIO.cleanup()

#################################################################
#                    RFID internal functions                    #
#################################################################

### 
#   _listen_once: Only listen read rfid once
###
    def _listen_once(self, *args):
        try:
            id, text = self._read_no_block()
            if not id == self.card_id and not id == None:
                print(type(self).__name__,"id="+ str(id), "text="+str(text))
                self.card_id = id
                self.card_text = str(text)
                self.data_flag = True
                self.scan_counter += 1
                self.db.insert_student_logs(id, str(text))
        finally:
            GPIO.cleanup()
 
### 
#   read: While listen_state is True call _read_no_block() 
###  
    def _read(self):
        print(type(self).__name__,"inside read()")
        id, text = self._read_no_block()
        i=0
        while (not id) and (self.listen_state):
            i+=1
            id, text = self._read_no_block()
            print(type(self).__name__,i,"id="+ str(id))    #Todo: remove after debug
        print(type(self).__name__,"Finally: id=", str(id),"\rtext=",str(text))   #Todo: remove after debug
        return id, text


    def _read_no_block(self):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        id = self._uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)
        status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, self.BlockAddr, self.KEY, uid)
        data = []
        text_read = ''
        if status == self.READER.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                block = self.READER.MFRC522_Read(block_num) 
                if block:
                        data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
        self.READER.MFRC522_StopCrypto1()
        return id, text_read


    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n


#################################################################
#                    Data handling functions                    #
#################################################################




#################################################################
#                       Debug functions                         #
#################################################################
        
    def read_id(self):
        id = self._read_id_no_block()
        while (not id) and (self.listen_state):
            id = self._read_id_no_block()
        return id

    def _read_id_no_block(self):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None
        return self.uid_to_num(uid)
    
### 
#   crackkey: function written for crack func in Read.py
###
    def crackkey(self, key):
        self.KEY = key
        id, text = self._read_no_block()
        while (not id) and (self.listen_state):
            id, text = self._read_no_block()
            #print("id="+ str(id))     
        return id, text

###?from mfrc522 import SimpleMFRC522    
#?    def write_tag(self, text):
#?        try:
#?                #text = input('New data:')
#?                print("Now place your tag to write")
#?                self.READER.write(text)
#?                print("Written")
#?        finally:
#?                GPIO.cleanup()
