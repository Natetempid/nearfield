from PyDAQmx import *
import numpy as np
import time
import datetime 
import threading

class daq9211():
    def __init__(self, name):
        self.name = name
        self.channels = {}
        self.data = {}
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False

    def add_channel(self, channel):
        self.channels[channel.name] = channel
        self.data[channel.name] = []

    def __measureAll(self, timestep):
        namelist = self.channels.keys()
        #run task once in each channel
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            self.stop_event.wait(timestep/2)
            for i in range(0,len(namelist)):
                self.channels[namelist[i]].measure()
                #print self.channels[namelist[i]].datum
                self.data[namelist[i]].append({'datetime': datetime.datetime.now(), 'data': self.channels[namelist[i]].datum.tolist()[0]})
        self.thread_active = False

    def measureAll(self, timestep):
        self.thread = threading.Thread(target = self.__measureAll, args = (timestep,))
        self.thread.start()   

class channel():
    #setup so that each channel has a task with measurement type of Thermocouple or Voltage
    def __init__(self, name, sensor, ID):
        self.task = Task()
        self.name = name
        self.sensor = sensor
        self.ID = ID
        self.datum = np.zeros((1,), dtype = np.float64)

    def setup_task(self): #I should do a better job of recording temperatures and voltages and use the source clock
        #if type is thermocouple then setup a thermocouple task
        #if type is voltage then setup a voltage task
        if isinstance(self.sensor, thermocouple):
            self.task.CreateAIThrmcplChan(self.name,"", float(self.sensor.min_temp), float(self.sensor.max_temp), DAQmx_Val_Kelvins, self.sensor.type, self.sensor.cjc['type'], self.sensor.cjc['value'],"")
        elif isinstance(sensor, voltage):
            self.task.CreateAIVoltageChan(self.name, "", DAQmx_Val_Diff, -0.08, 0.08, DAQmx_Val_Volts, None)
        else:
            return None

    def measure(self):
        read = int32()
        self.task.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,self.datum,1,byref(read),None)


class thermocouple():
    def __init__(self,type,min_temp,max_temp,cjc):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.cjc = {} #need to set this independent of construtor
        self.set_type(type)
        self.set_cjc(cjc)

    def set_type(self,type): #Types are K and E
        if type == "E":
            self.type = DAQmx_Val_E_Type_TC
        elif type == "K":
            self.type = DAQmx_Val_K_Type_TC
        else:
            self.type = None

    def set_cjc(self, cjc): #cjc can be Built-In or Consant
        if cjc == "Built-in":
            self.cjc['type'] = DAQmx_Val_BuiltIn
            self.cjc['value'] = 0
        elif cjc == "Constant":
            self.cjc['type'] = DAQmx_Val_ConstVal
            self.cjc['value'] = 25
        else:
            self.cjc = {}

    def set_cjc_val(self,value):
        self.cjc['value'] = value

class voltage():
    def __init__(self,ID):
        self.ID = ID
    
#task = Task()
#task.CreateAIThrmcplChan('cDAQ1Mod1/ai2',"",77,1000, DAQmx_Val_Kelvins, DAQmx_Val_E_Type_TC,DAQmx_Val_BuiltIn,0,"")
#data = numpy.zeros((1,), dtype=numpy.float64)
#read = int32()
#task.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
#print data - 273.15
#time.sleep(1)
##task.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
##print data - 273.15
##task.ClearTask()

#task2 = Task()
#task2.CreateAIVoltageChan('cDAQ1Mod1/ai3', "", DAQmx_Val_Diff, -0.08, 0.08,DAQmx_Val_Volts,None)
#task2.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
#print data
 



