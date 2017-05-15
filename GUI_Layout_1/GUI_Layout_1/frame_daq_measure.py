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

class daq_measure_frame(tk.Frame):
    def __init__(self, master, controller, daq9211):
        tk.Frame.__init__(self, master) 
        self.daq9211 = daq9211
        self.test_btn = ttk.Button(self, text = 'Test', command = lambda: self.test())
        self.test_btn.pack()
        self.running = False
        self.ani = None

        btns = tk.Frame(self)
        btns.pack()
        lbl = tk.Label(btns, text="Time Step (s)")
        lbl.pack(side=tk.LEFT)

        self.interval = tk.Entry(btns, width=5)
        self.interval.insert(0, '1')
        self.interval.pack(side=tk.LEFT)
        self.btn = tk.Button(btns, text='Start', command= lambda: self.on_click())
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
            self.axs[i].legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
            self.axs[i].set_title('Channel %d' % i)

        #self.ax0 = self.fig.add_subplot(2,2,1)
        #self.line0, = self.ax0.plot([], [], lw=2, label = 'A', color = 'b') #I have to address each plot individually. I can't put plots in a list
        #self.ax0.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        #self.ax0.set_title('Channel 0')
        
        #self.ax1 = self.fig.add_subplot(2,2,2)
        #self.line1, = self.ax1.plot([], [], lw=2, label = 'A', color = 'b') 
        #self.ax1.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        #self.ax1.set_title('Channel 1')
        
        #self.ax2 = self.fig.add_subplot(2,2,3)
        #self.line2, = self.ax2.plot([], [], lw=2, label = 'A', color = 'b') 
        #self.ax2.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        #self.ax2.set_title('Channel 2')
        
        #self.ax3 = self.fig.add_subplot(2,2,4)
        #self.line3, = self.ax3.plot([], [], lw=2, label = 'A', color = 'b') 
        #self.ax3.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        #self.ax3.set_title('Channel 3')
 

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
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            self.run_tasksetup()
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani.event_source.stop()
            self.daq9211.stop_event.set()
            self.btn.config(text='Start')
        else:
            self.btn.config(text='Stop')
            return self.start()
        self.running = not self.running

    def start(self):
        self.daq9211.measureAll(int(self.interval.get()))
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = int(self.interval.get())*1000 + 1, repeat=False)
        self.running = True
        self.btn.config(text='Stop')
        self.ani._start()

    #def update_graph(self,i):
    #    #plot by channel ID
    #    self.namelist = self.daq9211.channels.keys()
    #    print self.namelist
    #    for k in range(0,len(self.namelist)):
    #        xlist = []
    #        ylist = []
    #        ID = self.daq9211.channels[self.namelist[k]].ID
    #        if ID == 0:
    #            for elem in self.daq9211.data[self.namelist[k]]:
    #                xlist.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
    #                ylist.append(elem['data'])
    #            if xlist and ylist:
    #                self.line0.set_data(xlist,ylist) #something wrong here
    #                self.ax0.set_ylim(min(ylist), max(ylist))
    #                self.ax0.set_xlim(min(xlist), max(xlist))
    #        #elif ID == 1:

    #        #elif ID == 2:

    #        #elif ID == 3:

    #        else:
    #            return None

    def update_graph(self,i):
        #plot by channel ID
        self.namelist = self.daq9211.channels.keys()
        for k in range(0,len(self.namelist)):
            xlist = []
            ylist = []
            ID = self.daq9211.channels[self.namelist[k]].ID
            for elem in self.daq9211.data[self.namelist[k]]:
                xlist.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
                ylist.append(elem['data'])
            self.lines[ID].set_data(xlist,ylist)
            if xlist and ylist:
                self.axs[ID].set_ylim(min(ylist), max(ylist))
                self.axs[ID].set_xlim(min(xlist), max(xlist))

    def run_tasksetup(self):
        namelist = self.daq9211.channels.keys()
        for i in range(0,len(namelist)):
            self.daq9211.channels[namelist[i]].setup_task() #setup task in each channel
            self.daq9211.data[namelist[i]] = [] #initialize data dictionary
