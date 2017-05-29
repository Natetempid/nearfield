import pyvisa
import threading
import Queue as q
import datetime
import numpy as np
from enum import Enum

rm = pyvisa.ResourceManager()

class fluke8808a():
    def __init__(self,name):
        self.ctrl = rm.open_resource(name)
        self.ctrl.baudrate = 9600
        self.display1 = None
        self.dispaly2 = None
        self.defaultstr = "AUTO; RATE M; DBREF 1"

        #threading
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False

    def measurePrimaryDisplay(self, timestep):
        self.thread = threading.Thread(target = self.__measurePrimaryDisplay, args=(timestep,))
        self.thread.start()

    def __measurePrimaryDisplay(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            self.stop_event.wait(timestep)
            self.ctrl.clear()
            self.stop_event.wait(0.002)
            [val, unit] = self.ctrl.query("VAL1?").split(' ')
            datum['value'] = float(val)
            datum['unit'] = unit.strip('\r')#not tested yet
        self.thread_active = False


    def configurePrimaryDisplay(self,type):
        #type is a string resistance (2 wire), voltage, current
        self.ctrl.clear() #flush buffers
        if type == "resistance":
            self.status = self.ctrl.query("OHMS; WIRE2; %s" % self.defaultstr)
        elif type == "voltage":
            self.status = self.ctrl.query("VDC; %s" % self.defaultstr)
        elif type == "current":
            self.status = self.ctrl.query("ADC; %s" % self.defaultstr)
        else:
            self.status = -1
        self.display1 = type

    def configureSecondaryDisplay(self,type):
        #type is a string resistance (2 wire), voltage, current
        self.ctrl.clear() #flush buffers
        if type == "resistance":
            self.status = self.ctrl.query("OHMS2; WIRE2; %s" % self.defaultstr)
        elif type == "voltage":
            self.status = self.ctrl.query("VDC2; %s" % self.defaultstr)
        elif type == "current":
            self.status = self.ctrl.query("ADC2; %s" % self.defaultstr)
        else:
            self.status = -1
        self.display2 = type



