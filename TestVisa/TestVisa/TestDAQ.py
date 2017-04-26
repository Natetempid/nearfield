from PyDAQmx import *
import numpy

# Declaration of variable passed by reference
taskHandle = TaskHandle()
read = int32()
data = numpy.zeros((50,), dtype=numpy.float64)

try:
    # DAQmx Configure Code
    DAQmxCreateTask("",byref(taskHandle))
    DAQmxCreateAIVoltageChan(taskHandle,"cDAQ1Mod1/ai0","",DAQmx_Val_Cfg_Default,-0.08,0.08,DAQmx_Val_Volts,None)
    DAQmxCfgSampClkTiming(taskHandle,"",10.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,50)

    # DAQmx Start Code
    DAQmxStartTask(taskHandle)

    # DAQmx Read Code
    DAQmxReadAnalogF64(taskHandle,1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)

    print "Acquired %d points"%read.value
except DAQError as err:
    print "DAQmx Error: %s"%err
finally:
    if taskHandle:
        # DAQmx Stop Code
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)