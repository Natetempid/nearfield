import pyvisa
import threading
import Queue as q
import datetime
import numpy as np
from enum import Enum
import time

rm = pyvisa.ResourceManager()

class keithley2410():
    def __init__(self, name):
        #visa
        self.ctrl = rm.open_resource(name,read_termination='\r',write_termination='\r')
        self.ctrl.baudrate = 9600
        self.ctrl.timeout = 10000
        
        #threading
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False
        self.rampup_active = False
        self.rampdown_active = False
        #voltage properties
        self.v0 = 0 #ramp step start
        self.v1 = 0 #ramp step end - note: this is not the bias at the end of the ramp.  self.v1-self.v0 is the voltage jump for each step
        self.rampstart = 0
        self.rampend = 0
        self.deltaV = 0 #V/step
        self.ramprate = 0 #V/s
        self.numberofsteps = 0

        #measurements
        self.voltagelist = []
        self.currentlist = []
        self.resistancelist = []
        self.dataq = q.Queue()

    #The plan is to only ramp voltage and measure everything else, so measure setup will be to set voltage and then implement ramp in the code

    def configureMeasurement(self):
        self.ctrl.write(":VOLT:RANG:AUTO ON;")
        self.ctrl.write(":CURR:RANG:AUTO ON;")
        self.ctrl.write(":RES:RANG:AUTO ON;")
        #self.ctrl.write("SOUR:FUNC VOLT;:SOUR:VOLT 0.000000;:CURR:PROT 0.100000;")
        self.ctrl.write("SOUR:FUNC VOLT;:CURR:PROT 0.100000;")

    def setVoltage(self, voltage):
        self.ctrl.write(":SOUR:VOLT %.6f;" % voltage)

    def enableOutput(self):
        self.ctrl.write("OUTP ON;")

    def disableOutput(self):
        self.ctrl.write("OUTP OFF;")

    def readSingle(self):
        #setup trigger and source mode
        self.ctrl.write(":ARM:COUN 1;:TRIG:COUN 1;:SOUR:VOLT:MODE FIX;:SOUR:CURR:MODE FIX;")
        #pull trigger
        self.ctrl.write("ARM:SOUR IMM;:ARM:TIM 0.01000;:TRIG:SOUR IMM;:TRIG:DEL 0.000000")

    def initiateRead(self):
        #clear trigger and initialize
        self.ctrl.write(":TRIG:CLE;:INIT;")

    def waitForOperationComplete(self):
        self.ctrl.query("*OPC?")

    def read(self):
        data = self.ctrl.query(":FETC?")
        return data

    def testSingle(self):
        self.configureMeasurement()
        self.setVoltage(1.)
        self.enableOutput()
        self.readSingle()
        self.initiateRead()
        self.waitForOperationComplete()
        self.read()
        self.disableOutput()

    def incrementVoltage(self):
        self.v1 = self.v0 + self.deltaV
        self.setVoltage(self.v1)
        self.readSingle()
        self.initiateRead()
        self.waitForOperationComplete()
        data = self.read()        
        self.v0 = self.v1
        return data
        #return self.parseData(data)

    def decrementVoltage(self):
        self.v1 = self.v0 - self.deltaV
        self.setVoltage(self.v1)
        self.readSingle()
        self.initiateRead()
        self.waitForOperationComplete()
        data = self.read()        
        self.v0 = self.v1
        return data
        #return self.parseData(data)

    def parseData(self, data):
        datalist = data.split(',')
        parseddata = [datetime.datetime.now(), float(datalist[0]), float(datalist[1]), float(datalist[2])]
        return parseddata        

    def __rampUp(self):
        #initialize voltages
        #self.v0 =  self.rampstart
        secperstep = self.deltaV/self.ramprate
        #step 0
        self.configureMeasurement()
        self.setVoltage(self.v0)
        self.enableOutput()
        self.readSingle()
        self.initiateRead()
        self.waitForOperationComplete()
        data = self.read()
        parseddata = self.parseData(data)
        self.dataq.put(parseddata)

        self.stop_event.clear()
        self.thread_active = True #reset thread_active switch
        self.rampup_active = True
        while (not self.stop_event.is_set()):
            #self.adddatum_event.clear()
            self.stop_event.wait(secperstep)
            if self.v1 < self.rampend: #then ramp isn't complete
                data = self.incrementVoltage()
                parseddata = self.parseData(data)
                self.dataq.put(parseddata)
            else: #then the ramp is complete and it can be held
                self.rampup_active = False
                self.readSingle()
                self.initiateRead()
                self.waitForOperationComplete()
                data = self.read()
                parseddata = self.parseData(data)
                self.dataq.put(parseddata)
            #self.adddatum_event.set()
            #print "Set: %s" % datetime.datetime.now()
        self.thread_active = False
        self.rampup_active = False

    def rampUp(self):
        while (self.thread_active):  #wait to make sure that other methods are completed with the thread
            time.sleep(0.002)
        self.thread = threading.Thread(target = self.__rampUp)
        self.thread.start()

    def __rampDown(self):
        secperstep = self.deltaV/self.ramprate
        #self.configureMeasurement()
        self.stop_event.clear()
        self.thread_active = True
        self.rampdown_active = True
        while (not self.stop_event.is_set()):
            self.stop_event.wait(secperstep)
            if self.v1 > self.rampstart: #then ramp isn't complete
                data = self.decrementVoltage()
                parseddata = self.parseData(data)
                self.dataq.put(parseddata)
            else: #then the ramp is complete and it can be held
                self.rampdown_active = False
                self.readSingle()
                self.initiateRead()
                self.waitForOperationComplete() 
                data = self.read()
                parseddata = self.parseData(data)
                self.dataq.put(parseddata)
        self.thread_active = False
        self.rampdown_active = False

    def rampDown(self):
        while (self.thread_active):  #wait to make sure that other methods are completed with the thread
            time.sleep(0.002)
        self.thread = threading.Thread(target = self.__rampDown)
        self.thread.start()

    def __pauseRamp(self):
        secperstep = self.deltaV/self.ramprate
        self.stop_event.clear() #reset stop thread switch
        while (self.thread_active):  #wait to make sure that other methods are completed with the thread
            time.sleep(0.002)
        self.thread_active = True #resent thread_active switch
        self.rampup_active = False
        self.rampdown_active = False
        while (not self.stop_event.is_set()):
            self.stop_event.wait(secperstep)
            #read the current voltage and append it to data, but don't set the voltage
            self.readSingle()
            self.initiateRead()
            self.waitForOperationComplete()
            data = self.read()
            parsedata = self.parseData(data)
            self.dataq.put(parsedata)
        self.thread_active = False

    def pauseRamp(self):
        while (self.thread_active):  #wait to make sure that other methods are completed with the thread
            time.sleep(0.002)
        self.thread = threading.Thread(target = self.__pauseRamp)
        self.thread.start()

    def __turnOff(self):
        self.stop_event.clear()
        self.thread_active = True
        self.disableOutput()
        self.thread_active = False

    def turnOff(self):
        while (self.thread_active):  #wait to make sure that other methods are completed with the thread
            time.sleep(0.002)
        self.thread = threading.Thread(target = self.__turnOff)
        self.thread.start()
        
    def abort(self):
        #interrupt thread
        self.stop_event.set()
        while (self.thread_active):
            time.sleep(0.001)
        #send abort command
        self.ctrl.write(":ABOR;:TRIG:CLE;")
        self.disableOutput()