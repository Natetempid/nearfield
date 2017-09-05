from __future__ import print_function
import sys
import Tkinter as tk
import ttk
import numpy as np
import os
import datetime
from scipy import interpolate
import tkFileDialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import matplotlib.cm as cmx

import datetime

#classes
from model_frame import model_frame
from data_interpreter import data_interpreter
from thermal_resistor import thermal_resistor

class analyze_data(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)

        self.defaultdirectory = 'C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data'
        #self.defaultdirectory = '../../../experimental_data'
        self.f = None #file
        self.plot_total = 0
        self.interpreter_list = []
        self.selected_interpreter_list = []

        self.connectid = None
        self.getting_coordinates = False
        self.selected_intervals = []

        #Button Frame
        button_number = 1
        self.btn_frame = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.btn_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.btn_frame.grid_columnconfigure(0, weight = 1)		

        self.open_btn = ttk.Button(self.btn_frame, text = 'Show Raw Data', command = lambda: self.show_raw_data())#self.open_experiment())
        self.open_btn.grid(row = 0, column = 0, sticky = 'nsew')

        self.replot_selected_btn = ttk.Button(self.btn_frame, text = 'Replot Selected Graphs', command = lambda: self.replot_selected())
        self.replot_selected_btn.grid(row = 1, column = 0, sticky = 'nsew')	
        
        self.export_means_btn = ttk.Button(self.btn_frame, text = 'Export Interval Means', command = lambda: self.export_means())
        self.export_means_btn.grid(row = 2, column = 0, sticky = 'nsew')

        self.plot_selected_together_btn = ttk.Button(self.btn_frame, text = 'Plot Selected Together', command = lambda: self.plot_together())
        self.plot_selected_together_btn.grid(row = 3, column = 0, sticky = 'nsew')

        self.thermal_model_btn = ttk.Button(self.btn_frame, text = 'Fit to Thermal Model', command = lambda: self.thermal_model())
        self.thermal_model_btn.grid(row = 4, column = 0, sticky = 'nsew')

        #Plot Frame
        self.plot_frame = tk.Frame(self, borderwidth = 2)
        self.plot_frame.grid(row = 0, column = 1, sticky = 'nsew')
        #Replot Frame
        self.replot_frame = tk.Frame(self, borderwidth = 2)
        self.replot_frame.grid(row = 0, column = 1, sticky = 'nsew')
        #Plot Together Frame
        self.plot_together_frame = tk.Frame(self, borderwidth = 2)
        self.plot_together_frame.grid(row = 0, column = 1, sticky = 'nsew')
        self.plot_together_frame.grid_rowconfigure(0, weight = 1)
        self.plot_together_frame.grid_columnconfigure(0, weight = 1)
        #Model Frame
        self.thermal_frame = model_frame(self, self) #root and master are the same
        self.thermal_frame.grid(row = 0, column = 1, sticky = 'nsew')

        #plot power in model frame
        self.plot_frame.tkraise()

        self.open_experiment()

    def open_experiment(self):
        self.f = tkFileDialog.askdirectory(initialdir = self.defaultdirectory)
        #need to go down through the directories and get the various plots
        directory_list = os.listdir(self.f)
        #print directory_list
        for directory in directory_list:
            if 'lakeshore' in directory:
	            #Inputs A and B
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Input A', open('%s/lakeshore/inputA.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Input B', open('%s/lakeshore/inputB.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1
                #Output Amps
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Output 1 (Amps)', open('%s/lakeshore/output1Amps.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Output 2 (Amps)', open('%s/lakeshore/output2Amps.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1
                #Output Percent
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Output 1 (Percent)', open('%s/lakeshore/output1Percent.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Lakeshore Output 2 (Percent)', open('%s/lakeshore/output2Percent.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1

            if 'fluke' in directory:
                #Primary
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Fluke Primary', open('%s/fluke8808a/primarydisplay.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1

                #Check fluke secondary if anything is in there
                if os.stat('%s/fluke8808a/secondarydisplay.dat' % self.f).st_size > 0 :
                    self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Fluke Secondary', open('%s/fluke8808a/secondarydisplay.dat' % self.f, 'r'), self.plot_total))
                    self.plot_total = self.plot_total + 1

            if 'daq' in directory:
                daq_plotframe_list =  []
                for k in range(0,4):
                    self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'DAQ Channel %d' % k, open('%s/daq9211/channel%d.dat' % (self.f, k)), self.plot_total))
                    self.plot_total = self.plot_total + 1

            if 'keithley' in directory:
                #Applied Biase
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Applied Bias', open('%s/keithley/appliedbias.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1

	            #Measured Current
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Measured Current', open('%s/keithley/measuredcurrent.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1

	            #Measured Resistance
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Measured Resistance', open('%s/keithley/measuredresistance.dat' % self.f, 'r'), self.plot_total))
                self.plot_total = self.plot_total + 1	
        t0 = datetime.datetime.now()
        self.interpolate_all()
        print((datetime.datetime.now() - t0).total_seconds())
		#given number of plots, create proper grid of interperter_frames
        rows = int(np.floor(np.sqrt(self.plot_total)))
        columns = int(np.ceil(np.float64(self.plot_total)/np.float64(rows)))
        index = 0
        for k in range(0,rows):
            self.plot_frame.grid_rowconfigure(k, weight = 1)
            for l in range(0,columns):
                self.plot_frame.grid_columnconfigure(l, weight = 1)
                if index < self.plot_total:
                    self.interpreter_list[index].grid(row = k, column = l, sticky = 'nsew')
                    self.interpreter_list[index].plot_frame_row = k
                    self.interpreter_list[index].plot_frame_column = l
                    index = index + 1

    def replot_selected(self):
        #raise the replot_frame
        self.replot_frame.tkraise()
		#iterate over interpreter_list to see if any were selected
        plotframe_reinitialized = False
        total_selected = 0
        for interpreter in self.interpreter_list:
            #interpreter.grid_forget()
            if interpreter.selected:
                interpreter.reinit_toselectframe(self.replot_frame)
                self.selected_interpreter_list.append(interpreter)
                total_selected = total_selected + 1

        rows = int(np.floor(np.sqrt(total_selected)))
        columns = int(np.ceil(np.float64(total_selected)/np.float64(rows)))
        index = 0

        for k in range(0,rows):
            print('k = %d' % k) 
            self.replot_frame.grid_rowconfigure(k, weight = 1)
            for l in range(0,columns):
                print('l = %d' % l)
                self.replot_frame.grid_columnconfigure(l, weight = 1)
                if index < total_selected:
                    self.selected_interpreter_list[index].grid(row = k, column = l, sticky = 'nsew')
                    #self.selected_interpreter_list[index].config(border = 5, relief = tk.GROOVE)
                    index = index + 1

    def use_intervals(self):
        if self.selected_intervals: #then list isn't empty
            if not np.mod(len(self.selected_intervals),2):
            #then selected_times has an even number of entries
                #raise the plot list but change the data in each interpreter
                self.plot_frame.tkraise()
                for k in range(0,len(self.selected_intervals)/2):
                    t0 = self.selected_intervals[2*k]
                    t1 = self.selected_intervals[2*k+1]
                    for interpreter in self.interpreter_list:
                        
                        interpreter.selected_time = interpreter.selected_time + [t for t in interpreter.time if t > t0 and t <= t1]
                        interpreter.selected_data = interpreter.selected_data + [interpreter.data[k] for k,t in enumerate(interpreter.time) if t > t0 and t <= t1]
                        interpreter.mean_time.append(t0+(t1-t0)/2)
                        interpreter.mean_data.append(np.mean([interpreter.data[k] for k,t in enumerate(interpreter.time) if t > t0 and t <= t1]))
                        interpreter.std_dev.append(np.std([interpreter.data[k] for k,t in enumerate(interpreter.time) if t > t0 and t <= t1]))
                        
            #once I've gone through each interval, replot          
            for interpreter in self.interpreter_list:            
                interpreter.reinit_toplotframe(self.plot_frame) #if the interpreter was previously selected then its master has changed and it needs to be reinitialized back such that the plot_frame is the master
                interpreter.grid(row = interpreter.plot_frame_row, column = interpreter.plot_frame_column, sticky = 'nsew')
                interpreter.remove_plot()
                interpreter.line,  = interpreter.ax.plot(interpreter.selected_time, interpreter.selected_data, '.')
                interpreter.ax.plot(interpreter.mean_time, interpreter.mean_data, 'ro')
            
                interpreter.canvas.draw()

    def show_raw_data(self):
        self.plot_frame.tkraise()
        for interpreter in self.interpreter_list:            
            interpreter.reinit_toplotframe(self.plot_frame) #if the interpreter was previously selected then its master has changed and it needs to be reinitialized back such that the plot_frame is the master
            interpreter.grid(row = interpreter.plot_frame_row, column = interpreter.plot_frame_column, sticky = 'nsew')
            interpreter.remove_plot()
            interpreter.line,  = interpreter.ax.plot(interpreter.time, interpreter.data) #raw data instead of selected data
            interpreter.ax.plot(interpreter.mean_time, interpreter.mean_data, 'ro')
            interpreter.canvas.draw()

    def plot_together(self):
        #take data from selected data interpreter and put on same figure
        self.plot_together_frame.tkraise()
        #initialize figure here
        f = plt.Figure()
        ax = f.add_subplot(1,1,1)

        colmap = cm = plt.get_cmap('rainbow') 
        cNorm  = colors.Normalize(vmin=0, vmax=len(self.interpreter_list))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=colmap)
        lines = [ax.plot(interpreter.time, interpreter.data, color = scalarMap.to_rgba(k), label = interpreter.name )[0] for k, interpreter in enumerate(self.interpreter_list) if interpreter.selected]
        
        ax.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)

        together_canvas = FigureCanvasTkAgg(f,self.plot_together_frame)
        together_canvas.show()
        together_canvas_widget = together_canvas.get_tk_widget()
        together_canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        together_canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        together_navigator_frame = tk.Frame(self.plot_together_frame)
        together_navigator_frame.grid(row = 1, column = 0, sticky = 'nsew')
        together_toolbar = NavigationToolbar2TkAgg(together_canvas, together_navigator_frame)
        together_toolbar.update()

    def __timestr(self, utctimestamp):
        return datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(utctimestamp), '%Y-%m-%d %H:%M:%S.%f')
        
    def write2file(self, interpreter, file):
        for k in range(0, len(interpreter.mean_time) ):
            timestr = self.__timestr(interpreter.mean_time[k])
            file.write('%s,%g\n' % (timestr, interpreter.mean_data[k]))

    def writemean2file(self, interpreter, file):
        for k in range(0, len(interpreter.mean_time) ):
            timestr = self.__timestr(interpreter.mean_time[k])
            file.write('%s,%g,%g\n' % (timestr, interpreter.mean_data[k], interpreter.std_dev[k]))

    def export_means(self):
        mean_directory = self.create_mean_directory()
        for interpreter in self.interpreter_list:
            #Lakeshore
            if 'Lakeshore' in interpreter.name:
                #Assign 'lakeshore' directory if necessary
                if not os.path.exists('%s/lakeshore' % mean_directory):
                    os.makedirs('%s/lakeshore' % mean_directory)

                if interpreter.name == 'Lakeshore Input A':  
                    mean_file = open('%s/lakeshore/inputA.dat' % mean_directory, 'w')
                if interpreter.name == 'Lakeshore Input B':
                   mean_file = open('%s/lakeshore/inputB.dat' % mean_directory, 'w')
                if interpreter.name == 'Lakeshore Output 1 (Amps)':
                   mean_file = open('%s/lakeshore/output1Amps.dat' % mean_directory, 'w')
                if interpreter.name == 'Lakeshore Output 2 (Amps)':
                    mean_file = open('%s/lakeshore/output2Amps.dat' % mean_directory, 'w')
                if interpreter.name == 'Lakeshore Output 1 (Percent)':
                    mean_file = open('%s/lakeshore/output1Percent.dat' % mean_directory, 'w')
                if interpreter.name == 'Lakeshore Output 2 (Percent)':
                    mean_file = open('%s/lakeshore/output2Percent.dat' % mean_directory, 'w')
            #Fluke
            if 'Fluke' in interpreter.name:
                #Assign 'fluke8808a' directory if necessary
                if not os.path.exists('%s/fluke8808a' % mean_directory):
                    os.makedirs('%s/fluke8808a' % mean_directory)

                if interpreter.name == 'Fluke Primary':
                    mean_file = open('%s/fluke8808a/primarydisplay.dat' % mean_directory, 'w')
                if interpreter.name == 'Fluke Secondary':
                    mean_file = open('%s/fluke8808a/secondarydisplay.dat' % mean_directory, 'w')
            #DAQ
            if 'DAQ' in interpreter.name:
                #Assign 'daq9211' directory if necessary
                if not os.path.exists('%s/daq9211' % mean_directory):
                    os.makedirs('%s/daq9211' % mean_directory)

                for l in range(0,4):
                    if interpreter.name == ('DAQ Channel %d' % l):
                        mean_file = open('%s/daq9211/channel%d.dat' % (mean_directory, l), 'w')
            #Keithley
            if 'Keithley' in interpreter.name:
                #Assign 'keithley' directory if necessary
                if not os.path.exists('%s/keithley' % mean_directory):
                    os.makedirs('%s/keithley' % mean_directory)

                if interpreter.name =='Keithley Applied Bias':
                   mean_file = open('%s/keithley/appliedbias.dat' % mean_directory, 'w')
                if interpreter.name == 'Keithley Measured Current':
                   mean_file = open('%s/keithley/measuredcurrent.dat' % mean_directory, 'w')
                if interpreter.name == 'Keithley Measured Resistance':
                   mean_file = open('%s/keithley/measuredresistance.dat' % mean_directory, 'w')
            self.writemean2file(interpreter, mean_file)

    def create_mean_directory(self):
        #create an interval means directory - note: there can be multiple means directories, so they will be labeled with a time stamp
        time_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        newfile_str = '%s\\intervalmeans_%s' % (self.f, time_str)
        if not os.path.exists(newfile_str):
            os.makedirs(newfile_str)
            return newfile_str
        else:
            return -1

    def init_datafiles(self, instrument, instrument_directory):
        #Lakeshore
        if isinstance(instrument, lakeshore335):
            file_inputA = open('%s\\inputA.dat' % instrument_directory, 'w',0)
            file_inputB = open('%s\\inputB.dat' % instrument_directory, 'w',0)
            file_output1Amps = open('%s\\output1Amps.dat' % instrument_directory, 'w',0)
            file_output2Amps = open('%s\\output2Amps.dat' % instrument_directory, 'w',0)
            file_output1Percent = open('%s\\output1Percent.dat' % instrument_directory, 'w',0)
            file_output2Percent = open('%s\\output2Percent.dat' % instrument_directory, 'w',0)
            return [file_inputA, file_inputB, file_output1Amps , file_output2Amps, file_output1Percent, file_output2Percent]
        #Fluke
        if isinstance(instrument, fluke8808a):
            file_primary = open('%s\\primarydisplay.dat' % instrument_directory, 'w',0)
            file_secondary = open('%s\\secondarydisplay.dat' % instrument_directory, 'w',0)
            return [file_primary, file_secondary]
        #Keithley
        if isinstance(instrument, keithley2410):
            file_appliedBias = open('%s\\appliedbias.dat' % instrument_directory, 'w',0)
            file_measuredCurrent = open('%s\\measuredcurrent.dat' % instrument_directory, 'w',0)
            file_measuredResistance = open('%s\\measuredresistance.dat' % instrument_directory, 'w',0)
            return [file_appliedBias, file_measuredCurrent, file_measuredResistance]
        #DAQ
        if isinstance(instrument, daq9211):
            file_channel0 = open('%s\\channel0.dat' % instrument_directory, 'w',0)
            file_channel1 = open('%s\\channel1.dat' % instrument_directory, 'w',0)
            file_channel2 = open('%s\\channel2.dat' % instrument_directory, 'w',0)
            file_channel3 = open('%s\\channel3.dat' % instrument_directory, 'w',0)
            return [file_channel0, file_channel1, file_channel2, file_channel3]

    def thermal_model(self):
        self.thermal_frame.tkraise()
        #self.thermal_frame.update_plots()

    def interpolate_all(self):
        time_start = np.max([np.min(interpreter.time) for interpreter in self.interpreter_list])
        time_end = np.min([np.max(interpreter.time) for interpreter in self.interpreter_list])
        for interpreter in self.interpreter_list:
            interp_time = np.arange(time_start,time_end)
            interp_data = np.interp(interp_time, interpreter.time, interpreter.data)
            interpreter.time = interp_time
            interpreter.data = interp_data




def main():
    app = analyze_data()
    app.geometry('1750x1000')
    app.mainloop()
    

if __name__ == '__main__':
    main()


