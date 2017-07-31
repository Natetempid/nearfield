
from __future__ import print_function
import sys
import Tkinter as tk
import tkFileDialog
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
from scipy import interpolate

class data_interpreter():
    #single instrument
    def __init__(self, name, file, plot_index):
        self.name = name #this will be plot title
        self.file = file #open file not file path
        self.plot_index = plot_index #where to plot the data
        self.time = []
        self.data = []
        self.units = []
        self.read_data()
        self.selected_time = []
        self.selected_data = []
        self.mean_time = []
        self.mean_data = []

    def read_data(self):
        for line in self.file:
            datalist = line.split(',')
            if len(datalist) > 1:
                try:
                    self.time.append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()))
                    self.data.append(float(datalist[1]))
                except ValueError:
                    try:
                        self.time.append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds()))
                        self.data.append(float(datalist[1]))
                    except ValueError:
                        pass
                if len(datalist) > 2:
                    self.units.append(datalist[2])
                else:
                    self.units.append(None)

global f
global fig
global interpreter_list
global defaultdirectory
global axes
global plot_total
global selected_times

fig = plt.Figure()
interpreter_list = []
defaultdirectory = 'C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data'
axes = []
plot_total = 0
selected_times = []

def open_experiment():
    global f
    global plot_total
    global interpreter_list
    
    f = tkFileDialog.askdirectory(initialdir = defaultdirectory)
    #need to go down through the directories and get the various plots
    directory_list = os.listdir(f)
    #print directory_list
    for directory in directory_list:
        if 'lakeshore' in directory:
            #Inputs A and B
            interpreter_list.append(data_interpreter('Lakeshore Input A', open('%s\\lakeshore\\inputA.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
            interpreter_list.append(data_interpreter('Lakeshore Input B', open('%s\\lakeshore\\inputB.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
            #Output Amps
            interpreter_list.append(data_interpreter('Lakeshore Output 1 (Amps)', open('%s\\lakeshore\\output1Amps.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
            interpreter_list.append(data_interpreter('Lakeshore Output 2 (Amps)', open('%s\\lakeshore\\output2Amps.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
            #Output Percent
            interpreter_list.append(data_interpreter('Lakeshore Output 1 (Percent)', open('%s\\lakeshore\\output1Percent.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
            interpreter_list.append(data_interpreter('Lakeshore Output 2 (Percent)', open('%s\\lakeshore\\output2Percent.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1

        if 'fluke' in directory:
            #Primary
            interpreter_list.append(data_interpreter('Fluke Primary', open('%s\\fluke8808a\\primarydisplay.dat' % f, 'r'), plot_total))
            plot_total = plot_total + 1
                                   
            #Check fluke secondary if anything is in there
            if os.stat('%s\\fluke8808a\\secondarydisplay.dat' % f).st_size > 0 :
                interpreter_list.append(data_interpreter('Fluke Secondary', open('%s\\fluke8808a\\secondarydisplay.dat' % f, 'r'), plot_total))
                plot_total = plot_total + 1

        if 'daq' in directory:
            daq_plotframe_list =  []
            for k in range(0,4):
                interpreter_list.append(data_interpreter('DAQ Channel %d' % k, open('%s\\daq9211\\channel%d.dat' % (f, k)), plot_total))
                plot_total = plot_total + 1

        if 'keithley' in directory:
            #Applied Biase
            interpreter_list.append(data_interpreter('Keithley Applied Bias', '%s\\keithley\\appliedbias.dat' % f, plot_total))
            plot_total = plot_total + 1

            #Measured Current
            interpreter_list.append(data_interpreter('Keithley Measured Current', '%s\\keithley\\measuredcurrent.dat' % f, plot_total))
            plot_total = plot_total + 1

            #Measured Resistance
            interpreter_list.append(data_interpreter('Keithley Measured Resistance', '%s\\keithley\\measuredresistance.dat' % f, plot_total))
            plot_total = plot_total + 1

def plot_data():
    global f
    global fig
    global interpreter_list
    global defaultdirectory
    global axes
    global plot_total
    
    open_experiment()
    #open experiment updates the plot_total parameter
    rows = np.floor(np.sqrt(plot_total))
    columns = np.ceil(plot_total/rows)
    for interpreter in interpreter_list:
        axes.append(plt.subplot(rows, columns, interpreter.plot_index+1))
        axes[interpreter.plot_index].plot(interpreter.time, interpreter.data)
        axes[interpreter.plot_index].set_title(interpreter.name)
    connectid = plt.connect('button_press_event', on_click)
    plt.draw()  
   
def replot_data():
    global f
    global fig
    global interpreter_list
    global defaultdirectory
    global axes
    global selected_times
    global plot_total

    fig = plt.Figure()
    axes = []

    rows = np.floor(np.sqrt(plot_total))
    columns = np.ceil(plot_total/rows)
    for interpreter in interpreter_list:
        axes.append(plt.subplot(rows, columns, interpreter.plot_index+1))

    #get selected data
    if not np.mod(len(selected_times),2):
        #then selected_times has an even number of entries
        for k in range(0,len(selected_times)/2):
            t0 = selected_times[2*k]
            t1 = selected_times[2*k+1]
            for interpreter in interpreter_list:
                interpreter.selected_time = interpreter.selected_time + [t for t in interpreter.time if t > t0 and t <= t1]
                interpreter.selected_data = interpreter.selected_data + [interpreter.data[k] for k,t in enumerate(interpreter.time) if t > t0 and t <= t1]
                interpreter.mean_time.append(t0+(t1-t0)/2)
                interpreter.mean_data.append(np.mean([interpreter.data[k] for k,t in enumerate(interpreter.time) if t > t0 and t <= t1]))
                axes[interpreter.plot_index].plot(interpreter.selected_time, interpreter.selected_data)
                axes[interpreter.plot_index].plot(interpreter.mean_time, interpreter.mean_data, marker = "o", color = "r")
    
    plt.draw()  


def close_all():
    global interpreter_list
    
    for interpreter in interpreter_list:
        interpreter.file.close()
        
def on_click(event):
    # get the x and y coords, flip y from top to bottom
    global selected_times
    x, y = event.x, event.y
    if event.button == 1:
        if event.inaxes is not None:
            print('data coords %f %f' % (event.xdata, event.ydata))
            selected_times.append(event.xdata)

plt.connect('button_press_event', on_click)

if "test_disconnect" in sys.argv:
    print("disconnecting console coordinate printout...")
    plt.disconnect(binding_id)

#tk.withdraw()
plot_data()
plt.show()

print (selected_times)

#now that times have been selected, replot just the requested data

replot_data()
plt.show()
#get sensorcalibration

calibration_factor = 1.9*10**(-6)

calibration_file = open('C:\\Users\\Nate\\Source\\Repos\\nearfield\\Analyze_NearfieldData\\Analyze_NearfieldData\\calibrationfactor.csv', 'r')
calibration_temp = [float(line.split(',')[0]) for line in calibration_file]
calibration_file.seek(0)
calibration_value = [calibration_factor*float(line.strip().split(',')[1]) for line in calibration_file]
calibration = interpolate.interp1d(calibration_temp, calibration_value, kind = 'cubic')

#daq1 is the temperature of the heat flux sensor
for interpreter in interpreter_list:
    if interpreter.name == "DAQ Channel 0":
        data = np.array(interpreter.mean_data)
    if interpreter.name == "DAQ Channel 2":
        absorber_temp = np.array(interpreter.mean_data)
        updated_calibration_factors = calibration(absorber_temp)
    if interpreter.name == 'Lakeshore Input B':
        emitter_temp = np.array(interpreter.mean_data)
        
heatflux = -1*data/updated_calibration_factors

#fit
k_cu = 385
k_glass = 1.3

l_cu = 1e-3
l_glass = 1e-3

A_cu = 0.0254**2*1.2*1.6
A_glass = 0.0254**2

r_cu = l_cu/(A_cu*k_cu)
r_glass = l_glass/(A_glass*k_glass)

r_interface = 1.013

r_total = r_glass+r_interface+r_cu

plt.plot(emitter_temp - absorber_temp, (emitter_temp - absorber_temp)/r_total, color = 'b')
plt.plot(emitter_temp - absorber_temp, heatflux, marker = 'o', color = 'r')
plt.xlabel(r'$\Delta$ T')
plt.ylabel('Heat Flux (W/m^2')
plt.show()