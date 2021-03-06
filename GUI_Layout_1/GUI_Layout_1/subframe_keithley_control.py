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
#from frame_fluke8808a_control import fluke8808a_control_frame
import Queue as q
import numpy as np


class keithley_control_subframe(tk.Frame):
    def __init__(self, master, controller, root, keithley ):
        tk.Frame.__init__(self, master)
        self.master = master
        self.root = root
        self.controller = controller
        self.keithley = keithley

        self.keithleyframe = None

        self.outputon = False
    
        self.rampthread = threading.Thread()
        self.rampevent = threading.Event()
        self.rampevent.set()
        self.rampthread_active = False

        #self.grid_rowconfigure(0,weight = 1)
        #self.grid_columnconfigure(0, weight = 1)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.headingstr = tk.StringVar()
        self.headingstr.set('Keithley')
        self.headinglbl = tk.Label(self, textvariable = self.headingstr, font = ('tkDefaultFont', 18))
        self.headinglbl.grid(row = 0, column = 0, sticky = 'new')

        self.maxminlblframe = tk.LabelFrame(self, text = 'Max/Min Values')
        self.maxminlblframe.grid(row = 1, column = 0, sticky = 'new')
        self.maxminlblframe.grid_columnconfigure(0, weight = 1)
        self.maxminsubframe = tk.Frame(self.maxminlblframe)
        self.maxminsubframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.maxminsubframe.grid_columnconfigure(0, weight = 1)
        self.maxminsubframe.grid_columnconfigure(1, weight = 1)
        self.maxlbl = tk.Label(self.maxminsubframe, text = 'Max Limit (V)')
        self.maxlbl.grid(row = 0, column = 0, sticky ='nsew')
        self.minlbl = tk.Label(self.maxminsubframe, text = 'Min Limit (V)')
        self.minlbl.grid(row = 0, column = 1, sticky ='nsew')
        self.maxstr = tk.StringVar()
        self.maxstr.set(str(self.keithley.maxvoltage))
        self.maxentry = tk.Entry(self.maxminsubframe, textvariable = self.maxstr)
        self.maxentry.grid(row = 1, column = 0, sticky = 'nsew')
        self.minstr = tk.StringVar()
        self.minstr.set(str(self.keithley.minvoltage))
        self.minentry = tk.Entry(self.maxminsubframe, textvariable = self.minstr)
        self.minentry.grid(row = 1, column = 1, sticky = 'nsew')
        self.setlimitsbtn = ttk.Button(self.maxminlblframe, text = 'Update Keithley Limits', command = lambda: self.updatekeithleylimits() )
        self.setlimitsbtn.grid(row = 1, column = 0, sticky = 'nsew' )

        self.outputonoffframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.outputonoffframe.grid(row = 2, column = 0, sticky = 'ew')
        self.outputonoffframe.grid_columnconfigure(1, weight = 1)
        self.onoffindicator_canvas = tk.Canvas(self.outputonoffframe, width = 25, height = 25)
        self.onoffindicator_canvas.grid(row = 0, column = 0, sticky = 'ns')
        self.onoffindicator = self.onoffindicator_canvas.create_oval(5,5,20,20, fill = 'gray38')
        self.outputonoffbtn = ttk.Button(self.outputonoffframe, text = 'Ouput On/Off', command = lambda: self.outputonoffclick() )
        self.outputonoffbtn.grid(row = 0, column = 1, sticky = 'nsew')

        self.lastreadinglblframe = tk.LabelFrame(self, text = 'Last Reading')
        self.lastreadinglblframe.grid(row = 3, column = 0, sticky = 'new')
        self.lastreadinglblframe.grid_rowconfigure(0, weight = 1)
        self.lastreadinglblframe.grid_columnconfigure(0, weight = 1)
        self.lastreadingstr = tk.StringVar()
        self.lastreadingstr.set('0')
        self.lastreadinglbl = tk.Label(self.lastreadinglblframe, textvariable = self.lastreadingstr)
        self.lastreadinglbl.grid(row = 0, column = 0, sticky = 'nsew')

        self.voltagesteplblframe = tk.LabelFrame(self, text = 'Voltage Step (V)')
        self.voltagesteplblframe.grid(row = 4, column = 0, sticky = 'new')
        self.voltagesteplblframe.grid_rowconfigure(0, weight = 1)
        self.voltagesteplblframe.grid_columnconfigure(0, weight = 1)
        self.voltagestepstr = tk.StringVar()
        self.voltagestepstr.set('1')
        self.voltagesteplbl = tk.Entry(self.voltagesteplblframe, textvariable = self.voltagestepstr )
        self.voltagesteplbl.grid(row = 0, column = 0, sticky = 'nsew')
        
        self.updownframe = tk.Frame(self)
        self.updownframe.grid(row = 5, column = 0, sticky = 'new')
        self.updownframe.grid_columnconfigure(0, weight = 1)
        upimage = tk.PhotoImage(file = 'up.gif')
        downimage = tk.PhotoImage(file = 'down.gif')
        self.upbtn = tk.Button(self.updownframe, image = upimage, bg = 'white', command = lambda: self.incrementVoltage())
        self.upbtn.grid(row = 0, column = 0, sticky = 'ew')
        self.downbtn = tk.Button(self.updownframe, image = downimage, bg = 'white', command = lambda: self.decrementVoltage())
        self.downbtn.grid(row = 1, column = 0, sticky = 'ew')
        self.upbtn.image = upimage
        self.downbtn.image = downimage
        self.bindingcheckvar = tk.IntVar()
        self.bindingcheckvar.set(0)
        self.bindingcheckbtn = tk.Checkbutton(self.updownframe, text = 'Bind Arrow Keys', variable = self.bindingcheckvar, command = lambda: self.bindarrowkeys())
        self.bindingcheckbtn.grid(row = 2, column = 0, sticky = 'ew')

        #abort and  turn off buttons
        self.offbtnsframe = tk.Frame(self)
        self.offbtnsframe.grid(row = 6, column = 0, sticky = 'new')
        self.offbtnsframe.grid_rowconfigure(0, weight = 1)
        self.offbtnsframe.grid_columnconfigure(0, weight = 1)
        #self.offbtnsframe.grid_columnconfigure(1, weight = 1)
      #  self.offbtn = tk.Button(self.offbtnsframe, text = 'Off', bg = 'blue', fg = 'white', command = lambda: self.turnoff(), font = ('tkDefaultFont', 14))
       # self.offbtn.grid(row = 0, column = 0, sticky = 'new')
        self.abortbtn = tk.Button(self.offbtnsframe, text = 'Abort', bg = 'red', command = lambda: self.abort(), font = ('tkDefaultFont', 14) )
        self.abortbtn.grid(row = 0, column = 0, sticky = 'new')

        self.autorampframe = tk.Frame(self, borderwidth = 3, relief = tk.GROOVE)
        self.autorampframe.grid(row = 7, column = 0, sticky = 'new')
        self.autorampframe.grid_rowconfigure(1, weight = 1)
        self.autorampframe.grid_columnconfigure(0, weight = 1)
        self.autorampcheckvar = tk.IntVar()
        self.autorampcheckvar.set(0)
        self.autorampcheckbox = tk.Checkbutton(self.autorampframe, text = 'Auto Ramp', variable  = self.autorampcheckvar, command = lambda: self.setautoramp() )
        self.autorampcheckbox.grid(row = 0, column = 0, sticky = 'new')
        self.autorampsubframe = tk.Frame(self.autorampframe)
        self.autorampsubframe.grid(row = 1, column = 0, sticky = 'new')
        self.autorampsubframe.grid_columnconfigure(0, weight = 1)
        
        self.ramptimelbl = tk.Label(self.autorampsubframe, text = 'Ramp Time Step (s)')
        self.ramptimelbl.grid(row = 0, column = 0, sticky = 'new')
        self.ramptimestr = tk.StringVar()
        self.ramptimestr.set('10')
        self.ramptimeentry = tk.Entry(self.autorampsubframe, textvariable = self.ramptimestr)
        self.ramptimeentry.grid(row = 1, column = 0, sticky = 'new')
        self.rampupbtn = ttk.Button(self.autorampsubframe, text = 'Ramp up', command = lambda: self.rampup())
        self.rampupbtn.grid(row = 2, column = 0, sticky = 'new')
        self.rampdownbtn = ttk.Button(self.autorampsubframe, text = 'Ramp down', command = lambda: self.rampdown())
        self.rampdownbtn.grid(row = 3, column = 0, sticky = 'new')
        self.rampstatelbl = tk.Label(self.autorampsubframe, text = 'Ramping Idle')
        self.rampstatelbl.grid(row = 4, column = 0, sticky = 'new')
        self.rampstopbtn = tk.Button(self.autorampsubframe, text = 'Stop Ramp', command = lambda: self.stopramp())
        self.rampstopbtn.config(background = 'red', foreground = 'black')
        self.rampstopbtn.grid(row = 5, column = 0, sticky = 'new')
        self.disableframe(self.autorampsubframe)


    def updatekeithleylimits(self):
        print self.keithley.maxvoltage, self.keithley.minvoltage
        self.keithley.maxvoltage = float(self.maxstr.get())
        self.keithley.minvoltage = float(self.minstr.get())
        print self.keithley.maxvoltage, self.keithley.minvoltage

    def disableframe(self, frame):
        for child in frame.winfo_children():
            child.configure(state='disable')

    def enableframe(self, frame):
        for child in frame.winfo_children():
            child.configure(state='normal')

    def setautoramp(self):
        if self.autorampcheckvar.get():
            self.enableframe(self.autorampsubframe)            
        else:
            self.disableframe(self.autorampsubframe)            
    
    def stopramp(self):
        self.rampevent.set()
          

    def rampup(self):
        self.rampthread = threading.Thread(target = self.__rampup)
        self.rampthread.start()

    def __rampup(self):
        #reinitialize the ramp event and the rampactive bool
        self.rampevent.clear()
        self.rampthread_active = True
        #disable the rampdown button
        self.rampdownbtn.config(state = tk.DISABLED)
        self.rampstatelbl.config(text = 'Ramping Up...')
        while (not self.rampevent.is_set()):
            #get the time step
            timestep = float(self.ramptimestr.get())
            self.rampevent.wait(timestep)
            self.incrementVoltage() #comment out while testing
            if float(self.lastreadingstr.get()) >= self.keithley.maxvoltage:
                self.rampevent.set()
        #Reset all parameters back to normal state
        self.rampdownbtn.config(state = tk.NORMAL)
        self.rampstatelbl.config(text = 'Ramping Idle')                
        self.rampthread_active = False
        

    def rampdown(self):
        self.rampthread = threading.Thread(target = self.__rampdown)
        self.rampthread.start()

    def __rampdown(self):
        #reinitialize the ramp event and the rampactive bool
        self.rampevent.clear()
        self.rampthread_active = True
        #disable rampup btn
        self.rampupbtn.config(state = tk.DISABLED)
        self.rampstatelbl.config(text = 'Ramping Down...')
        while (not self.rampevent.is_set()):
            #get the time step
            timestep = float(self.ramptimestr.get())
            self.rampevent.wait(timestep)
            self.decrementVoltage() #comment out while testing
            if float(self.lastreadingstr.get()) <= self.keithley.minvoltage:
                self.rampevent.set()
            #Reset all parameters back to normal state
        self.rampupbtn.config(state = tk.NORMAL)
        self.rampstatelbl.config(text = 'Ramping Idle')                
        self.rampthread_active = False


    def outputonoffclick(self):
        #get previous state
        if self.keithley.outputon: #then turn off
            self.keithley.disableOutput()
            self.onoffindicator_canvas.itemconfig(self.onoffindicator, fill = "gray38")
        else:#turn on output
            self.keithley.enableOutput()
            self.onoffindicator_canvas.itemconfig(self.onoffindicator, fill = "RoyalBlue2")


    def bindarrowkeys(self): 
        if self.bindingcheckvar.get() == 1:
            self.root.bind('<Up>', self.uparrow)
            self.root.bind('<Down>', self.downarrow)
        else:
            self.root.unbind('<Up>')
            self.root.unbind('<Down>')

    def uparrow(self, event):
        self.incrementVoltage()

    def downarrow(self, event):
        self.decrementVoltage()

    def incrementVoltage(self):
        self.upbtn.config(state = tk.DISABLED)
        self.downbtn.config(state = tk.DISABLED)
        if self.keithleyframe == None:
            self.setKeithleyFrame()
        #set Keithley deltaV whatever the current delta V is
        self.keithley.deltaV = float( self.voltagestepstr.get() )
        #determine if keithley thread is running and data are being measured
        plotwasrunning = self.keithleyframe.plot_running #determine if plot was running before changing any frame settings
        print plotwasrunning
        if self.keithley.thread_active:
            #stop measurement and the plot
            self.keithleyframe.measure_click()
            while self.keithley.thread_active:
                time.sleep(0.002)
            #increment voltage
            data = self.keithley.incrementVoltage() 
            #restart measurement
            if plotwasrunning: #then the plot was also running, and need to restart the plot
                self.keithleyframe.measure_and_plot_click()
            else: #then only the measurement was running and the plot wasn't
                self.keithleyframe.measure_click()
        else:
            data = self.keithley.incrementVoltage()
        parseddata = self.keithley.parseData(data)
        self.lastreadingstr.set( str(parseddata[1]))
        self.upbtn.config(state = tk.NORMAL)
        self.downbtn.config(state = tk.NORMAL)

    def decrementVoltage(self):
        self.upbtn.config(state = tk.DISABLED)
        self.downbtn.config(state = tk.DISABLED)
        if self.keithleyframe == None:
            self.setKeithleyFrame()
        #set Keithley deltaV whatever the current delta V is
        self.keithley.deltaV = float( self.voltagestepstr.get() )
        #determine if keithley thread is running and data are being measured
        plotwasrunning = self.keithleyframe.plot_running #determine if plot was running before changing any frame settings
        if self.keithley.thread_active: #thread active problem
            #stop measurement
            self.keithleyframe.measure_click()
            while self.keithley.thread_active:
                time.sleep(0.002)
            #increment voltage
            data = self.keithley.decrementVoltage()
            #restart measurement
            if plotwasrunning: #then the plot was also running, and need to restart the plot
                self.keithleyframe.measure_and_plot_click()
            else: #then only the measurement was running and the plot wasn't
                self.keithleyframe.measure_click()
        else:
            data = self.keithley.decrementVoltage()
        parseddata = self.keithley.parseData(data)
        self.lastreadingstr.set( str(parseddata[1]))
        self.upbtn.config(state = tk.NORMAL)
        self.downbtn.config(state = tk.NORMAL)


    def setKeithleyFrame(self):
        self.keithleyframe = self.getKeithleyFrame()

    def getKeithleyFrame(self):
        framekeys = self.controller.frames.keys()
        for key in framekeys:
            if 'keithley_measure' in key.__name__:
                return self.controller.frames[key]

    def abort(self):
        self.keithley.abort()

    #def turnoff(self):
