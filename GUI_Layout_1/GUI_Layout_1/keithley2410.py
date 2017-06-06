import pyvisa
import threading
import Queue as q
import datetime
import numpy as np
from enum import Enum

rm = pyvisa.ResourceManager()

class keithley2410():
    def __init__(self, name):
        self.ctrl = rm.open_resource(name,read_termination='\r',write_termination='\r')
        self.ctrl.baudrate = 9600
        #print self.ctrl.query("*IDN?")
        self.ctrl.timeout = 10000
        #self.testSingle()

    #The plan is to only ramp voltage and measure everything else, so measure setup will be to set voltage and then implement ramp in the code

    def configureMeasurement(self):
        self.ctrl.write(":VOLT:RANG:AUTO ON;")
        self.ctrl.write(":CURR:RANG:AUTO ON;")
        self.ctrl.write(":RES:RANG:AUTO ON;")
        self.ctrl.write("SOUR:FUNC VOLT;:SOUR:VOLT 0.000000;:CURR:PROT 0.100000;")

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
        print data

    def testSingle(self):
        self.configureMeasurement()
        self.setVoltage(1.)
        self.enableOutput()
        self.readSingle()
        self.initiateRead()
        self.waitForOperationComplete()
        self.read()
        self.disableOutput()





