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
        self.stop_event.set()
        
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
        self.parent = parent
        self.ID = IDnumber
        self.mode = None
        self.input = None
        self.powerupenable = None
        #Polarity
        heater.outputtype = None
        heater.polarity = None
        #Heater Setup
        heater.type = None
        heater.resistance = None
        heater.maxcurrent = None
        heater.maxusercurrent = None
        heater.iorw = None
        #PID
        heater.p = None
        heater.i = None
        heater.d = None
        #Setpoint
        heater.setpoint = None
        heater.setpointramp = None
        heater.setpointrampenable = None

    #Configure Heater
    def prepare_outmode(self):
        return 'OUTMODE %d,%d,%d,%d' % (self.ID, self.mode, self.input, self.powerupenable)
    def prepare_polarity(self):
        return 'POLARITY 2,%d' % self.polarity
    def prepare_htrset(self):
        return 'HTRSET %d,%d,%d,%d,%.3f,%d' % (self.ID, self.type, self.resistance, self.maxcurrent, self.maxusercurrent, self.iorw)
    def prepare_pid(self):
        return 'PID %d,%.1f,%.1f,%.1f' % (self.ID, self.p, self.i, self.d)
    def prepare_ramp(self):
        return 'RAMP %d,%d,%.1f' % (self.ID, self.setpointrampenable, self.setpointramp)
    def prepare_setp(self):
        return 'SETP %d,%.4f' % (self.ID, self.setpoint)
    
    def config(self):
        if self.ID is 2 and self.outputtype is 2: #include polarity
            command_str = '%s;%s;%s;%s;%s;%s' % (self.prepare_outmode(), self.prepare_polarity(), self.prepare_htrset(), self.prepare_pid(), self.prepare_ramp(), self.prepare_setp())
        else:
            command_str = '%s;%s;%s;%s;%s' % (self.prepare_outmode(), self.prepare_htrset(), self.prepare_pid(), self.prepare_ramp(), self.prepare_setp())
        #print command_str
        self.parent.ctrl.write(command_str)

    #Query Heater
    def prepare_outmode_q(self):
        return 'OUTMODE? %d' % (self.ID)
    def prepare_polarity_q(self):
        return 'POLARITY? %d' % (self.ID)
    def prepare_htrset_q(self):
        return 'HTRSET? %d'% (self.ID)
    def prepare_pid_q(self):
        return 'PID? %d' % (self.ID)
    def prepare_ramp_q(self):
        return 'RAMP? %d' % (self.ID)
    def prepare_setp_q(self):
        return 'SETP? %d' % (self.ID)

    def query(self):
        command_str = '%s;%s;%s;%s;%s;%s' % (self.prepare_outmode_q(), self.prepare_polarity_q(), self.prepare_htrset_q(), self.prepare_pid_q(), self.prepare_ramp_q(), self.prepare_setp_q())
        return_str = self.parent.ctrl.query(command_str)
        [outmode_str, polarity_str, htrset_str, pid_str, ramp_str, setp_str] = return_str.split(';')
        [mode_str, input_str, powerupenable_str] = outmode_str.split(',')
        self.mode = int(mode_str)
        self.input = int(input_str)
        self.powerupenable = int(powerupenable_str)
        self.polarity = int(polarity_str)
        [type_str, resistance_str, maxcurrent_str, maxusercurrent_str, iorw_str] = htrset_str.split(',')
        self.type = int(type_str)
        self.resistance = int(resistance_str)
        self.maxcurrent = int(maxcurrent_str)
        self.maxusercurrent = float(maxusercurrent_str)
        self.iorw = int(iorw_str)
        [p_str, i_str, d_str] = pid_str.split(',')
        self.p = float(p_str)
        self.i = float(i_str)
        self.d = float(d_str)
        [setpointrampenable_str, setpointramp_str] = ramp_str.split(',')
        self.setpointrampenable = int(setpointrampenable_str)
        self.setpointramp = float(setpointramp_str)
        self.setpoint = float(setp_str)
    #def config():
     #   parent.ctrl.write('*TST?')