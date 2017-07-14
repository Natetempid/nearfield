from PyDAQmx import *
from daq9211 import *

import Tkinter as tk
import tkFileDialog
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import Queue as q

class daq_measure_frame(tk.Frame):
    def __init__(self, master, controller, daq9211):
        tk.Frame.__init__(self, master) 
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.daq9211 = daq9211
        #self.test_btn = ttk.Button(self, text = 'Test', command = lambda: self.test())
        #self.test_btn.pack()
        self.measurement_running = False
        self.plot_running = False
        self.tasksetup_run = False

        self.callback = None

        #data queues
        self.channeltime_list = [np.array([]), np.array([]), np.array([]), np.array([])]
        self.channeldata_list = [np.array([]), np.array([]), np.array([]), np.array([])] #4 channels each appending data to an np.ndarray

        #Header frame that includes all controls
        self.headerframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.headerframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.headerframe.grid_rowconfigure(0,weight = 1)
        self.headerframe.grid_columnconfigure(3,weight=1)
        self.headerframe.grid_columnconfigure(4,weight=1)
        self.headerframe.grid_columnconfigure(5,weight=1)
        #canvas for indicator
        self.indicator_canvas = tk.Canvas(self.headerframe, width = 50, height = 50)
        self.indicator_canvas.grid(row = 0, column = 0, sticky = 'ns')
        self.indicator = self.indicator_canvas.create_oval(5,5,40,40, fill = 'red4')
        self.indicatorstr = tk.StringVar()
        self.indicatorstr.set('DAQ not measuring')
        self.indicatorlbl = tk.Label(self.headerframe, textvariable = self.indicatorstr, font = ('tkDefaultFont', 12))
        self.indicatorlbl.grid(row = 0, column = 1, sticky = 'nsew')
        #Time interval
        self.intervalframe = tk.Frame(self.headerframe,borderwidth = 5)
        self.intervalframe.grid(row = 0, column = 2, sticky = 'nsew')
        self.intervalframe.grid_rowconfigure(0,weight = 1)
        self.intervalframe.grid_columnconfigure(0, weight = 1)
        self.interval_lbl = tk.Label(self.intervalframe, text = 'Measurement Time Step (s)')
        self.interval_lbl.grid(row = 0, column = 0)
        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(self.intervalframe, textvariable = self.intervalstr, width=5)
        self.interval.grid(row = 1, column = 0, sticky = 'nsew')
        #Measure Button
        self.measure_btn = ttk.Button(self.headerframe, text = 'Start Measurement', command = lambda:self.measure_click())
        self.measure_btn.grid(row = 0, column = 3, sticky = 'nsew')
        #Plot Button
        self.measure_and_plot_btn = ttk.Button(self.headerframe, text = 'Start Measurement & Plot', command = lambda: self.measure_and_plot_click())
        self.measure_and_plot_btn.grid(row = 0, column = 4, sticky = 'nsew')
        #Reset Plot Button
        self.resetbtn = ttk.Button(self.headerframe, text = 'Reset Graphs', command = lambda: self.reset_graphs())
        self.resetbtn.grid(row = 0, column = 5, sticky = 'nsew')


        #Plotting
        self.fig = plt.Figure(figsize=(5,5))

        #make plots depend on number of configured channels of the daq9211
        self.axs = []
        self.lines = []
        
        for i in range(0,4):
            self.axs.append(self.fig.add_subplot(2,2,i+1))
            line, = self.axs[i].plot([], [], lw=2, label = 'A', color = 'b')
            self.lines.append(line)
            #self.axs[i].legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
            self.axs[i].set_title('Channel %d' % i)
 

        self.canvas = FigureCanvasTkAgg(self.fig,self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 1, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    #Click Methods
    def measure_click(self):
        if self.measurement_running: #then user wants to stop the Measurement
            self.stop_instrument()
            self.stop_graph() #stopping the measurement also stops the graph
        else: #then user wants to start the measurement without running the graph
            self.start_instrument()

    def measure_and_plot_click(self):
        if self.measurement_running and not self.plot_running: #then user has started measuring and wants to graph
            self.start_graph()
        elif self.measurement_running and self.plot_running: #then user wants to stop the graph but keep the measurement going
            self.stop_graph()
        elif not self.measurement_running and not self.plot_running: #then user wants to start the measurement and start the graph
            self.start_instrument()
            self.start_graph()
        #note the user cannot stop the measurement from the measure_and_plot button. To stop the Measurement, the user must click the measure_btn

    def start_instrument(self):
        if not self.tasksetup_run: #then I need to setup the daq channel tasks
            self.run_tasksetup()
            self.tasksetup_run = True
        self.daq9211.measureAll(float(self.intervalstr.get()))
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "green2")    
        self.indicatorstr.set('DAQ measuring...')
        #change measurement button
        self.measure_btn.config(text = 'Stop Measurement & Plot')
        #change measurement running state
        self.measurement_running = True

    def stop_instrument(self):
        self.daq9211.stop_event.set()
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "red4")    
        self.indicatorstr.set('DAQ not measuring')
        #change measurement button
        self.measure_btn.config(text = 'Start Measurement')
        while self.daq9211.thread_active:
            time.sleep(0.002) #wait for the measurement to stop
        #clear the measurement queue
        self.daq9211.clear_queues()
        #change measurement running state
        self.measurement_running = False

    def start_graph(self):
        #change plot running state
        self.plot_running = True
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Stop Plot')
        #disable reset button
        self.resetbtn.config(state = tk.DISABLED)
        #update the graph
        self.update_graph()

    def stop_graph(self):
        #change plot running state
        self.plot_running = False
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Start Measurement & Plot')
        #enable reset button
        self.resetbtn.config(state = tk.NORMAL)
        #print self.callback
        if self.callback is not None:
            self.after_cancel(self.callback)
    
    def reset_graphs(self):
        self.channeltime_list = [np.array([]), np.array([]), np.array([]), np.array([])]
        self.channeldata_list = [np.array([]), np.array([]), np.array([]), np.array([])]
        for k in range(0,4):
            self.lines[k].set_data(self.channeltime_list[k], self.channeldata_list[k])
        self.canvas.draw_idle()
            
    def update_graph(self):#,i):\
        #try:
        def totalseconds(x):
            return (x - datetime.datetime(1970,1,1)).total_seconds()
        totalseconds = np.vectorize(totalseconds)
        #plot by channel ID
        for k in range(0,len(self.daq9211.channels)):
            ID = self.daq9211.channels[k].ID #data in channel # ID is plotted on the graph # ID
            while (not self.daq9211.channels[k].dataq.empty()):
                data = self.daq9211.channels[k].dataq.get()
                time_val = data[0]
                val = data[1]
                self.channeltime_list[k] = np.append(self.channeltime_list[k], time_val)
                self.channeldata_list[k] = np.append(self.channeldata_list[k], val)
                self.lines[ID].set_data(totalseconds(self.channeltime_list[k]), self.channeldata_list[k])
            self.axs[ID].relim()
            self.axs[ID].autoscale_view()
            self.canvas.draw_idle()
        self.callback = self.after(100, self.update_graph)
    
    def run_tasksetup(self):
        for i in range(0,len(self.daq9211.channels)):
            self.daq9211.channels[i].setup_task() #setup task in each channel
            #self.daq9211.data[i]] = [] #initialize data dictionary
