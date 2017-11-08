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

        #self.grid_rowconfigure(0,weight = 1)
        #self.grid_columnconfigure(0, weight = 1)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.headingstr = tk.StringVar()
        self.headingstr.set('Keithley')
        self.headinglbl = tk.Label(self, textvariable = self.headingstr, font = ('tkDefaultFont', 18))
        self.headinglbl.grid(row = 0, column = 0, sticky = 'new')

        self.lastreadinglblframe = tk.LabelFrame(self, text = 'Last Reading')
        self.lastreadinglblframe.grid(row = 1, column = 0, sticky = 'new')
        self.lastreadinglblframe.grid_rowconfigure(0, weight = 1)
        self.lastreadinglblframe.grid_columnconfigure(0, weight = 1)
        self.lastreadingstr = tk.StringVar()
        self.lastreadingstr.set('0')
        self.lastreadinglbl = tk.Label(self.lastreadinglblframe, textvariable = self.lastreadingstr)
        self.lastreadinglbl.grid(row = 0, column = 0, sticky = 'nsew')

        self.voltagesteplblframe = tk.LabelFrame(self, text = 'Voltage Step (V)')
        self.voltagesteplblframe.grid(row = 2, column = 0, sticky = 'new')
        self.voltagesteplblframe.grid_rowconfigure(0, weight = 1)
        self.voltagesteplblframe.grid_columnconfigure(0, weight = 1)
        self.voltagestepstr = tk.StringVar()
        self.voltagestepstr.set('1')
        self.voltagesteplbl = tk.Entry(self.voltagesteplblframe, textvariable = self.voltagestepstr )
        self.voltagesteplbl.grid(row = 0, column = 0, sticky = 'nsew')
        
        self.updownframe = tk.Frame(self)
        self.updownframe.grid(row = 3, column = 0, sticky = 'new')
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
        self.offbtnsframe.grid(row = 4, column = 0, sticky = 'new')
        self.offbtnsframe.grid_rowconfigure(0, weight = 1)
        self.offbtnsframe.grid_columnconfigure(0, weight = 1)
        #self.offbtnsframe.grid_columnconfigure(1, weight = 1)
      #  self.offbtn = tk.Button(self.offbtnsframe, text = 'Off', bg = 'blue', fg = 'white', command = lambda: self.turnoff(), font = ('tkDefaultFont', 14))
       # self.offbtn.grid(row = 0, column = 0, sticky = 'new')
        self.abortbtn = tk.Button(self.offbtnsframe, text = 'Abort', bg = 'red', command = lambda: self.abort(), font = ('tkDefaultFont', 14) )
        self.abortbtn.grid(row = 0, column = 0, sticky = 'new')

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
