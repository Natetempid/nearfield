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
            relay_tmp = relay(self,k)
            relay_tmp.turnOff()
            self.relays.append(relay_tmp)
        

    def turnOffAllRelays(self):
        self.ctrl.write( chr(254) + chr(129) + chr(1) )
        for k in range(0,8):
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
        self.status = 0
        #self.getStatus()

    def set_onID(self):
        return 107 + self.number

    def set_offID(self):
        return 99 + self.number

    def set_statusID(self):
        return 115 + self.number

    def turnOn(self):
        self.master.ctrl.write( chr(254) + chr(self.onID) + chr(1) )
        self.status = 1

    def turnOff(self):
        self.master.ctrl.write( chr(254) + chr(self.offID) + chr(1))
        self.status = 0

    def getStatus(self):
        waste = self.master.ctrl.read(1024) #read everything in the buffer currently, and then write
        self.master.ctrl.write( chr(254) + chr(self.statusID) + chr(1))
        #print self.master.ctrl.read(1024)
        input = self.master.ctrl.read(1024)
        print input
        self.status = ord(input)
