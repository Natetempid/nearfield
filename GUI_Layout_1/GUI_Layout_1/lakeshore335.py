import pyvisa
import threading
import Queue as q
import datetime
import numpy as np
from enum import Enum

rm = pyvisa.ResourceManager()

class lakeshore335():
    def __init__(self, name):
        self.ctrl = rm.open_resource(name)
        self.ctrl.baud_rate = 57600
        self.ctrl.parity = pyvisa.constants.Parity.odd
        self.ctrl.data_bits = 7

        self.identity = self.lakestr2str(self.ctrl.query("*IDN?"))
        self.status = self.ctrl.query("*TST?")
        self.queueA = q.Queue()

        #data storage

        #temperature for inputs A and B
        self.listA = []#np.ndarray((1,), dtype = float)
        self.listB = []#np.ndarray((1,), dtype = float)

        #status of heaters 1 and 2
        self.heater1 = heater(self,1)
        self.heater2 = heater(self,2)

        #threading
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        
    #methods for threading and measuring    

    def configThread(self):
        self.stop_event.clear()

#########################
## Measure Temperature ##
#########################


  
    def get_tempA(self):
        temp = self.ctrl.query("KRDG? A")
        return self.lakestr2float(temp)

    def __measureA(self, timestep):
        self.stop_event.clear()
        while (not self.stop_event.is_set()):
            #self.queueA.put({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.listA.append({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.stop_event.wait(timestep)

    def measureA(self, timestep):
        self.thread = threading.Thread(target = self.__measureA, args=(timestep,))
        self.thread.start()

    def get_tempB(self):
        temp = self.ctrl.query("KRDG? B")
        return self.lakestr2float(temp)

    def __measureB(self, timestep):
        self.stop_event.clear()
        while (not self.stop_event.is_set()):
            #self.queueA.put({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.listB.append({'datetime': datetime.datetime.now(), 'data': self.get_tempB()})
            self.stop_event.wait(timestep)
    
    def measureB(self, timestep):
        self.thread = threading.Thread(target = self.__measureB, args=(timestep,))
        self.thread.start()


    def get_tempAandB(self):
        tempstrlist = self.lakestr2str(self.ctrl.query("KRDG? A KRDG? B")).split(';')
        tempfltlist = []
        for elem in tempstrlist:
            tempfltlist.append(float(elem))
        return tempfltlist

    def __measureAandB(self, timestep):
        self.stop_event.clear()
        while (not self.stop_event.is_set()):
            tempfltlist = self.get_tempAandB()
            self.listA.append({'datetime': datetime.datetime.now(), 'data': tempfltlist[0]})
            self.listB.append({'datetime': datetime.datetime.now(), 'data': tempfltlist[1]})
            self.stop_event.wait(timestep)

    def measureAandB(self, timestep):
        self.thread = threading.Thread(target = self.__measureAandB, args=(timestep,))
        self.thread.start()

    def stopThread(self):
        self.stop_event.set()

###########################
## Measure Heater Output ##
###########################


###Deal here 20170504_NHT    
#    def getHeaterOutput1and2(self):
#        heater1str = self.lakestr2str(self.ctrl.query("HTRSET? 1 OUTMODE? 1"))
#        heater2str = self.lakestr2str(self.ctrl.query("HTRSET? 2 OUTMODE? 2"))

#    def heaterstr2dict(heaterstr):
#        heaterdict = {}
#        splitarray = heaterstr.split(';')
#        htrsetstr = splitarry[1]
#        outmodestr = splitarry[2]

#        htrsetarray = htrsetstr.split(',')
#        heaterdict

        

    
#    def __measureHeater1and2(self, timestep):
#        self.stop_event.clear()
#        while (not self.stop_event.is_set()):
#            heater1_setupstr = self.ctrl.


    #methods for writing serial commmands to lakeshore
    def close(self):
        self.ctrl.close()
  

    def lakestr2str(self, str):
        return str.strip("\r\n")

    def lakestr2float(self, str):
        return float(str.strip("\r\n"))


class heater():
    def __init__(self, parent, IDnumber):
        #parent is lakeshore instance
        self.ID = IDnumber
    #def config():
     #   parent.ctrl.write('*TST?')