

import Tkinter as tk
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.animation as animation
import datetime
import ttk
import os
import time
import threading
import numpy as np

#lkshr = lakeshore335('ASRL3::INSTR')
LARGE_FONT= ("Verdana", 12)

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        
        #plotting boolean to determine whether I'm currently plotting
        self.plotting = False

        #dictionary to identify which instruments to plot
        self.selected_instruments = {'lakeshore': False, 'fluke primary': False, 'fluke secondary': False, 'keithley': False, 'daq': False}
        self.datafiles = {}

        #animation thread
        self.stop_animation_event = threading.Event()


        #Directory Frame
        self.defaultdirectorystr = tk.StringVar()
        self.defaultdirectorystr.set('C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data')

        #defaultdirectoryframe
        self.defaultdirectoryframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.defaultdirectoryframe.grid(row = 0, column = 0, columnspan = '2', sticky = 'new')
        self.defaultdirectoryframe.grid_columnconfigure(1, weight = 1)
        self.defaultdirectorylbl = tk.Label(self.defaultdirectoryframe, text = "Experiment File Directory", font = ("tkDefaultFont", 18))
        self.defaultdirectorylbl.grid(row = 0, column = 0, sticky = 'nw')
        self.defaultdirectoryentry = tk.Label(self.defaultdirectoryframe, textvariable = self.defaultdirectorystr, background = 'white', justify = tk.LEFT)
        self.defaultdirectoryentry.grid(row = 0, column = 1, sticky = 'nsew')
        self.defaultdirectorybtn = ttk.Button(self.defaultdirectoryframe, text = "Set Directory", command = lambda: self.set_directory())
        self.defaultdirectorybtn.grid(row = 0, column = 2, sticky = 'nsew')

        #Button Frame
        self.btnframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.btnframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.btnframe.grid_columnconfigure(0, weight = 1)
        self.openexperimentbtn = ttk.Button(self.btnframe, text = 'Open Experiment', command = lambda: self.openexperiment())
        self.openexperimentbtn.grid(row = 0, column = 0, sticky = 'nsew')
        self.plotbtn = ttk.Button(self.btnframe, text = 'Start Plot', command = lambda: self.plot_click(), state = tk.DISABLED)
        self.plotbtn.grid(row = 1, column = 0, sticky = 'nsew')

        #Plot Frame
        self.plottingframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.plottingframe.grid(row = 1, column = 1, sticky = 'nsew')  
        self.plottingframe.grid_rowconfigure(0, weight = 1)
        self.plottingframe.grid_columnconfigure(0, weight = 1)
        
        self.fig = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, self.plottingframe)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')
        self.plotnum = 0

    def set_directory(self):
        filename = tkFileDialog.askdirectory(initialdir = 'C:\Users\Nate\Dropbox (Minnich Lab)\\', title = 'Select Experiment Directory')
        self.defaultdirectorystr.set(filename)

    def openexperiment(self):
        self.f = tkFileDialog.askdirectory(initialdir = self.defaultdirectorystr.get())
        #need to go down through the directories and get the various plots
        directory_list = os.listdir(self.f)
        self.row_index = 0
        self.column_index = 0

        #go through directoy to configure subplots
        for directory in directory_list:
            if 'lakeshore' in directory:
                self.plotnum = self.plotnum + 3
                self.selected_instruments['lakeshore'] = True
                self.datafiles['lkshr_inputA'] = open('%s\\lakeshore\\inputA.dat' % self.f, 'r')
                self.datafiles['lkshr_inputB'] = open('%s\\lakeshore\\inputB.dat' % self.f, 'r')
                self.datafiles['lkshr_output1Amps'] = open('%s\\lakeshore\\output1Amps.dat' % self.f, 'r')
                self.datafiles['lkshr_output2Amps'] = open('%s\\lakeshore\\output2Amps.dat' % self.f, 'r')
                self.datafiles['lkshr_output1Percent'] = open('%s\\lakeshore\\output1Percent.dat' % self.f, 'r')
                self.datafiles['lkshr_output2Percent'] = open('%s\\lakeshore\\output2Percent.dat' % self.f, 'r')
            if 'fluke' in directory:
                #build plot frame for primary
                self.plotnum = self.plotnum + 1
                self.selected_instruments['fluke primary'] = True
                #open fluke secondary to see if anything is in there
                if os.stat('%s\\fluke8808a\\secondarydisplay.dat' % self.f).st_size > 0 :
                    #then data from secondary exists
                    self.plotnum = self.plotnum + 1
                    self.selected_instruments['fluke secondary'] = True
            if 'daq' in directory:
                self.plotnum = self.plotnum + 4
                self.selected_instruments['daq'] = True
            if 'keithley' in directory:
                self.plotnum = self.plotnum + 3
                self.selected_instruments['keithley'] = True

            #now setup subplots based on instruments and total number of plots
            if self.plotnum == 1:
                self.rows = 1
                self.columns = 1
            elif self.plotnum == 2:
                self.rows = 1
                self.columns = 2
            elif self.plotnum == 3:
                self.rows = 1
                self.columns = 3
            elif self.plotnum == 4:
                self.rows = 2
                self.columns = 2
            elif self.plotnum == 5:
                self.rows = 2
                self.columns = 3
            elif self.plotnum == 6:
                self.rows = 2
                self.columns = 3
            elif self.plotnum == 7:
                self.rows = 2
                self.columns = 4
            elif self.plotnum == 8:
                self.rows = 2
                self.columns = 4
            elif self.plotnum == 9:
                self.rows = 3
                self.columns = 3
            elif self.plotnum == 10:
                self.rows = 3
                self.columns = 4
            elif self.plotnum == 11:
                self.rows = 3
                self.columns = 4
            elif self.plotnum == 12:
                self.rows = 3
                self.columns = 4
            #now setup all the subplots
            self.axes = []
            self.subplot_index = 1
            for k in range(0,self.plotnum):
                self.axes.append(self.fig.add_subplot(self.rows, self.columns, self.subplot_index))
                self.subplot_index = self.subplot_index + 1
            
            
            self.plotcell_index = 0
            self.plotcell_list = []
            if self.selected_instruments['lakeshore']:
                self.plotcell_list.append(plot_cell(self.axes[self.plotcell_index], 2, 'Lakeshore Temperature', 'Temp (K)', [self.datafiles['lkshr_inputA'], self.datafiles['lkshr_inputB']], ['A', 'B']))
                self.plotcell_index = self.plotcell_index + 1
                self.plotcell_list.append(plot_cell(self.axes[self.plotcell_index], 2, 'Lakeshore Output Amps', 'Temp (K)', [self.datafiles['lkshr_output1Amps'], self.datafiles['lkshr_output2Amps']], ['1', '2']))
                self.plotcell_index = self.plotcell_index + 1
                self.plotcell_list.append(plot_cell(self.axes[self.plotcell_index], 2, 'Lakeshore Output Percent', 'Temp (K)', [self.datafiles['lkshr_output1Percent'], self.datafiles['lkshr_output2Percent']], ['1', '2']))
                self.plotcell_index = self.plotcell_index + 1
            self.canvas.draw_idle()
    
        #now that the plots are initialized, I can enable the plot button
        self.plotbtn.config(state = tk.NORMAL)
        
    def plot_click(self):
        if self.plotting: #then pause the plot
            self.stop_animation_event.set()
            self.plotting = False
            self.plotbtn.config(text = 'Start Plot')
        else: #then start plotting
            self.plotting = True
            self.plotbtn.config(text = 'Stop Plot')
            self.start()


    def start(self):
        t = threading.Thread(target = self.animation_target())
        t.start()         

    def animation_target(self):
        #every 30 seconds clear data in ram and plot entire data file
        self.stop_animation_event.clear()
        while  not (self.stop_animation_event.is_set()):
            self.stop_animation_event.wait(10)
            self.update_graph()

    def update_graph(self):
        for k in range(0,self.plotcell_index):
            try: 
                self.plotcell_list[k].read_file()
                self.canvas.draw_idle()
      
            except RuntimeError,e:
                print '%s: %s' % ("Lakeshore",e.message)
                if "dictionary changed size during iteration" in e.message:
                    #disable the start button
                    self.plotbtn.config(state = tk.DISABLED)
                    #stop the graph animation
                    self.plotting = False
                    self.stop_animation_event.set()
                    #wait for animation to finish
                    time.sleep(1.1)
                    #restart thread
                    t = threading.Thread(target = self.animation_target)
                    t.start()
                    print "Animation Thread-%d" % t.ident



class plot_cell():
    def __init__(self, axis, linesperaxis, title, yaxis, datafiles, legendlabels):
        self.axis = axis
        self.axis.set_title(title)
        self.axis.set_ylabel(yaxis)
        self.linesperaxis = linesperaxis
        self.datafiles = datafiles #list of open files not paths
        self.legendlabels = legendlabels
        #initialize lines
        colmap = cm = plt.get_cmap('rainbow') 
        cNorm  = colors.Normalize(vmin=0, vmax=linesperaxis*2)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=colmap)
        self.lines = []
        for k in range(0,self.linesperaxis):
            line, = self.axis.plot([],[], color = scalarMap.to_rgba(k+1), label = self.legendlabels[k] )
            self.lines.append(line)

    def read_file(self):
        for k in range(0, self.linesperaxis):
            #datafile is the file object not the path
            data = {'x': [], 'y': [], 'units': None}
            #read first line
            dataline = self.datafiles[k].readline()
            datalist = dataline.split(',')
            if len(datalist) > 2: #then the instrument is fluke and the third column is the units
                data['units'] = datalist[2]
            #print (datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()
            try:
                data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds())
            except ValueError:
                data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds())
            data['y'].append(float(datalist[1]))
            for line in self.datafiles[k]:
                datalist = line.split(',')
                print datalist[0]
                try:
                    data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds())
                except ValueError:
                    data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds())
                data['y'].append(float(datalist[1]))
            self.lines[k].set_data(data['x'], data['y'])
            self.axis.relim()
            self.axis.autoscale_view()



def main():
    app = GraphTk()
    app.geometry('1750x1000')
    app.mainloop()
    

if __name__ == '__main__':
    main()