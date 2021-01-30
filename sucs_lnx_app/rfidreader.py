# SUCS_RFID class runs on a seperate thread on a microprocessor. 
# This class has been written specifically for the Stellenbosch University Card Scanner skripsie 


import multiprocessing  as mp
import RPi.GPIO         as GPIO
from kivy.clock     import Clock
from mfrc522        import MFRC522

import settings as s



class SUCS_RFID(mp.Process):
    def __init__(self, key=[0xFF,0xFF,0xFF,0xFF,0xFF,0xFF], block_addrs=[8, 9, 10]):
        super(SUCS_RFID, self).__init__()
        self.KEY = key
        self.BLOCK_ADDRS = block_addrs
        self.BlockAddr = 5
        self.listen_state = False
        self.data_flag = True
        self.card_id = None
        self.card_text = None
        self.rfidScanSchedule = None
        self.READER = MFRC522(bus=1, device=0, pin_rst=37)

    #################################################################
    #                     RFID global functions                     #
    #################################################################

    def is_scanning(self):
        return self.rfidScanSchedule.is_triggered


    def get_lastread_text(self):
        if not self.card_text == None:
            usnum = self.card_text
            name = "NoName"
            return usnum, name


    def rfid_start_scan(self, scan_interval=0.2):
        print(type(self).__name__,"-----Start Scan")                                  #!Print
        self.scan_interval = scan_interval
        if s.APP_STATE == "SCAN":
            self.rfidScanSchedule = Clock.schedule_interval(self._listen_once, self.scan_interval)

        if not self.is_scanning():
            self.rfidScanSchedule()

    def rfid_stop_scan(self):
        print(type(self).__name__,"-----Stop Scan")                                  #!Print
        if not self.rfidScanSchedule:
            return
        if self.is_scanning():
            self.rfidScanSchedule.cancel()



    #################################################################
    #                    RFID internal functions                    #
    #################################################################

    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

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
        USNumStr = ''
        if status == self.READER.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                USNum1 = self.READER.MFRC522_Read(block_num)
                if (USNum1 != None):
                    USNum = USNum1[0:4]
                    USNumStr = "".join(format(x, '02x') for x in USNum)
        self.READER.MFRC522_StopCrypto1()
        return id, USNumStr
        
    ###
    #   _listen_once: Only listen read rfid once
    ###
    def _listen_once(self, *args):
        try:
            id, text = self._read_no_block()
            print(type(self).__name__,"id="+ str(id), "text="+str(text))    #? Debug print
            # check that the same card is not read twice 
            if not id == None: 
                # if s.SCAN_BLOCK.count(text) = 0:
                if not id == s.SCAN_ID :
                    s.SCAN_READ += 1
                    s.SCAN_ID = id
                    s.SCAN_TEXT = text
                
        finally:
            print(type(self).__name__,"RFID _listen_once")
            GPIO.cleanup()




