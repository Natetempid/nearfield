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
        self.disablebtn = tk.Button(self.controlframe, text = "Turn Off", font = ("tkDefaultFont",14), command = lambda: self.turnoff())
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

        self.showkeithley()

    def showkeithley(self):
        self.keithleyraised = True
        self.currentframe.tkraise()
        self.resistanceframe.tkraise()

    def showfluke(self):
        self.flukeframe.tkraise()
        self.keithleyraised = False
        #start a thread that gets line information from fluke frame
        flukethread = threading.Thread(target = self.updateflukegraph)
        flukethread.start()

    def updateflukegraph(self):
        #get plot interval from fluke frame
        flukeframereference = self.controller.frames[fluke8808a_control_frame]
        interval = float(flukeframereference.intervalstr.get())
        #get data from the fluke frame
        while not (flukeframereference.stopgraph_event.is_set() or self.keithleyraised):
            time.sleep(interval)
            [xlist1, ylist1] = self.controller.frames[fluke8808a_control_frame].line1.get_data() #get data from the plot on the fluke frame. THis is so I don't have to get tehd ata from the fluke reference myself
            if len(xlist1) == len(ylist1):
                self.flukeline.set_data(xlist1, ylist1)
            if xlist1 and ylist1:
                self.flukeax.set_ylim(min(ylist1), max(ylist1))
                self.flukeax.set_xlim(min(xlist1), max(xlist1))
                self.flukeax.set_title('Primary Display')
            self.flukecanvas.draw_idle() #update the canvas
        print "fluke done"

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
            self.stopgraph_event.set() #stop the graph
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
        #self.rampupbtn.config(text='Pause Ramp', background = "salmon1")
        t = threading.Thread(target = self.animation_target)
        t.start()
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
            return self.startrampdown()
        if self.running and self.keithley.rampdown_active: #then the voltage is currently ramping and user wants to pause the ramp
            self.ani = False
            self.keithley.stop_event.set() #stop ramping
            self.pauseramp()
            #self.stopgraph_event.set()
        elif self.running and (not self.keithley.rampdown_active): #then the ramp is complete and the user wants to restart the ramp or do another ramp
            self.keithley.stop_event.set() #stop the thread
            self.stopgraph_event.set() #stop the graph
            self.setkeithleyparameters() #set parameters
            #note: in this case the user has no choice over the start voltage. It will be whatever the final voltage from the previous ramp was
            self.keithley.v0 = self.keithley.v1
            return self.startrampdown()
        else: #then the user wants to continue the ramp Note: the ramp parameters (v0 and v1) are still stored in the keithley instance
            self.keithley.stop_event.set() #stop the thread
            return self.startrampdown()
        self.running = not self.running

    def startrampdown(self):
        self.keithley.rampdown_active = True
        #self.rampdownbtn.config(text='Pause Ramp', background = "salmon1")
        time.sleep(0.002)
        t = threading.Thread(target = self.animation_target)
        t.start()
        print "Keithley Animation Thread-%d" % t.ident
        self.keithley.rampDown()
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
            self.stopgraph_event.set()
            self.keithley.turnOff()

    def animation_target(self):
        self.stopgraph_event.clear()
        while(not self.stopgraph_event.is_set()):
            self.stopgraph_event.wait(0.25)
            self.update_graph()
            #self.stopgraph_event.wait(0.25)
            #self.update_buttons()
            

    def update_graph(self):
        try:
            #rewrite this so the keithley data is put on a queue and it is pulled off and put into a list
            #if self.keithley.adddatum_event.is_set(): #if the keithley thread puts data onto the q, take off all elements
                #print "Trigger %s" % datetime.datetime.now()
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
        
                #adjust axes
                if self.xlist1 and self.ylist1:
                    self.ax1.set_ylim(min(self.ylist1), max(self.ylist1))
                    self.ax1.set_xlim(min(self.xlist1), max(self.xlist1))
                    self.ax1.set_title('Applied Bias: %.3fV' % parseddata[1])
                if self.xlist2 and self.ylist2:
                    self.ax2.set_ylim(min(self.ylist2), max(self.ylist2))
                    self.ax2.set_xlim(min(self.xlist2), max(self.xlist2))
                    self.ax2.set_title('Measured Current: %gA' % parseddata[2])
                if self.xlist3 and self.ylist3:
                    self.ax3.set_ylim(min(self.ylist3), max(self.ylist3))
                    self.ax3.set_xlim(min(self.xlist3), max(self.xlist3))
                    self.ax3.set_title('Measured Resistance: %gOhms' % parseddata[3])
                self.canvas1.draw_idle()
                self.canvas2.draw_idle()
                self.canvas3.draw_idle()
        except RuntimeError,e:
            print '%s: %s' % ("Keithley",e.message)
            if "dictionary changed size during iteration" in e.message:
                #disable the start button
                #self.startbtn.config(state = tk.DISABLED)
                #stop the graph animation
                self.ani = False
                self.stopgraph_event.set()
                #wait for animation to finish
                time.sleep(1.1)
                #restart thread
                t = threading.Thread(target = self.animation_target)
                t.start()
                print "Keithley Animation Thread-%d" % t.ident
                self.ani = True
                #renable start button
                #self.startbtn.config(state = tk.NORMAL) 

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