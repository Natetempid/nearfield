import serial
import threading
import Queue as q
import datetime
import numpy as np
import sys  
import time
#reload(sys)  
#sys.setdefaultencoding('utf8')

class usbswitch():
    def __init__(self, name):
        self.ctrl = serial.Serial()
        portname = ""
        for k in range(0,10):
            if str(k) in name:
                print portname
                portname = "COM%d" % k
        self.ctrl.port = portname
        self.ctrl.baudrate = 115200
        self.ctrl.timeout = 2
        self.ctrl.open()
        self.error = None
        self.relays = []
        self.__initrelays()

    def __initrelays(self):
        for k in range(1,9):
            self.relays.append(relay(self,k))

    def turnOnRelay(self, relay):
        self.ctrl.write( chr(254) + chr(relay.onID) + chr(1) )
        relay.status = 1

    def turnOffRelay(self, relay):
        self.ctrl.write( chr(254) + chr(relay.offID) + chr(1))
        relay.status = 0

    def turnOffAllRelays(self):
        self.ctrl.write( chr(254) + chr(129) + chr(1) )
        for k in range(1,9):
            self.relays[k].status = 0

    def close(self):
        self.ctrl.close()

class relay():
    def __init__(self, master, number):
        self.master = master
        if number < 1 or number > 8:
            self.number = None
            return None
        else:   
            self.number = number #number is for relay 1 - 8
        
        self.onID = self.set_onID() #this is an integer that is sent to relay to turn it on
        self.offID = self.set_offID() #this is an integer that is sent to relay to turn it off
        self.statusID = self.set_statusID()
        self.status = None
        self.getStatus()

    def set_onID(self):
        return 107 + self.number

    def set_offID(self):
        return 99 + self.number

    def set_statusID(self):
        return 115 + self.number

    def getStatus(self):
        self.master.ctrl.write( chr(254) + chr(self.statusID) + chr(1))
        #print self.master.ctrl.read(1024)
        self.status = ord(self.master.ctrl.read(1024))
