import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import threading
from frame_usbswitch_diagram import usbswitch_diagram_frame
from subframe_fluke8808a_plot import fluke8808a_plot_subframe
import numpy as np
import Queue as q


class fluke8808a_control_frame(tk.Frame):
    def __init__(self,master,controller,usbswitch,fluke8808a):
        tk.Frame.__init__(self,master)
        self.grid_rowconfigure(1,weight = 1) #mess with frames
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.usbswitch = usbswitch
        self.fluke8808a = fluke8808a
        self.running = False
        self.ani = None
        self.stopgraph_event = threading.Event()

        self.measurement_running = False
        self.plot_running = False
        self.callback = None

        #datalists
        self.primarylist_time = np.array([])
        self.primarylist_data = np.array([])
        self.secondarylist_time = np.array([])
        self.secondarylist_data = np.array([])
        
        self.usbswitchframe = usbswitch_diagram_frame(self,controller,self.usbswitch)
        self.usbswitchframe.config(borderwidth = 5, relief = tk.GROOVE)
        self.usbswitchframe.grid(row = 0, column = 0, sticky = 'nsew')

        #Frame to configure Fluke Primary and Secondary Displays
        self.configframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.configframe.grid(row = 1, column = 0, sticky = 'nsew')
        for k in range(0,4):
            self.configframe.grid_rowconfigure(k,weight=1)
        self.configframe.grid_columnconfigure(0, weight = 1)
        self.configframe.grid_columnconfigure(1, weight = 1)
       
        self.primarylbl = tk.Label(self.configframe, text = "Primary Display", font = ("tkDefaultFont",18))
        self.primarylbl.grid(row = 0, column = 0, sticky = 'nw')
        self.primary_str = tk.StringVar()
        self.primary_list = ["DC Voltage","DC Current","Resistance"]
        self.primary_str.set(self.primary_list[0]) 
        self.primarymenu = ttk.OptionMenu(self.configframe, self.primary_str, self.primary_list[0], *self.primary_list)
        self.primarymenu.grid(row = 1, column = 0, sticky = 'nsew')
        self.primaryconfigbtn = ttk.Button(self.configframe, text = 'Config', command = lambda: self.configPrimaryDisplay())
        self.primaryconfigbtn.grid(row = 0, column = 1, rowspan = 2, sticky = 'nsew')
        
        self.primaryvallbl = tk.Label(self.configframe, text = "Primary Raw Value", font = ("tkDefaultFont",18))
        self.primaryvallbl.grid(row = 0, column = 2, sticky = 'nw')
        self.primaryvalstr = tk.StringVar()
        self.primaryvalstr.set('INF')
        self.primaryval = tk.Label(self.configframe, textvariable = self.primaryvalstr,font = ("tkDefaultFont",16), background = 'white')
        self.primaryval.grid(row = 1, column = 2, sticky = 'nsew')
        
        
        self.secondarylbl = tk.Label(self.configframe, text = "Secondary Display", font = ("tkDefaultFont",18))
        self.secondarylbl.grid(row = 2, column = 0, sticky = 'nw')
        self.secondary_str = tk.StringVar()
        self.secondary_list = ["DC Voltage","DC Current","Resistance"]
        self.secondary_str.set(self.secondary_list[0])
        self.secondarymenu = ttk.OptionMenu(self.configframe, self.secondary_str, self.secondary_list[0], *self.secondary_list)
        self.secondarymenu.grid(row = 3, column = 0, sticky = 'nsew')
        self.secondaryconfigbtn = ttk.Button(self.configframe, text = 'Config', command = lambda: self.configSecondaryDisplay())
        self.secondaryconfigbtn.grid(row = 2, column = 1, rowspan = 2, sticky = 'nsew')

        self.secondaryvallbl = tk.Label(self.configframe, text = "Secondary Raw Value", font = ("tkDefaultFont",18))
        self.secondaryvallbl.grid(row = 2, column = 2, sticky = 'nw')
        self.secondaryvalstr = tk.StringVar()
        self.secondaryvalstr.set('INF')
        self.secondaryval = tk.Label(self.configframe, textvariable = self.secondaryvalstr, font = ("tkDefaultFont",18), background = 'white')
        self.secondaryval.grid(row = 3, column = 2, sticky = 'nsew')
        #get individual reading
        self.primarybtn = ttk.Button(self.configframe, text = "Instant Reading", command = lambda: self.getPrimaryReading())
        self.primarybtn.grid(row = 0, column = 3, rowspan = 2, sticky = 'nsew')
        self.secondarybtn = ttk.Button(self.configframe, text = "Instant Reading", command = lambda: self.getSecondaryReading())
        self.secondarybtn.grid(row = 2, column = 3, rowspan = 2, sticky = 'nsew')

        #setup measurement frame
        self.switchsetupframe = tk.Frame(self.configframe)
        self.switchsetupframe.grid(row = 4, column = 0, columnspan = 4, sticky = 'nsew')
        for k in range(0,4):
            self.switchsetupframe.grid_columnconfigure(k,weight = 1)
        self.r1btn = ttk.Button(self.switchsetupframe, text = "Resistance 1", command = lambda: self.setUSBRes1())
        self.r1btn.grid(row = 0, column = 0, sticky = 'nsew')
        self.r2btn = ttk.Button(self.switchsetupframe, text = "Resistance 2", command = lambda: self.setUSBRes2())
        self.r2btn.grid(row = 0, column = 1, sticky = 'nsew')
        self.vbtn = ttk.Button(self.switchsetupframe, text = "Voltage", command = lambda: self.setUSBVoltage())
        self.vbtn.grid(row = 0, column = 2, sticky = 'nsew')
        self.ibtn = ttk.Button(self.switchsetupframe, text = "Current", command = lambda: self.setUSBCurrent())
        self.ibtn.grid(row = 0, column = 3, sticky = 'nsew')

        #####################
        ## Start 5/30 by defining these functions

        #Plotting
        #self.plotframe = fluke8808a_plot_subframe(self,self.fluke8808a)
        #self.plotframe.grid(row = 0, column = 1, sticky = 'nsew')
        self.plotframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.plotframe.grid_rowconfigure(1,weight = 1)
        self.plotframe.grid_rowconfigure(2,weight = 1)
        self.plotframe.grid_columnconfigure(0,weight = 1)
        self.plotframe.grid(row = 0, column = 1, rowspan = 2, sticky = 'nsew')
        
        self.primarypltframe = tk.Frame(self.plotframe)
        self.primarypltframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.primarypltframe.grid_rowconfigure(0, weight = 1)
        self.primarypltframe.grid_columnconfigure(0, weight = 1)
        self.fig1 = plt.Figure()
        self.ax1 = self.fig1.add_subplot(1,1,1)
        self.line1, = self.ax1.plot([], [], lw=2, color = 'r')
        self.ax1.set_title('Primary Display:')
        self.canvas1 = FigureCanvasTkAgg(self.fig1,self.primarypltframe)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas1._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.secondarypltframe = tk.Frame(self.plotframe)
        self.secondarypltframe.grid(row = 2, column = 0, sticky = 'nsew')
        self.secondarypltframe.grid_rowconfigure(0, weight = 1)
        self.secondarypltframe.grid_columnconfigure(0, weight = 1)
        self.fig2 = plt.Figure()
        self.ax2 = self.fig2.add_subplot(1,1,1)
        self.ax2.set_title('Secondary Display:')
        self.line2, = self.ax2.plot([], [], lw=2, color = 'r')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.secondarypltframe)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas2._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #Header frame that includes all controls
        self.headerframe = tk.Frame(self.plotframe, borderwidth = 5, relief = tk.GROOVE)
        self.headerframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.headerframe.grid_rowconfigure(0,weight = 1)
        #self.headerframe.grid_columnconfigure(3,weight=1)
        #self.headerframe.grid_columnconfigure(4,weight=1)
        self.headerframe.grid_columnconfigure(5,weight=1)
        #canvas for indicator
        self.indicator_canvas = tk.Canvas(self.headerframe, width = 50, height = 50)
        self.indicator_canvas.grid(row = 0, column = 0, sticky = 'ns')
        self.indicator = self.indicator_canvas.create_oval(5,5,40,40, fill = 'red4')
        self.indicatorstr = tk.StringVar()
        self.indicatorstr.set('Not Measuring')
        self.indicatorlbl = tk.Label(self.headerframe, textvariable = self.indicatorstr, font = ('tkDefaultFont', 12), width = 14)
        self.indicatorlbl.grid(row = 0, column = 1, sticky = 'nsew')
        #Time interval
        self.intervalframe = tk.Frame(self.headerframe,borderwidth = 5)
        self.intervalframe.grid(row = 0, column = 2, sticky = 'nsew')
        self.intervalframe.grid_rowconfigure(0,weight = 1)
        self.intervalframe.grid_columnconfigure(0, weight = 1)
        self.interval_lbl = tk.Label(self.intervalframe, text = 'Time Step (s)')
        self.interval_lbl.grid(row = 0, column = 0)
        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(self.intervalframe, textvariable = self.intervalstr, width=5)
        self.interval.grid(row = 1, column = 0, sticky = 'nsew')
        #Measure Button
        self.measure_btn = ttk.Button(self.headerframe, text = 'Start Measurement', command = lambda:self.measure_click(), width = 25)
        self.measure_btn.grid(row = 0, column = 3, sticky = 'nsew')
        #Plot Button
        self.measure_and_plot_btn = ttk.Button(self.headerframe, text = 'Start Measurement & Plot', command = lambda: self.measure_and_plot_click(), width = 25)
        self.measure_and_plot_btn.grid(row = 0, column = 4, sticky = 'nsew')
        #Reset Plot Button
        self.resetbtn = ttk.Button(self.headerframe, text = 'Reset Graphs', command = lambda: self.reset_graphs())#, width = 22)
        self.resetbtn.grid(row = 0, column = 5, sticky = 'nsew')


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
        self.fluke8808a.measureBothDisplays(float(self.intervalstr.get()))
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "green2")    
        self.indicatorstr.set('Measuring...')
        #change measurement button
        self.measure_btn.config(text = 'Stop Measurement & Plot')
        #change measurement running state
        self.measurement_running = True

    def stop_instrument(self):
        self.fluke8808a.stop_event.set()
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "red4")    
        self.indicatorstr.set('Not Measuring')
        #change measurement button
        self.measure_btn.config(text = 'Start Measurement')   
        while self.fluke8808a.thread_active:
            time.sleep(0.002) #wait for the measurement to stop
        #clear the measurement queue
        self.fluke8808a.clear_queues()
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
        if self.callback is not None:
            self.after_cancel(self.callback)

    def update_graph(self):
        #try:
        def totalseconds(x):
            return (x - datetime.datetime(1970,1,1)).total_seconds()
        totalseconds = np.vectorize(totalseconds)
        #update temperature graph
        while not (self.fluke8808a.primaryq.empty()):
            primarydata = self.fluke8808a.primaryq.get()
            timeprimary = primarydata[0]
            tempprimary = primarydata[1]
            unitprimary = primarydata[2]
            self.primarylist_time = np.append(self.primarylist_time, timeprimary)
            self.primarylist_data = np.append(self.primarylist_data, tempprimary)
            self.line1.set_data(totalseconds(self.primarylist_time), self.primarylist_data )
            self.ax1.relim()
            self.ax1.autoscale_view()
            #change axes
            if self.primarylist_time.size > 0 and self.primarylist_data.size > 0:
                self.ax1.set_title('Primary Display: %g%s ' % (self.primarylist_data[-1], unitprimary))
        while not (self.fluke8808a.secondaryq.empty()):
            secondarydata = self.fluke8808a.secondaryq.get()
            timesecondary = secondarydata[0]
            tempsecondary = secondarydata[1]
            unitsecondary = secondarydata[2]
            self.secondarylist_time = np.append(self.secondarylist_time, timesecondary)
            self.secondarylist_data = np.append(self.secondarylist_data, tempsecondary)
            self.line2.set_data(totalseconds(self.secondarylist_time), self.secondarylist_data )
            self.ax2.relim()
            self.ax2.autoscale_view()
            #change axes
            if self.secondarylist_time.size > 0 and self.secondarylist_data.size > 0:
                self.ax2.set_title('Secondary Display: %g%s ' % (self.secondarylist_data[-1], unitsecondary))
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()
        self.callback = self.after(100, self.update_graph)

    #def update_graph(self):
    #    xlist1 = []
    #    ylist1 = []
    #    xlist2 = []
    #    ylist2 = []
    #    for elem1 in self.fluke8808a.list1:
    #        xlist1.append((elem1['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
    #        #need to interpet the units
    #        ylist1.append(elem1['data']) 
    #    self.line1.set_data(xlist1,ylist1)
    #    for elem2 in self.fluke8808a.list2:
    #        xlist2.append((elem2['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
    #        ylist2.append(elem2['data'])
    #    self.line2.set_data(xlist2,ylist2)
    #    #adjust axes
    #    if xlist1 and ylist1:
    #        self.ax1.set_ylim(min(ylist1), max(ylist1))
    #        self.ax1.set_xlim(min(xlist1), max(xlist1))
    #        self.ax1.set_title('Primary Display: %s' % elem1['unit'])
    #    if xlist2 and ylist2:
    #        self.ax2.set_ylim(min(ylist2), max(ylist2))
    #        self.ax2.set_xlim(min(xlist2), max(xlist2))
    #        self.ax2.set_title('Secondary Display: %s' % elem2['unit'])
    #    self.canvas1.draw_idle()
    #    self.canvas2.draw_idle()
    
    def reset_graphs(self):
        self.primarylist_time = np.array([])
        self.primarylist_data = np.array([])
        self.secondarylist_time = np.array([])
        self.secondarylist_data = np.array([])

        self.line1.set_data(self.primarylist_time, self.primarylist_data )
        self.line2.set_data(self.secondarylist_time, self.secondarylist_data )
        
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()


    def configPrimaryDisplay(self):
        #setup measure routine, so it can be interrupted to change configuration
        self.primaryconfigbtn.config(state = tk.DISABLED)
        self.secondaryconfigbtn.config(state = tk.DISABLED)
        if self.running: #need to stop running by running "on_click"
            self.on_click()
            while self.fluke8808a.thread_active:
            #ask if the thread has truly stopped
                time.sleep(0.002)
            #config
            self.fluke8808a.configPrimaryDisplay(self.primary_str.get())
            self.on_click() #start run again
        else:
            time.sleep(0.002)
            self.fluke8808a.configPrimaryDisplay(self.primary_str.get())
        self.primaryconfigbtn.config(state = tk.NORMAL)
        self.secondaryconfigbtn.config(state = tk.NORMAL)

    def configSecondaryDisplay(self):
        #setup measure routine, so it can be interrupted to change configuration
        self.primaryconfigbtn.config(state = tk.DISABLED)
        self.secondaryconfigbtn.config(state = tk.DISABLED)
        if self.running: #need to stop running by running "on_click"
            self.on_click()
            while self.fluke8808a.thread_active:
            #ask if the thread has truly stopped
                time.sleep(0.002)
            #config
            self.fluke8808a.configSecondaryDisplay(self.secondary_str.get())
            self.on_click() #start run again
        else:
            time.sleep(0.002)
            self.fluke8808a.configSecondaryDisplay(self.secondary_str.get())
        self.primaryconfigbtn.config(state = tk.NORMAL)
        self.secondaryconfigbtn.config(state = tk.NORMAL)


    def getPrimaryReading(self):
        self.primarybtn.config(state = tk.DISABLED)
        if self.running: #need to stop running by running "on_click"
            self.on_click()
            while self.fluke8808a.thread_active:
            #ask if the thread has truly stopped
                time.sleep(0.002)
            #config
            self.fluke8808a.singlePrimaryDisplay()
            self.on_click() #start run again
        else:
            time.sleep(0.002)
            self.fluke8808a.singlePrimaryDisplay()
        self.primaryvalstr.set('%g %s' % (self.fluke8808a.single1['data'], self.fluke8808a.single1['unit']))
        self.primarybtn.config(state = tk.NORMAL)

    def getSecondaryReading(self):
        self.secondarybtn.config(state = tk.DISABLED)
        if self.running: #need to stop running by running "on_click"
            self.on_click()
            while self.fluke8808a.thread_active:
            #ask if the thread has truly stopped
                time.sleep(0.002)
            #config
            self.fluke8808a.singleSecondaryDisplay()
            self.on_click() #start run again
        else:
            time.sleep(0.002)
            self.fluke8808a.singleSecondaryDisplay()
        self.secondaryvalstr.set('%g %s' % (self.fluke8808a.single2['data'], self.fluke8808a.single2['unit']))
        self.secondarybtn.config(state = tk.NORMAL)

    
    def setUSBGeneral(self, relay1, relay2, type):
        #configure usbswitch to open relays1 and relay2 and close all others and configure fluke primary display to measure type
        self.usbswitch.turnOffAllRelays()
        for k in range(0,8):
            self.usbswitchframe.relaybtns[k].updateState()
        time.sleep(0.1)
        self.usbswitchframe.relaybtns[relay1].change_state()
        time.sleep(0.1)
        self.usbswitchframe.relaybtns[relay2].change_state()

        #now configure fluke to measure type at primary display
        self.primary_str.set(type)
        self.configPrimaryDisplay()

    def setUSBRes1(self):
        self.setUSBGeneral(0,4,"Resistance")

    def setUSBRes2(self):
        self.setUSBGeneral(1,5,"Resistance")

    def setUSBVoltage(self):
        self.setUSBGeneral(2,6,"DC Voltage")

    def setUSBCurrent(self): #need to edit this so that primary display is voltage and secondary is current
        #set voltage for primary display
        self.setUSBVoltage()
        #current will go on the secondary display and only needs switch 8. 
        if not self.usbswitchframe.relaybtns[7].relay.status:
            #then relay 8 is closed and should be kept open
            self.usbswitchframe.relaybtns[7].change_state()
        #now configure fluke to measure current at secondary display
        self.secondary_str.set("DC Current")
        self.configSecondaryDisplay()