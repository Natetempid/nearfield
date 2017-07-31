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
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime

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

        self.open_btn = ttk.Button(self.btn_frame, text = 'Open Experiment', command = lambda: self.open_experiment())
        self.open_btn.grid(row = 0, column = 0, sticky = 'nsew')

        self.replot_selected_btn = ttk.Button(self.btn_frame, text = 'Replot Selected Graphs', command = lambda: self.replot_selected())
        self.replot_selected_btn.grid(row = 1, column = 0, sticky = 'nsew')		

        self.use_coordinates_btn = ttk.Button(self.btn_frame, text = 'Apply Selected Time Intervals', command = lambda: self.use_intervals())
        self.use_coordinates_btn.grid(row = 2, column = 0, sticky = 'nsew')

        self.thermal_model_btn = ttk.Button(self.btn_frame, text = 'Fit to Thermal Model', command = lambda: self.thermal_model())
        self.thermal_model_btn.grid(row = 3, column = 0, sticky = 'nsew')

        #Plot Frame
        self.plot_frame = tk.Frame(self, borderwidth = 2)
        self.plot_frame.grid(row = 0, column = 1, sticky = 'nsew')
        #Replot Frame
        self.replot_frame = tk.Frame(self, borderwidth = 2)
        self.replot_frame.grid(row = 0, column = 1, sticky = 'nsew')
        #Model Frame
        self.model_frame = tk.Frame(self, borderwidth = 2)
        self.model_frame.grid(row = 0, column = 1, sticky = 'nsew')
        self.plot_frame.tkraise()

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
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Applied Bias', '%s/keithley/appliedbias.dat' % self.f, self.plot_total))
                self.plot_total = self.plot_total + 1

	            #Measured Current
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Measured Current', '%s/keithley/measuredcurrent.dat' % self.f, self.plot_total))
                self.plot_total = self.plot_total + 1

	            #Measured Resistance
                self.interpreter_list.append(data_interpreter(self.plot_frame, self, 'Keithley Measured Resistance', '%s/keithley/measuredresistance.dat' % self.f, self.plot_total))
                self.plot_total = self.plot_total + 1	

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

		#the grid growth is working properly 2017-07-26

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
                        
            #once I've gone through each interval, replot          
            for interpreter in self.interpreter_list:            
                interpreter.reinit_toplotframe(self.plot_frame) #if the interpreter was previously selected then its master has changed and it needs to be reinitialized back such that the plot_frame is the master
                interpreter.grid(row = interpreter.plot_frame_row, column = interpreter.plot_frame_column, sticky = 'nsew')
                interpreter.remove_plot()
                interpreter.line,  = interpreter.ax.plot(interpreter.selected_time, interpreter.selected_data, '.')
                interpreter.ax.plot(interpreter.mean_time, interpreter.mean_data, 'ro')
                interpreter.canvas.draw()
    
                    

class data_interpreter(tk.Frame):
    #single instrument
    def __init__(self, master, root, name, file, plot_index):
        tk.Frame.__init__(self, master)
        self.config(border = 2)
        self.master = master
        self.root = root
        self.plot_frame_row = -1
        self.plot_frame_column = -1

        self.grid_rowconfigure(0,weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.name = name #this will be plot title
        self.file = file #open file not file path
        self.plot_index = plot_index #where to plot the data
        self.time = []
        self.data = []
        self.units = []

        #read data
        self.read_data()

        #plot_data
        self.fig = plt.Figure()#figsize=(10,10))
        self.ax = self.fig.add_subplot(1,1,1)
        self.line, = self.ax.plot(self.time, self.data)
        self.ax.set_title(self.name)
        self.canvas = FigureCanvasTkAgg(self.fig,self)
        self.canvas.show()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

        self.selected = False

        self.selected_intervals = [] #times for the beginning and end of each interval
        self.selected_vlines = [] #lines to place at selected intervals
                
        self.selected_time = [] #times within interval to plot
        self.selected_data = [] #cooresponding data to plot
        self.mean_time = []
        self.mean_data = []

        self.getting_coordinates = False
        self.connectid = None

        #select button
        self.select_btn = ttk.Button(self, text = 'Select Graph', command = lambda: self.select_graph())
        self.select_btn.grid(row = 1, column = 0, sticky = 'nsew')

    def reinit_toselectframe(self, master):
        self.master = master #overwrite previous master frame
        tk.Frame.__init__(self, self.master)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.config(border = 2, relief = tk.GROOVE)
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.line, = self.ax.plot(self.time, self.data)
        self.ax.set_title(self.name)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

        self.get_coordinates_btn = ttk.Button(self, text = 'Select Intervals', command = lambda: self.get_coordinates())
        self.get_coordinates_btn.grid(row = 1, column = 0, sticky = 'nsew')

    def reinit_toplotframe(self, master):
        self.master = master #overwrite previous master frame
        tk.Frame.__init__(self, self.master)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.config(border = 2, relief = tk.GROOVE)
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.line, = self.ax.plot(self.time, self.data)
        self.ax.set_title(self.name)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

        #self.select_btn = ttk.Button(self, text = 'Select Graph', command = lambda: self.select_graph())
        #self.select_btn.grid(row = 1, column = 0, sticky = 'nsew')


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

    def select_graph(self):
        if self.selected:
            self.select_btn.config(text = 'Select Graph')
            self.config(relief = tk.FLAT)
        else:
            self.select_btn.config(text = 'Unselect Graph')
            self.config(relief = tk.GROOVE)
        self.selected = not self.selected

    def remove_plot(self):
        self.ax.lines.remove(self.line)

    def get_coordinates(self):
        if self.getting_coordinates:
            #then stop getting coordinates
            self.get_coordinates_btn.config(text = 'Select Intervals')
            #send selected coordinates to root
            self.root.selected_intervals = self.selected_intervals
            try:
                self.canvas.mpl_disconnect(self.connectid)
            except SystemError:
                pass
        else:
            #then start getting coordinates
            self.get_coordinates_btn.config(text = 'Stop Selecting Intervals... ')
            self.connectid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.getting_coordinates = not self.getting_coordinates

    def on_click(self, event):
        #get the x and y coords, flip y from top to bottom
        x, y = event.x, event.y
        if event.button == 1:
            if event.inaxes is not None:
                print('data coords %f %f' % (event.xdata, event.ydata))
                #self.root.selected_times.append(event.xdata)
                self.selected_intervals.append(event.xdata)
                #plot vertical lines on this interpreter
                line = self.ax.axvline(x = event.xdata, color = 'r')
                self.selected_vlines.append(line)

                #plot vertical lines on other selected interpreters
                for interpreter in self.root.selected_interpreter_list:
                    if interpreter.name != self.name: #only do this for other selected interpreters
                        other_line = interpreter.ax.axvline(x = event.xdata, color = 'r')
                        interpreter.selected_vlines.append(other_line)
                        interpreter.canvas.draw()
        if event.button == 3:
            if event.inaxes is not None:
                self.selected_intervals = self.selected_intervals[:-1]
                self.ax.lines.remove(self.selected_vlines[-1])
                #remove vertical lines from other selected interpreters
                for interpreter in self.root.selected_interpreter_list:
                    if interpreter.name != self.name: #only do this for other selected interpreters
                        interpreter.ax.lines.remove(interpreter.selected_vlines[-1])
                        interpreter.canvas.draw()

        self.canvas.draw()

      



def main():
    app = analyze_data()
    app.geometry('1750x1000')
    app.mainloop()
    

if __name__ == '__main__':
    main()


	
	

