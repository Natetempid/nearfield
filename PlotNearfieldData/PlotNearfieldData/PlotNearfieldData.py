
import Tkinter as tk
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
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
        self.datafiles = {}
        self.data = {}
        self.data_instances = []
        #callback
        self.callback = None
        
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
        self.plottingintervallbl = tk.Label(self.btnframe, text = 'Plot Interval (s)')
        self.plottingintervallbl.grid(row = 2, column = 0)
        self.plottingintervalstr = tk.StringVar()
        self.plottingintervalstr.set('30')
        self.plottingintervalentry = tk.Entry(self.btnframe, textvariable = self.plottingintervalstr)
        self.plottingintervalentry.grid(row = 3, column = 0)

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
        #print directory_list
        self.row_index = 0
        self.column_index = 0
        for directory in directory_list:
            if 'lakeshore' in directory:
                #build three plotframes for temperature, heaterooutput in Amps and heateroutput in Percent
                
                #Temperature Plot
                self.lkshr_temperature_plotframe = plotframe(self.plottingframe, 'Lakeshore Temperature', 'Temp (K)', 2)
                [self.row_index, self.column_index] = self.lkshr_temperature_plotframe.newgrid(self.row_index, self.column_index)
                    #Setup data_instance
                self.data_instances.append(data_instance(2,self.lkshr_temperature_plotframe,['%s\\lakeshore\\inputA.dat' % self.f, '%s\\lakeshore\\inputB.dat' % self.f]))

                #Output Amps
                self.lkshr_outputamps_plotframe =  plotframe(self.plottingframe, 'Lakeshore Output Amps', 'Amps', 2)
                [self.row_index, self.column_index] = self.lkshr_outputamps_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(2,self.lkshr_outputamps_plotframe, ['%s\\lakeshore\\output1Amps.dat' % self.f, '%s\\lakeshore\\output2Amps.dat' % self.f]))

                #Output Percent
                self.lkshr_outputpercent_plotframe =  plotframe(self.plottingframe, 'Lakeshore Output Percent', 'Amps', 2)
                [self.row_index, self.column_index] = self.lkshr_outputpercent_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(2,self.lkshr_outputpercent_plotframe, ['%s\\lakeshore\\output1Percent.dat' % self.f, '%s\\lakeshore\\output2Percent.dat' % self.f]))
                self.selected_instruments['lakeshore'] = True
                

            if 'fluke' in directory:
                #Primary
                self.fluke_primary_plotframe = plotframe(self.plottingframe, 'Fluke Primary', '', 1)
                [self.row_index, self.column_index] = self.fluke_primary_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(1,self.fluke_primary_plotframe, ['%s\\fluke8808a\\primarydisplay.dat' % self.f]))

                self.selected_instruments['fluke primary'] = True
                
                
                #Check fluke secondary if anything is in there
                if os.stat('%s\\fluke8808a\\secondarydisplay.dat' % self.f).st_size > 0 :
                    #then data from secondary exists
                    self.fluke_secondary_plotframe = plotframe(self.plottingframe, 'Fluke Secondary', '', 1)
                    [self.row_index, self.column_index] = self.fluke_secondary_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                    self.data_instances.append(data_instance(1,self.fluke_secondary_plotframe, ['%s\\fluke8808a\\secondarydisplay.dat' % self.f]))

                    self.selected_instruments['fluke secondary'] = True

            if 'daq' in directory:
                self.daq_plotframe_list =  []
                for k in range(0,4):
                    self.daq_plotframe_list.append(plotframe(self.plottingframe, 'DAQ Channel %d' % k, '', 1))
                    [self.row_index, self.column_index] = self.daq_plotframe_list[k].newgrid(self.row_index, self.column_index)
                    #data instance
                    self.data_instances.append(data_instance(1, self.daq_plotframe_list[k], ['%s\\daq9211\\channel%d.dat' % (self.f, k)]))
                self.selected_instruments['daq'] = True

            if 'keithley' in directory:
                #Applied Biase
                self.keithley_appliedbias_plotframe = plotframe(self.plottingframe, 'Keithley Applied Bias', '', 1)
                [self.row_index, self.column_index] = self.keithley_appliedbias_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(1,self.keithley_appliedbias_plotframe, ['%s\\keithley\\appliedbias.dat' % self.f]))

                #Measured Current
                self.keithley_measuredcurrent_plotframe = plotframe(self.plottingframe, 'Keithley Measured Current', 'Amps', 1)
                [self.row_index, self.column_index] = self.keithley_measuredcurrent_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(1,self.keithley_measuredcurrent_plotframe, ['%s\\keithley\\measuredcurrent.dat' % self.f]))

                #Measured Resistance
                self.keithley_measuredresistance_plotframe = plotframe(self.plottingframe, 'Keithley Measured Resistance', 'Ohms', 1)
                [self.row_index, self.column_index] = self.keithley_measuredresistance_plotframe.newgrid(self.row_index, self.column_index)
                    #data instance
                self.data_instances.append(data_instance(1,self.keithley_measuredresistance_plotframe, ['%s\\keithley\\measuredresistance.dat' % self.f]))

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
            self.stop_plot()
        else: #then start plotting
            self.start_plot()
    
    def stop_plot(self):
        self.plotting = False
        self.plotbtn.config(text = 'Start Plot')
        if self.callback is not None:
            self.after_cancel(self.callback)

    def start_plot(self):
        self.plotting = True
        self.plotbtn.config(text = 'Stop Plot')
        self.update_graph()
 

    def update_graph(self):
        t1 = datetime.datetime.now()
        print t1
        #update all plot frames
        for k in range(len(self.data_instances)):
            self.data_instances[k].update_plotframe()
        #draw_idle all at once
        for k in range(len(self.data_instances)):
            self.data_instances[k].draw_idle()
        t2 = datetime.datetime.now()
        print t2
        delta_t = (t2 - t1).total_seconds()
        if delta_t < float(self.plottingintervalstr.get()):
            self.callback = self.after(1000*int(float(self.plottingintervalstr.get()) - delta_t),self.update_graph)
        else:
            self.callback = self.after(100,self.update_graph)

   
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
        colmap = cm = plt.get_cmap('rainbow') 
        cNorm  = colors.Normalize(vmin=0, vmax=numberoflines)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=colmap)
        for k in range(0,numberoflines):
            line, = self.ax.plot([],[], color = scalarMap.to_rgba(k))
            self.lines.append(line)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

        #self.navigator_frame = tk.Frame(self)
        #self.navigator_frame.grid(row = 1, column = 0, sticky = 'nsew')
        #self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.navigator_frame)

    def newgrid(self, row_index, column_index):
        self.grid(row = row_index, column = column_index, sticky = 'nsew')
        #time.sleep(0.25)
        #print row_index, column_index
        if row_index > 2:
            return [0, column_index + 1]
        else:
            return [row_index+1, column_index]

class data_instance():
    def __init__(self, linesperaxis, plotframe, filepaths):
        self.linesperaxis = linesperaxis
        self.plotframe = plotframe
        #the files input is a list of file paths
        self.filepaths = filepaths
        self.files = {} 
        self.x = {}
        self.y = {}
        self.units = {}
        self.file_startindices = {}
        self.__initAll()
        

    def __initAll(self):
        for k in range(self.linesperaxis):
            self.files['%d' % k] = open(self.filepaths[k], 'r')
            self.x['%d' % k] = []
            self.y['%d' % k] = []
            self.units['%d' % k] = None
            self.file_startindices['%d' % k] = 0

    def __reopenfiles(self):
        for k in range(self.linesperaxis):
            self.files['%d' % k].close()
            self.files['%d' % k] = open(self.filepaths[k], 'r')

    def __read_file(self, file_num):
        datafile = self.files['%d' % file_num]
        #datafile is the file object not the path
        data = {'x': [], 'y': [], 'units': None}
        #seek to the start_index
        start_index = self.file_startindices['%d' % file_num]
        for k in range(start_index):
            datafile.readline()
        #read first line
        dataline = datafile.readline()
        datalist = dataline.split(',')
        if len(datalist) > 2: #then the instrument is fluke and the third column is the units
            data['units'] = datalist[2]
        #print (datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()
        try:
            data['x'].append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()))
            data['y'].append(float(datalist[1]))
        except ValueError:
            try:
                data['x'].append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds()))
                data['y'].append(float(datalist[1]))
            except ValueError:
                pass
        
        while True:
            line =  datafile.readline()
            if not line: 
                break
            datalist = line.split(',')
            try:
                data['x'].append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime(1970,1,1)).total_seconds()))
                data['y'].append(float(datalist[1]))
            except ValueError:
                try:
                    data['x'].append(float((datetime.datetime.strptime(datalist[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime(1970,1,1)).total_seconds()))
                    data['y'].append(float(datalist[1]))
                except ValueError:
                    pass
        return data
   
    def set_data(self,data_dictionary, file_num):
        #x and y are dictionarys with keys '1', '2', ... to lines per axis
        #data_dictionary is dictionary with keys 'x' and 'y' ' data'
        self.x['%d' % file_num] = self.x['%d' % file_num] + data_dictionary['x']
        self.y['%d' % file_num] = self.y['%d' % file_num] + data_dictionary['y']
        self.units['%d' % file_num] = data_dictionary['units']

    def __set_file_startindices(self):
        #the file_startindex for each file is the length of that corresponding x list
        for k in range(self.linesperaxis):
            startindex = len(self.x['%d' % k])
            self.file_startindices['%d' % k] = startindex

    def __read_all_data(self):
        #close and reopen files
        self.__reopenfiles()
        #update file indicices
        self.__set_file_startindices()
        for k in range(self.linesperaxis):            
            data = self.__read_file(k)
            self.set_data(data, k)

    def update_plotframe(self):
        self.__read_all_data()
        for k in range(self.linesperaxis):
            self.plotframe.lines[k].set_data(self.x['%d' % k], self.y['%d' % k])
        #rescale and redraw
        self.plotframe.ax.relim()
        self.plotframe.ax.autoscale_view()
        
    def draw_idle(self):
        self.plotframe.canvas.draw_idle()


def main():
    app = GraphTk()
    app.geometry('1750x1000')
    app.mainloop()
    

if __name__ == '__main__':
    main()
