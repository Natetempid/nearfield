

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

    def set_directory(self):
        filename = tkFileDialog.askdirectory(initialdir = 'C:\Users\Nate\Dropbox (Minnich Lab)\\', title = 'Select Experiment Directory')
        self.defaultdirectorystr.set(filename)

    def openexperiment(self):
        self.f = tkFileDialog.askdirectory(initialdir = self.defaultdirectorystr.get())
        #need to go down through the directories and get the various plots
        directory_list = os.listdir(self.f)
        print directory_list
        self.row_index = 0
        self.column_index = 0
        for directory in directory_list:
            if 'lakeshore' in directory:
                #build three plotframes for temperature, heaterooutput in Amps and heateroutput in Percent
                self.lkshr_temperature_plotframe = plotframe(self.plottingframe, 'Lakeshore Temperature', 'Temp (K)', 2)
                [self.row_index, self.column_index] = self.lkshr_temperature_plotframe.newgrid(self.row_index, self.column_index)
                self.lkshr_outputamps_plotframe =  plotframe(self.plottingframe, 'Lakeshore Output Amps', 'Amps', 2)
                [self.row_index, self.column_index] = self.lkshr_outputamps_plotframe.newgrid(self.row_index, self.column_index)
                self.lkshr_outputpercent_plotframe =  plotframe(self.plottingframe, 'Lakeshore Output Percent', 'Amps', 2)
                [self.row_index, self.column_index] = self.lkshr_outputpercent_plotframe.newgrid(self.row_index, self.column_index)
                self.selected_instruments['lakeshore'] = True
            if 'fluke' in directory:
                #build plot frame for primary
                self.fluke_primary_plotframe = plotframe(self.plottingframe, 'Fluke Primary', '', 1)
                [self.row_index, self.column_index] = self.fluke_primary_plotframe.newgrid(self.row_index, self.column_index)
                #open fluke secondary to see if anything is in there
                if os.stat('%s\\fluke8808a\\secondarydisplay.dat' % self.f).st_size > 0 :
                    #then data from secondary exists
                    self.fluke_secondary_plotframe = plotframe(self.plottingframe, 'Fluke Secondary', '', 1)
                    [self.row_index, self.column_index] = self.fluke_secondary_plotframe.newgrid(self.row_index, self.column_index)
                    self.selected_instruments['fluke secondary'] = True
                self.selected_instruments['fluke primary'] = True
            if 'daq' in directory:
                self.daq_plotframe_list =  []
                for k in range(0,4):
                    self.daq_plotframe_list.append(plotframe(self.plottingframe, 'DAQ Channel %d' % k, '', 1))
                    [self.row_index, self.column_index] = self.daq_plotframe_list[k].newgrid(self.row_index, self.column_index)
                self.selected_instruments['daq'] = True
            if 'keithley' in directory:
                self.keithley_appliedbias_plotframe = plotframe(self.plottingframe, 'Keithley Applied Bias', '', 1)
                [self.row_index, self.column_index] = self.keithley_appliedbias_plotframe.newgrid(self.row_index, self.column_index)
                self.keithley_measuredcurrent_plotframe = plotframe(self.plottingframe, 'Keithley Measured Current', 'Amps', 1)
                [self.row_index, self.column_index] = self.keithley_measuredcurrent_plotframe.newgrid(self.row_index, self.column_index)
                self.keithley_measuredresistance_plotframe = plotframe(self.plottingframe, 'Keithley Measured Resistance', 'Ohms', 1)
                [self.row_index, self.column_index] = self.keithley_measuredresistance_plotframe.newgrid(self.row_index, self.column_index)
                self.selected_instruments['keithley'] = True

        #setup grid configuration to change cell weights
        if self.column_index > 0: #then the maximum # of rows has been achieved and cells in next column have been filled
            if self.row_index == 0: #then the last column has been filled and the column index has increased by one
                for k in range(0,4):
                    self.plottingframe.grid_rowconfigure(k,weight=1)
                for k in range(0,self.column_index):
                    self.plottingframe.grid_columnconfigure(k,weight=1)
            else: #then the final column isn't full and the column index has not been increased
                for k in range(0,4):
                    self.plottingframe.grid_rowconfigure(k,weight=1)
                for k in range(0,self.column_index+1):
                    self.plottingframe.grid_columnconfigure(k,weight=1)
        else: #then there is only one column
            print self.row_index, self.column_index
            for k in range(0,self.row_index):
                self.plottingframe.grid_rowconfigure(k,weight=1)
            for k in range(0,self.column_index+1):
                self.plottingframe.grid_columnconfigure(k,weight=1)
    
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
        try:
            if self.selected_instruments['lakeshore']:
                #Input A
                file = open('%s\\lakeshore\\inputA.dat' % self.f)
                data = self.read_file(file)
                self.lkshr_temperature_plotframe.lines[0].set_data(data['x'], data['y'])
                #Input B
                file = open('%s\\lakeshore\\inputB.dat' % self.f)
                data = self.read_file(file)
                self.lkshr_temperature_plotframe.lines[1].set_data(data['x'], data['y'])
                print self.lkshr_temperature_plotframe.lines[1].get_data()
                self.lkshr_temperature_plotframe.ax.relim()
                self.lkshr_temperature_plotframe.ax.autoscale_view()
                self.lkshr_temperature_plotframe.canvas.draw_idle()
      
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

    #def totalseconds(self, x):
    #        return (x - datetime.datetime(1970,1,1)).total_seconds()
            

    def read_file(self, datafile):
        #datafile is the file object not the path
        data = {'x': [], 'y': [], 'units': None}
        #read first line
        dataline = datafile.readline()
        datalist = dataline.split(',')
        if len(datalist) > 2: #then the instrument is fluke and the third column is the units
            data['units'] = datalist[2]
        #print (datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()
        try:
            data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds())
        except ValueError:
            data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds())
        data['y'].append(float(datalist[1]))
        for line in datafile:
            datalist = line.split(',')
            try:
                data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds())
            except ValueError:
                data['x'].append((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds())
            data['y'].append(float(datalist[1]))
        return data


class plotframe(tk.Frame):
    def __init__(self, master,title,yaxis, numberoflines):
        tk.Frame.__init__(self,master)
        self.config(borderwidth = 2)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_title('%s' % title)
        self.lines = []
        for k in range(0,numberoflines):
            line, = self.ax.plot([],[])
            self.lines.append(line)        
        colmap = cm = plt.get_cmap('hsv') 
        cNorm  = colors.Normalize(vmin=0, vmax=numberoflines)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=colmap)
        for k in range(1,numberoflines+1):
            self.lines.append(self.ax.plot([],[], color = scalarMap.to_rgba(k)))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

    def newgrid(self, row_index, column_index):
        self.grid(row = row_index, column = column_index, sticky = 'nsew')
        #time.sleep(0.25)
        #print row_index, column_index
        if row_index > 2:
            return [0, column_index + 1]
        else:
            return [row_index+1, column_index]


def main():
    app = GraphTk()
    app.geometry('1750x1000')
    app.mainloop()
    

if __name__ == '__main__':
    main()