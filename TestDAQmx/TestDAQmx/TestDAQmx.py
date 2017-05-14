
from PyDAQmx import *
import numpy
import time


task = Task()
task.CreateAIThrmcplChan('cDAQ1Mod1/ai2',"",77,1000, DAQmx_Val_Kelvins, DAQmx_Val_E_Type_TC,DAQmx_Val_BuiltIn,0,"")
data = numpy.zeros((1,), dtype=numpy.float64)
read = int32()
task.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
print data - 273.15
time.sleep(1)
#task.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
#print data - 273.15
#task.ClearTask()

task2 = Task()
task2.CreateAIVoltageChan('cDAQ1Mod1/ai3', "", DAQmx_Val_Diff, -0.08, 0.08,DAQmx_Val_Volts,None)
task2.ReadAnalogF64(1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
print data
 
