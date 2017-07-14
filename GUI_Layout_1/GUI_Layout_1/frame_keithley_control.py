import Tkinter as tk
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import threading
from frame_fluke8808a_control import fluke8808a_control_frame
import Queue as q
import numpy as np

class keithley_control_frame(tk.Frame):
    def __init__(self,master,controller, keithley, fluke8808a):
        tk.Frame.__init__(self,master)       
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        #self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(1,weight=1)

        self.master = master
        self.controller = controller
        self.keithley = keithley
        self.fluke8808a = fluke8808a
        
        self.running = False
        self.ani = None
        self.stopgraph_event = threading.Event()

        self.keithleyraised = True

        self.keithley_callback = None
        self.fluke_callback = None

        #setup frame with 2 vertical cells, each with 2 subcells
        #left frame
        self.leftframe = tk.Frame(self)
        self.leftframe.grid_rowconfigure(1,weight = 1)
        self.leftframe.grid_columnconfigure(0,weight = 1)
        self.leftframe.grid(row = 0, column = 0,sticky='nsew')
        self.controlframe = tk.Frame(self.leftframe, borderwidth=5, relief=tk.GROOVE)
        self.controlframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.controlframe.grid_columnconfigure(0,weight=1)
        self.controlframe.grid_columnconfigure(1,weight=1)
        self.controlframe.grid_columnconfigure(2,weight=1)
        self.controlframe.grid_columnconfigure(3,weight=1)
        self.voltageframe = tk.Frame(self.leftframe, borderwidth = 5, relief = tk.GROOVE)
        self.voltageframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.voltageframe.grid_rowconfigure(0,weight=1)
        self.voltageframe.grid_columnconfigure(0,weight=1)
        #right frame
        self.rightframe = tk.Frame(self)
        self.rightframe.grid_rowconfigure(2,weight=1)
        self.rightframe.grid_rowconfigure(1,weight=1)
        self.rightframe.grid_columnconfigure(0,weight=1)
        self.rightframe.grid(row=0,column=1,sticky='nsew')

        #indicate if user wants to see fluke measurements or keithley measurements
        self.rightbtnframe = tk.Frame(self.rightframe)
        self.rightbtnframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.rightbtnframe.grid_columnconfigure(0, weight = 1)
        self.rightbtnframe.grid_columnconfigure(1, weight = 1)
        self.currentframe = tk.Frame(self.rightframe, borderwidth = 5, relief = tk.GROOVE)
        self.currentframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.currentframe.grid_rowconfigure(0,weight=1)
        self.currentframe.grid_columnconfigure(0,weight=1)
        self.resistanceframe = tk.Frame(self.rightframe, borderwidth = 5, relief = tk.GROOVE)
        self.resistanceframe.grid(row = 2, column = 0, sticky = 'nsew')
        self.resistanceframe.grid_rowconfigure(0,weight=1)
        self.resistanceframe.grid_columnconfigure(0,weight=1)

        #Voltage Control
        self.voltagestartlbl = tk.Label(self.controlframe,text = "Volt. Ramp Start (V)", font = ("tkDefaultFont",18))
        self.voltagestartlbl.grid(row = 0, column = 0, sticky = 'nsw')
        self.voltagestartstr = tk.StringVar()
        self.voltagestartstr.set('0')
        self.voltagestartentry = tk.Entry(self.controlframe, textvariable = self.voltagestartstr)
        self.voltagestartentry.grid(row = 1, column = 0, sticky = 'nsw')

        self.voltageendlbl = tk.Label(self.controlframe,text = "Volt. Ramp End (V)", font = ("tkDefaultFont",18))
        self.voltageendlbl.grid(row = 0, column = 1, sticky = 'nsw')
        self.voltageendstr = tk.StringVar()
        self.voltageendstr.set('0')
        self.voltageendentry = tk.Entry(self.controlframe, textvariable = self.voltageendstr)
        self.voltageendentry.grid(row = 1, column = 1, sticky = 'nsw')

        self.rampratelbl = tk.Label(self.controlframe, text =  "Ramp Rate (V/s)", font = ("tkDefaultFont",18))
        self.rampratelbl.grid(row = 0, column = 2, sticky = 'nsw')
        self.rampratestr = tk.StringVar()
        self.rampratestr.set('1')
        self.ramprateentry = tk.Entry(self.controlframe, textvariable = self.rampratestr)
        self.ramprateentry.grid(row = 1, column = 2, sticky = 'nsw')

        self.voltagesteplbl = tk.Label(self.controlframe, text =  "Ramp Step Size (V)", font = ("tkDefaultFont",18))
        self.voltagesteplbl.grid(row = 0, column = 3, sticky = 'nsw')
        self.voltagestepstr = tk.StringVar()
        self.voltagestepstr.set('1')
        self.voltagestepentry = tk.Entry(self.controlframe, textvariable = self.voltagestepstr)
        self.voltagestepentry.grid(row = 1, column = 3, sticky = 'nsw')

        self.rampupbtn = tk.Button(self.controlframe, text = "Ramp Up", font = ("tkDefaultFont",14), background = "green4", command = lambda: self.rampup())
        self.rampupbtn.grid(row = 2, column = 0, sticky = 'nsew', padx = 5, pady = 5)
        self.rampdownbtn = tk.Button(self.controlframe, text = "Ramp Down", font = ("tkDefaultFont",14), foreground = "white", background = "blue", command = lambda: self.rampdown())
        self.rampdownbtn.grid(row = 2, column = 1, sticky = 'nsew', padx = 5, pady = 5)
        self.disablebtn = tk.Button(self.controlframe, text = "Turn Off/Reset Graphs", font = ("tkDefaultFont",14), command = lambda: self.turnoff())
        self.disablebtn.grid(row = 2, column = 2, sticky = 'nsew', padx = 5, pady = 5)
        self.abortbtn = tk.Button(self.controlframe, text = "Abort Ramp", font = ("tkDefaultFont",14), foreground = "white", background = "red", command = lambda: self.abortramp())
        self.abortbtn.grid(row = 2, column = 3, sticky = 'nsew', padx = 5, pady = 5)

        #fluke or keithley buttons
        self.keithleybtn = ttk.Button(self.rightbtnframe, text = "Keithley Measurements", command = lambda: self.showkeithley())
        self.keithleybtn.grid(row = 0, column = 0, sticky = 'nsew')
        self.flukebtn = ttk.Button(self.rightbtnframe, text = "Fluke Measurements", command = lambda: self.showfluke())
        self.flukebtn.grid(row = 0, column = 1, sticky = 'nsew')

        #graphs
        #Voltage
        self.fig1 = plt.Figure(figsize=(5,5))
        self.ax1 = self.fig1.add_subplot(1,1,1)
        self.ax1.set_title('Applied Bias')
        self.line1, = self.ax1.plot([], [], color='r')
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.voltageframe)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas1._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')
        #Current
        self.fig2 = plt.Figure(figsize=(5,5))
        self.ax2 = self.fig2.add_subplot(1,1,1)
        self.ax2.set_title('Measured Current')
        self.line2, = self.ax2.plot([], [], color='r')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.currentframe)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas2._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')
        #Resistance
        self.fig3 = plt.Figure(figsize=(5,5))
        self.ax3 = self.fig3.add_subplot(1,1,1)
        self.ax3.set_title('Measured Resistance')
        self.line3, = self.ax3.plot([], [], color='r')
        self.canvas3 = FigureCanvasTkAgg(self.fig3, self.resistanceframe)
        self.canvas3.show()
        self.canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas3._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')
        
        #data
        self.xlist1 = []
        self.ylist1 = []
        self.xlist2 = []
        self.ylist2 = []
        self.xlist3 = []
        self.ylist3 = []

        #fluke frame
        self.flukeframe = tk.Frame(self.rightframe)
        self.flukeframe.grid(row = 1, column = 0, rowspan = 2, sticky = 'nsew' )
        self.flukeframe.grid_rowconfigure(0,weight=1)
        self.flukeframe.grid_columnconfigure(0,weight=1)
        self.flukefig = plt.Figure(figsize=(5,5))
        self.flukeax = self.flukefig.add_subplot(1,1,1)
        self.flukeline, = self.flukeax.plot([], [], lw=2, color = 'r')
        self.flukeax.set_title('Fluke Primary Display:')
        self.flukecanvas = FigureCanvasTkAgg(self.flukefig,self.flukeframe)
        self.flukecanvas.show()
        self.flukecanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.flukecanvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')

        #fluke data
        self.fluke_primarylist_time = np.array([])
        self.fluke_primarylist_data = np.array([])

        self.showkeithley()

    def showkeithley(self):    
        self.stop_flukegraph()
        self.keithleyraised = True
        self.currentframe.tkraise()
        self.resistanceframe.tkraise()

    def stop_flukegraph(self):
        if self.fluke_callback is not None:
            self.after_cancel(self.fluke_callback)

    def showfluke(self):
        #if self.callback is not None:
         #   self.stop() #stop the keithley from plotting
        self.flukeframe.tkraise()
        self.keithleyraised = False
        self.start_flukegraph()
        #start a thread that gets line information from fluke frame
        #flukethread = threading.Thread(target = self.updateflukegraph)
        #flukethread.start()

    def start_flukegraph(self):
        self.flukeframereference = self.controller.frames[fluke8808a_control_frame]       
        self.fluke_primarylist_time = self.flukeframereference.primarylist_time
        self.fluke_primarylist_data = self.flukeframereference.primarylist_data
        self.update_flukegraph()

    def update_flukegraph(self):
        def totalseconds(x):
            return (x - datetime.datetime(1970,1,1)).total_seconds()
        totalseconds = np.vectorize(totalseconds)
        #update temperature graph
        while not (self.fluke8808a.primaryq.empty()):
            primarydata = self.fluke8808a.primaryq.get()
            timeprimary = primarydata[0]
            tempprimary = primarydata[1]
            unitprimary = primarydata[2]
            self.fluke_primarylist_time = np.append(self.fluke_primarylist_time, timeprimary)
            self.fluke_primarylist_data = np.append(self.fluke_primarylist_data, tempprimary)
            self.flukeline.set_data(totalseconds(self.fluke_primarylist_time), self.fluke_primarylist_data )
            #pass data back to fluke frame
            self.flukeframereference.primarylist_time = self.fluke_primarylist_time
            self.flukeframereference.primarylist_data = self.fluke_primarylist_data 
            self.flukeax.relim()
            self.flukeax.autoscale_view()
            #change axes
            if self.fluke_primarylist_time.size > 0 and self.fluke_primarylist_data.size > 0:
                self.flukeax.set_title('Primary Display: %g%s ' % (self.fluke_primarylist_data[-1], unitprimary))
            self.flukecanvas.draw_idle()
        self.fluke_callback = self.after(100,self.update_flukegraph)       
    
    def stop_keithleygraph(self):
        if self.keithley_callback is not None:
            self.after_cancel(self.keithley_callback)    

    def stop_graph(self):
        self.stop_keithleygraph()
        self.stop_flukegraph()

    def rampup(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            self.setkeithleyparameters()
            return self.startrampup()
        if self.running and self.keithley.rampup_active: #then the voltage is currently ramping and user wants to pause the ramp
            self.ani = False
            self.keithley.stop_event.set() #stop ramping
            self.pauseramp()
            #self.stopgraph_event.set()
        elif self.running and (not self.keithley.rampup_active): #the the ramp is complete and the user wants to restart the ramp or do another ramp
            self.keithley.stop_event.set() #stop the thread
            #self.stopgraph_event.set() #stop the graph
            self.stop_keithleygraph() #stop the graph
            self.setkeithleyparameters() #set parameters
            #note: in this case the user has no choice over the start voltage. It will be whatever the final voltage from the previous ramp was
            self.voltagestartstr.set(str(self.keithley.v1))
            self.keithley.v0 = self.keithley.v1
            return self.startrampup()
        else: #then the user wants to continue the ramp Note: the ramp parameters (v0 and v1) are still stored in the keithley instance
            self.keithley.stop_event.set() #stop the thread
            return self.startrampup()
        

    def startrampup(self):
        self.keithley.rampup_active = True
        self.update_graph()
        self.keithley.rampUp()
        time.sleep(0.002)
        self.ani = True
        self.running = True

    def pauseramp(self):
        self.running = False
        self.rampupbtn.config(text='Ramp Up', background = "green4")
        self.rampdownbtn.config(text='Ramp Down', background = "blue")
        self.keithley.pauseRamp()

    def rampdown(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            self.setkeithleyparameters()
            self.startrampdown()
        if self.running and self.keithley.rampdown_active: #then the voltage is currently ramping and user wants to pause the ramp
            self.ani = False
            self.keithley.stop_event.set() #stop ramping
            self.pauseramp()
        elif self.running and (not self.keithley.rampdown_active): #then the ramp is complete and the user wants to restart the ramp or do another ramp
            self.keithley.stop_event.set() #stop the thread
            self.stop_keithleygraph() #stop the graph
            self.setkeithleyparameters() #set parameters
            #note: in this case the user has no choice over the start voltage. It will be whatever the final voltage from the previous ramp was
            self.keithley.v0 = self.keithley.v1
            self.startrampdown()
        else: #then the user wants to continue the ramp Note: the ramp parameters (v0 and v1) are still stored in the keithley instance
            self.keithley.stop_event.set() #stop the thread
            self.startrampdown()

    def startrampdown(self):
        self.keithley.rampdown_active = True
        time.sleep(0.002)
        self.keithley.rampDown()
        self.update_graph()
        self.ani = True
        self.running = True

    #need a stop ramp method to keep the graph from updating too. Graph will stop when the Keithley output is disabled
    def turnoff(self):
        if self.keithley.rampup_active or self.keithley.rampdown_active: #then user wants to disable output from Keithley but the ramp is running
            tkMessageBox.showwarning("Warning:","Voltage is currently ramping and cannot turn off. In emergency, click Abort")
        else:
            self.keithley.stop_event.set()
            while (self.keithley.thread_active):  #wait to make sure that other methods are completed with the thread
                time.sleep(0.002)
            self.stop_keithleygraph()
            self.keithley.turnOff()
            #reset graphs
            self.xlist1 = []
            self.ylist1 = []
            self.xlist2 = []
            self.ylist2 = []
            self.xlist3 = []
            self.ylist3 = []

            self.line1.set_data(self.xlist1,self.ylist1)
            self.line2.set_data(self.xlist2,self.ylist2)
            self.line3.set_data(self.xlist3,self.ylist3)

            self.canvas1.draw_idle()
            self.canvas2.draw_idle()
            self.canvas3.draw_idle()

            #clear the keithley queues
            while self.keithley.thread_active:
                time.sleep(0.002) #wait for the measurement to stop
            #clear the measurement queue
            self.keithley.clear_queues()
            #change running state
            self.running = False

    def update_graph(self):
        while (not self.keithley.dataq.empty()):
            parseddata = self.keithley.dataq.get()
            
            self.xlist1.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.ylist1.append(parseddata[1]) 
            self.line1.set_data(self.xlist1,self.ylist1)

            self.xlist2.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.ylist2.append(parseddata[2])
            self.line2.set_data(self.xlist2,self.ylist2)
        
            self.xlist3.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.ylist3.append(parseddata[3])
            self.line3.set_data(self.xlist3,self.ylist3)
        
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.ax3.relim()
            self.ax3.autoscale_view()

            self.canvas1.draw_idle()
            self.canvas2.draw_idle()
            self.canvas3.draw_idle()

        self.keithley_callback = self.after(100, self.update_graph)

    def update_buttons(self):
        #I only need to change the buttons from the paused state if the ramp is not active
        #this is becuase after the ramp is complete, it doesn't automatically call pauseramp to change the buttons back to their original state
        if (not self.keithley.rampup_active and self.rampupbtn['text'] != "Ramp Up"):
            self.rampupbtn.config(text="Ramp Up", background = "green4")
        if (not self.keithley.rampdown_active and self.rampdownbtn['text'] != "Ramp Down"):
            self.rampdownbtn.config(text="Ramp Down", background = "blue")

    def setkeithleyparameters(self):
        self.keithley.rampstart = float(self.voltagestartstr.get())
        self.keithley.v0 = self.keithley.rampstart
        self.keithley.rampend = float(self.voltageendstr.get())
        self.keithley.deltaV = float(self.voltagestepstr.get())
        self.keithley.ramprate = float(self.rampratestr.get())


    def abortramp(self):
        self.keithley.abort()