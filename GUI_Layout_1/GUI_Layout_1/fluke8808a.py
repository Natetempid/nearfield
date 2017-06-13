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
        self.display2 = None
        self.list1 =[]# {'datetime': [], 'unit': [], 'data': []}
        self.list2 = []#{'datetime': [], 'unit': [], 'data': []}
        self.single1 = {'unit': None, 'data': None}
        self.single2 = {'unit': None, 'data': None}
        self.defaultstr = "AUTO; RATE M; DBREF 1"

        #threading
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False

        #data queue
        self.primaryq = q.Queue() #each element will be a list with 3 elements [0] = Time | [1] = data value | [2] = data unit
        self.secondaryq = q.Queue()

    #def measurePrimaryDisplay(self, timestep):
    #    self.thread = threading.Thread(target = self.__measurePrimaryDisplay, args=(timestep,))
    #    self.thread.start()

    def singlePrimaryDisplay(self):
        self.ctrl.clear()
        [val, unit] = self.ctrl.query("VAL1?").split(' ')
        self.single1['data'] = float(val)
        self.single1['unit'] = unit.strip('\r\n')

    def singleSecondaryDisplay(self):
        self.ctrl.clear()
        input = self.ctrl.query("VAL2?")
        #print input
        [val, unit] = input.split(' ')
        self.single2['data'] = float(val)
        self.single2['unit'] = unit.strip('\r\n')

    
    def measureBothDisplays(self, timestep):
        self.thread = threading.Thread(target = self.__measureBothDisplays, args = (timestep,))
        self.thread.start()

    def __measureBothDisplays(self,timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            val_list = []
            self.stop_event.wait(timestep)
            self.ctrl.clear()
            self.stop_event.wait(0.002)
            val_list = self.ctrl.query("VAL?").split(',')
            #print val_list
            nowtime = datetime.datetime.now()
            if len(val_list) == 1:
                #then only the primary display is configured
                [val1, unit1] = val_list[0].split(' ')
                self.primaryq.put([nowtime, float(val1), unit1.strip('\r\n')])
                #self.list1.append({'datetime': datetime.datetime.now(), 'unit': unit1.strip('\r\n'), 'data': float(val1)})
            elif len(val_list) == 2:
                #then the secondary display is also configured
                [val1, unit1] = val_list[0].split(' ')
                self.primaryq.put([nowtime, float(val1), unit1.strip('\r\n')])
                #self.list1.append({'datetime': datetime.datetime.now(), 'unit': unit1.strip('\r\n'), 'data': float(val1)})     
                [val2, unit2] = val_list[1].split(' ')
                self.secondaryq.put([nowtime, float(val2), unit2.strip('\r\n')])
                #self.list2.append({'datetime': datetime.datetime.now(), 'unit': unit2.strip('\r\n'), 'data': float(val2)})
        self.thread_active = False

                
    def configPrimaryDisplay(self,type):
        #type is a string resistance (2 wire), voltage, current
        self.ctrl.clear() #flush buffers
        if type == "Resistance":
            self.status = self.ctrl.query("OHMS; WIRE2; %s" % self.defaultstr)
        elif type == "DC Voltage":
            self.status = self.ctrl.query("VDC; %s" % self.defaultstr)
        elif type == "DC Current":
            self.status = self.ctrl.query("ADC; %s" % self.defaultstr)
        else:
            self.status = -1
        self.display1 = type

    def configSecondaryDisplay(self,type):
        #type is a string resistance (2 wire), voltage, current
        self.ctrl.clear() #flush buffers
        if type == "Resistance":
            self.status = self.ctrl.query("OHMS2; WIRE2; %s" % self.defaultstr)
        elif type == "DC Voltage":
            self.status = self.ctrl.query("VDC2; %s" % self.defaultstr)
        elif type == "DC Current":
            self.status = self.ctrl.query("ADC2; %s" % self.defaultstr)
        else:
            self.status = -1
        self.display2 = type



