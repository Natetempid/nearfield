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
import datetime

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

        self.navigator_frame = tk.Frame(self)
        self.navigator_frame.grid(row = 1, column = 0, sticky = 'nsew')
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.navigator_frame)
        self.toolbar.update()

        self.get_coordinates_btn = ttk.Button(self, text = 'Select Intervals', command = lambda: self.get_coordinates())
        self.get_coordinates_btn.grid(row = 2, column = 0, sticky = 'nsew')

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

        self.select_btn = ttk.Button(self, text = 'Select Graph', command = lambda: self.select_graph())
        self.select_btn.grid(row = 1, column = 0, sticky = 'nsew')


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
        if self.getting_coordinates is None: #then button has been pressed just after initilization and need to start getting interals
            self.get_coordinates_btn.config(text = 'Stop Selecting Intervals... ')
            self.connectid = self.canvas.mpl_connect('button_press_event', self.on_click)
            self.getting_coordinates = True
        else:
            if self.getting_coordinates:
                #then stop getting coordinates
                self.get_coordinates_btn.config(text = 'Updating Curves...')
                #send selected coordinates to root
                self.root.selected_intervals = self.selected_intervals
                try:
                    self.canvas.mpl_disconnect(self.connectid)
                    self.root.use_intervals()
                    self.get_coordinates_btn.config(text = 'Select Intervals')
                except SystemError:
                    pass
            else:
                #then something went wrong.  Logic shouldn't allow this code to run 
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


