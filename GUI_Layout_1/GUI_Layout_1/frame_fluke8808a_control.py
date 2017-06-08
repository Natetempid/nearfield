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

class fluke8808a_control_frame(tk.Frame):
    def __init__(self,master,controller,usbswitch,fluke8808a):
        tk.Frame.__init__(self,master)
        #self.grid_rowconfigure(0,weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.usbswitch = usbswitch
        self.fluke8808a = fluke8808a
        self.running = False
        self.ani = None
        self.stopgraph_event = threading.Event()
        
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
        self.plotframe.grid_rowconfigure(0,weight = 1)
        self.plotframe.grid_rowconfigure(1,weight = 1)
        self.plotframe.grid_columnconfigure(0,weight = 1)
        self.plotframe.grid(row = 0, column = 1, rowspan = 2, sticky = 'nsew')
        
        self.primarypltframe = tk.Frame(self.plotframe)
        self.primarypltframe.grid(row = 0, column = 0, sticky = 'nsew')
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
        self.secondarypltframe.grid(row = 1, column = 0, sticky = 'nsew')
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

        self.intervalframe = tk.Frame(self.plotframe)
        self.intervalframe.grid(row = 2, column = 0, sticky = 'nsew')
        self.intervalframe.grid_columnconfigure(0,weight = 1)
        self.intervalframe.grid_columnconfigure(1,weight = 1)
        self.intervalframe.grid_columnconfigure(2,weight = 1)
        self.intervallbl = tk.Label(self.intervalframe, text = "Time Step (s)")
        self.intervallbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(self.intervalframe, textvariable = self.intervalstr, width=5)
        self.interval.grid(row = 0, column = 1, sticky = 'nsew')
        self.startbtn = ttk.Button(self.intervalframe, text='Start', command= lambda: self.on_click())
        self.startbtn.grid(row = 0, column = 2, sticky = 'nsew')

    def on_click(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani = False
            self.fluke8808a.stop_event.set()
            self.stopgraph_event.set()
            self.startbtn.config(text='Start')
        else:
            self.startbtn.config(text='Stop')
            return self.start()
        self.running = not self.running

    def start(self):
        self.startbtn.config(text='Stop')
        self.fluke8808a.measureBothDisplays(float(self.intervalstr.get()))
        t = threading.Thread(target = self.animation_target)
        t.start()
        self.ani = True
        self.running = True

    def update_graph(self):
        xlist1 = []
        ylist1 = []
        xlist2 = []
        ylist2 = []
        for elem1 in self.fluke8808a.list1:
            xlist1.append((elem1['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            #need to interpet the units
            ylist1.append(elem1['data']) 
        self.line1.set_data(xlist1,ylist1)
        for elem2 in self.fluke8808a.list2:
            xlist2.append((elem2['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylist2.append(elem2['data'])
        self.line2.set_data(xlist2,ylist2)
        #adjust axes
        if xlist1 and ylist1:
            self.ax1.set_ylim(min(ylist1), max(ylist1))
            self.ax1.set_xlim(min(xlist1), max(xlist1))
            self.ax1.set_title('Primary Display: %s' % elem1['unit'])
        if xlist2 and ylist2:
            self.ax2.set_ylim(min(ylist2), max(ylist2))
            self.ax2.set_xlim(min(xlist2), max(xlist2))
            self.ax2.set_title('Secondary Display: %s' % elem2['unit'])
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()

    def animation_target(self):
        self.stopgraph_event.clear()
        while(not self.stopgraph_event.is_set()):
            time.sleep(float(self.intervalstr.get()))
            self.update_graph()
        self.stopgraph_event.set() #once animation stops, reset the stop event to trigger again


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