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
import ttk
import Queue as q

class daq_measure_frame(tk.Frame):
    def __init__(self, master, controller, daq9211):
        tk.Frame.__init__(self, master) 
        self.daq9211 = daq9211
        #self.test_btn = ttk.Button(self, text = 'Test', command = lambda: self.test())
        #self.test_btn.pack()
        self.running = False
        self.ani = None
        self.stopgraph_event = threading.Event()
        self.stopgraph_event.set()

        #data queues
        self.channeltime_list = [np.array([]), np.array([]), np.array([]), np.array([])]
        self.channeldata_list = [np.array([]), np.array([]), np.array([]), np.array([])] #4 channels each appending data to an np.ndarray

        btns = tk.Frame(self)
        btns.pack()
        lbl = tk.Label(btns, text="Time Step (s)")
        lbl.pack(side=tk.LEFT)
        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(btns, textvariable = self.intervalstr, width=5)
        self.interval.pack(side=tk.LEFT)
        self.btn = ttk.Button(btns, text='Start', command= lambda: self.on_click())
        self.btn.pack(side=tk.LEFT)

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
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def test(self):
        self.namelist = self.daq9211.channels.keys()
        print self.namelist
        print self.daq9211.channels[self.namelist[0]].ID
        self.daq9211.channels[self.namelist[0]].setup_task()

        

    def on_click(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.run_tasksetup
            self.run_tasksetup()
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani = False
            self.daq9211.stop_event.set()
            self.stopgraph_event.set()
            self.btn.config(text='Start')
        else:
            self.btn.config(text='Stop')
            return self.start()
        self.running = not self.running

    def start(self):
        self.daq9211.measureAll(float(self.intervalstr.get()))
        t = threading.Thread(target = self.animation_target)
        t.start()
        #self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = float(self.interval.get())*1000 + 1, repeat=False)
        self.ani = True
        self.running = True

        self.btn.config(text='Stop')
        #self.anithread = threading.Thread(target = self.ani._start())
        #self.ani._start()
    
    def update_graph(self):#,i):
        def totalseconds(x):
            return (x - datetime.datetime(1970,1,1)).total_seconds()
        totalseconds = np.vectorize(totalseconds)
        #plot by channel ID
        for k in range(0,len(self.daq9211.channels)):
            ID = self.daq9211.channels[k].ID #data in channel # ID is plotted on the graph # ID
            while (not self.daq9211.channels[k].dataq.empty()):
                data = self.daq9211.channels[k].dataq.get()
                time = data[0]
                val = data[1]
                self.channeltime_list[k] = np.append(self.channeltime_list[k], time)
                self.channeldata_list[k] = np.append(self.channeldata_list[k], val)
                self.lines[ID].set_data(totalseconds(self.channeltime_list[k]), self.channeldata_list[k])
            self.axs[ID].relim()
            self.axs[ID].autoscale_view()
            self.canvas.draw_idle()
    
    def animation_target(self):
        self.stopgraph_event.clear()
        while(not self.stopgraph_event.is_set()):
            #time.sleep(float(self.intervalstr.get()))
            self.stopgraph_event.wait(0.5)
            self.update_graph()
        #self.stopgraph_event.set() #once animation stops, reset the stop event to trigger again

    def run_tasksetup(self):
        for i in range(0,len(self.daq9211.channels)):
            self.daq9211.channels[i].setup_task() #setup task in each channel
            #self.daq9211.data[i]] = [] #initialize data dictionary
