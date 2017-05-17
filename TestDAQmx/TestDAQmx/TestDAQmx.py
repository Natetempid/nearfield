
#from PyDAQmx import *
#import numpy
#import time


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
 
from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
from numpy import zeros
import datetime

"""This example is a PyDAQmx version of the ContAcq_IntClk.c example
It illustrates the use of callback functions
This example demonstrates how to acquire a continuous amount of 
data using the DAQ device's internal clock. It incrementally stores the data 
in a Python list. 
"""



# one cannot create a weakref to a list directly
# but the following works well
class MyList(list):
    pass

# list where the data are stored
data = MyList()
id_a = create_callbackdata_id(data)



# Define two Call back functions
def EveryNCallback_py(taskHandle, everyNsamplesEventType, nSamples, callbackData_ptr):
    callbackdata = get_callbackdata_from_id(callbackData_ptr)
    read = int32()
    data = zeros(5)
    t1 = datetime.datetime.now()
    DAQmxReadAnalogF64(taskHandle,5,10.0,DAQmx_Val_GroupByScanNumber,data,10,byref(read),None)
    callbackdata.extend(data.tolist())
    print "Acquired total %d samples after %.4f seconds " % (len(data), (datetime.datetime.now() - t1).total_seconds())
    return 0 # The function should return an integer

# Convert the python function to a CFunction      
EveryNCallback = DAQmxEveryNSamplesEventCallbackPtr(EveryNCallback_py)

def DoneCallback_py(taskHandle, status, callbackData):
    print "Status",status.value
    return 0 # The function should return an integer

# Convert the python function to a CFunction      
DoneCallback = DAQmxDoneEventCallbackPtr(DoneCallback_py)


# Beginning of the script

#DAQmxResetDevice('cDAQ1Mod1')

taskHandle=TaskHandle()
DAQmxCreateTask("",byref(taskHandle))
DAQmxCreateAIVoltageChan(taskHandle,"cDAQ1Mod1/ai0","",DAQmx_Val_Diff,-0.08,0.08,DAQmx_Val_Volts,None)
DAQmxCfgSampClkTiming(taskHandle,"",10,DAQmx_Val_Rising,DAQmx_Val_ContSamps,10)

DAQmxRegisterEveryNSamplesEvent(taskHandle,DAQmx_Val_Acquired_Into_Buffer,1,0,EveryNCallback,id_a)
DAQmxRegisterDoneEvent(taskHandle,0,DoneCallback,None)

DAQmxStartTask(taskHandle)

raw_input('Acquiring samples continuously. Press Enter to interrupt\n')

DAQmxStopTask(taskHandle)
DAQmxStartTask(taskHandle)
raw_input('Acquiring samples continuously. Press Enter to interrupt\n')

DAQmxClearTask(taskHandle)
