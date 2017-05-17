from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
import numpy as np
from numpy import zeros
import time
import datetime 
import threading

class daq9211():
    def __init__(self, name):
        self.name = name
        self.channels = []
        self.data = {}
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False
        self.callbackID = 0

    def add_channel(self, channel):
        self.channels.append(channel)
        self.data[channel.name] = []
    
    def set_callbackID(self,k):
        self.callbackID = k #the callbackID should be the channel index in self.channels that corresponds to the taskHandle in the 

    def EveryNCallback_py(self, taskHandle, everyNsamplesEventType, nSamples, callbackData_ptr):
        callbackdata = get_callbackdata_from_id(callbackData_ptr)
        read = int32()
        data = zeros(1)
        t1 = datetime.datetime.now()
        DAQmxReadAnalogF64(taskHandle,1,10.0,DAQmx_Val_GroupByScanNumber,data,6,byref(read),None)
        callbackdata.extend(data.tolist())
        print "Channel %d samples after %.4f seconds " % (self.callbackID, (datetime.datetime.now() - t1).total_seconds())
        self.channels[self.callbackID].data.append({'datetime': datetime.datetime.now(), 'data': np.mean(data)})
        return 0 # The function should return an integer
        
    def DoneCallback_py(self, taskHandle, status, callbackData):
        print "Status",status.value
        return 0 # The function should return an integer

    def __measureAll(self, timestep, start_restart):
        self.stop_event.clear()
        self.thread_active = True
        data = MyList()
        id_a = create_callbackdata_id(data)
        #for k in range(0,len(self.channels)):
        k = 0
        

        #Convert the python function to a CFunction      
        EveryNCallback = DAQmxEveryNSamplesEventCallbackPtr(self.EveryNCallback_py) #can't call this every time. Each callback function must be unique
        DoneCallback = DAQmxDoneEventCallbackPtr(self.DoneCallback_py)

        if start_restart == "start": #start restart is still a problem 
            DAQmxRegisterEveryNSamplesEvent(self.channels[k].taskHandle,DAQmx_Val_Acquired_Into_Buffer,1,0,EveryNCallback,id_a)
            DAQmxRegisterDoneEvent(self.channels[k].taskHandle,0,DoneCallback,None)
        DAQmxStartTask(self.channels[k].taskHandle)

        while (not self.stop_event.is_set()):
            pass
    #    for k in range(0,len(self.channels)):
        DAQmxStopTask(self.channels[0].taskHandle)
        self.thread_active = False

    def measureAll(self, timestep, start_restart):
        self.thread = threading.Thread(target = self.__measureAll, args = (timestep,start_restart))
        self.thread.start()   

    def close(self):
        for k in range(0,len(self.channels)):
            self.channels[k].DAQmxClearTask(self.channels[k].taskHandle)

class MyList(list):
    pass

class channel():
    #setup so that each channel has a task with measurement type of Thermocouple or Voltage
    def __init__(self, name, sensor, ID):
        #self.task = Task()
        self.taskHandle = TaskHandle()
        DAQmxCreateTask("",byref(self.taskHandle))
        self.name = name
        self.sensor = sensor
        self.ID = ID
        self.data= []
        self.datum = np.zeros((1,), dtype = np.float64)

    def setup_task(self): #I should do a better job of recording temperatures and voltages and use the source clock
        #if type is thermocouple then setup a thermocouple task
        #if type is voltage then setup a voltage task
        if isinstance(self.sensor, thermocouple):
            DAQmxCreateAIThrmcplChan(self.taskHandle,self.name,"", float(self.sensor.min_temp), float(self.sensor.max_temp), DAQmx_Val_Kelvins, self.sensor.type, self.sensor.cjc['type'], self.sensor.cjc['value'],"")
            DAQmxCfgSampClkTiming(self.taskHandle,"",6,DAQmx_Val_Rising,DAQmx_Val_ContSamps,6)
        elif isinstance(sensor, voltage):
            DAQmxCreateAIVoltageChan(self.taskHandle,self.name, "", DAQmx_Val_Diff, -0.08, 0.08, DAQmx_Val_Volts, None)
            DAQmxCfgSampClkTiming(self.taskHandle,"",6,DAQmx_Val_Rising,DAQmx_Val_ContSamps,6)
        else:
            return None

    def measure(self):
        read = int32()
        t1 = datetime.datetime.now()
        DAQmxReadAnalogF64(self.taskHandle,1,10.0,DAQmx_Val_GroupByChannel,self.datum,1,byref(read),None)
        print (datetime.datetime.now() - t1).total_seconds()

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
 



## list where the data are stored




## Define two Call back functions
#def EveryNCallback_py(taskHandle, everyNsamplesEventType, nSamples, callbackData_ptr):
#    callbackdata = get_callbackdata_from_id(callbackData_ptr)
#    read = int32()
#    data = zeros(5)
#    t1 = datetime.datetime.now()
#    DAQmxReadAnalogF64(taskHandle,5,10.0,DAQmx_Val_GroupByScanNumber,data,10,byref(read),None)
#    callbackdata.extend(data.tolist())
#    print "Acquired total %d samples after %.4f seconds " % (len(data), (datetime.datetime.now() - t1).total_seconds())
#    return 0 # The function should return an integer

## Convert the python function to a CFunction      
#EveryNCallback = DAQmxEveryNSamplesEventCallbackPtr(EveryNCallback_py)

#def DoneCallback_py(taskHandle, status, callbackData):
#    print "Status",status.value
#    return 0 # The function should return an integer

## Convert the python function to a CFunction      
#DoneCallback = DAQmxDoneEventCallbackPtr(DoneCallback_py)


## Beginning of the script

##DAQmxResetDevice('cDAQ1Mod1')

#taskHandle=TaskHandle()
#DAQmxCreateTask("",byref(taskHandle))
#DAQmxCreateAIVoltageChan(taskHandle,"cDAQ1Mod1/ai0","",DAQmx_Val_Diff,-0.08,0.08,DAQmx_Val_Volts,None)
#DAQmxCfgSampClkTiming(taskHandle,"",10,DAQmx_Val_Rising,DAQmx_Val_ContSamps,10)

#DAQmxRegisterEveryNSamplesEvent(taskHandle,DAQmx_Val_Acquired_Into_Buffer,1,0,EveryNCallback,id_a)
#DAQmxRegisterDoneEvent(taskHandle,0,DoneCallback,None)

#DAQmxStartTask(taskHandle)

#raw_input('Acquiring samples continuously. Press Enter to interrupt\n')

#DAQmxStopTask(taskHandle)
#DAQmxClearTask(taskHandle)



