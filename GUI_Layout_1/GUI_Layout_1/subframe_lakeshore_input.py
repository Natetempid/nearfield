import Tkinter as tk
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
from frame_lakeshore_command import lakeshore_command_frame
from frame_lakeshore_measure import lakeshore_measure_frame
from lakeshore335 import heater
import time

class input_subframe(tk.Frame):
    def __init__(self,  master, lakeshore, IDletter):
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.lakeshore = lakeshore
        self.ID = IDletter

        self.grid_columnconfigure(0, weight = 1)
        
        #Title Frame
        self.title_frame = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.title_frame.grid(row = 0, column = 0, sticky = 'ew')
        self.title_frame.grid_columnconfigure(0, weight = 1)
        self.head_lbl = tk.Label(self.title_frame, text = 'Input %s' % self.ID, font = ('tkDefaultFont', 24))
        self.head_lbl.grid(row = 0, column = 0, sticky = 'new')

        #Body Frame
        self.body_frame = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.body_frame.grid_columnconfigure(0, weight = 1)
        self.body_frame.grid_columnconfigure(1, weight = 1)
        self.body_frame.grid(row = 1, column = 0, sticky = 'nsew')
        #Sensor Type
        self.type_lbl = tk.Label(self.body_frame, text = 'Sensor Type and Range', font = ('tkDefaultFont', 16))
        self.type_lbl.grid(row = 1, column = 0, sticky = 'ew')
        self.type_str = tk.StringVar()
        self.type_list = ["Disabled","Diode 2.5 V (Silicon)", "Diode 10 V (GaAlAs)", "PTC RTD Autorange", "PTC RTD 10 Ohm", "PTC RTD 30 Ohm", "PTC RTD 100 Ohm",
                          "PTC RTD 300 Ohm", "PTC RTD 1 kOhm", "PTC RTD 3 kOhm", "PTC RTD 10 kOhm", "NTC RTD Autorange", "NTC RTD 10 Ohm", "NTC RTD 30 Ohm", 
                          "NTC RTD 100 Ohm", "NTC RTD 300 Ohm", "NTC RTD 1 kOhm", "NTC RTD 3 kOhm", "NTC RTD 10 kOhm", "NTC RTD 30 kOhm", "NTC RTD 100 kOhm", "Thermocouple"]
        self.type_str.set(self.type_list[0])
        self.type_menu = ttk.OptionMenu(self.body_frame, self.type_str, self.type_list[0], *self.type_list)
        self.type_menu.grid(row = 2, column = 0, sticky = 'ew')
        #Curve
        self.curve_lbl = tk.Label(self.body_frame, text = 'Sensor Type and Range', font = ('tkDefaultFont', 16))
        self.curve_lbl.grid(row = 1, column = 1, sticky = 'ew')
        self.curve_str = tk.StringVar()
        self.curve_list = ["DT-470", "DT-670", "DT-500-D", "DT-500-E1", "PT-100", "PT-1000", "RX-102A-AA", "RX-202A-AA", "Type K", "Type E", "Type T", "AuFe 0.03%", "AuFe 0.07%"]
        for k in range (21, 60):
            self.curve_list.append('User %d' % k)
        self.curve_str.set(self.curve_list[0])
        self.curve_menu = ttk.OptionMenu(self.body_frame, self.curve_str, self.curve_list[0], *self.curve_list)
        self.curve_menu.grid(row = 2, column = 1, sticky = 'ew')
        #Enable Compensation
        self.enablecomplbl = tk.Label(self.body_frame, text = 'Enable Compensation', font = ("tkDefaultFont",16))
        self.enablecomplbl.grid(row = 3, column = 1, sticky = 'ew')
        self.enablecompvar = tk.IntVar()
        self.enablecomptxtvar = tk.StringVar()
        self.enablecomptxtvar.set("Off")
        self.enablecompbox = tk.Checkbutton(self.body_frame, textvariable = self.enablecomptxtvar, variable = self.enablecompvar, command = lambda: self.updateenablecompbox())
        self.enablecompbox.grid(row = 4, column = 1)
        #Preferred Units
        self.preferredunitslbl = tk.Label(self.body_frame, text = 'Preferred Units', font = ("tkDefaultFont", 16))
        self.preferredunitslbl.grid(row = 3, column = 0, sticky = 'ew')
        self.preferredunitsstr = tk.StringVar()
        self.preferredunitslist = ['Kelvin', 'Celsius', 'Sensor Units'] #need to add +1 to the index
        self.preferredunitsstr.set(self.preferredunitslist[0])
        self.preferredunitsmenu = ttk.OptionMenu(self.body_frame, self.preferredunitsstr, self.preferredunitslist[0], *self.preferredunitslist)
        self.preferredunitsmenu.grid(row = 4, column = 0, sticky = 'ew')
        #Diode Current Units
        self.diodecurrentlbl = tk.Label(self.body_frame, text = 'Diode Current', font = ("tkDefaultFont", 16))
        self.diodecurrentlbl.grid(row = 5, column = 1, sticky = 'ew')
        self.diodecurrentstr = tk.StringVar()
        self.diodecurrentlist = ['10 uA', '1mA'] #need to add +1 to the index
        self.diodecurrentstr.set(self.diodecurrentlist[0])
        self.diodecurrentmenu = ttk.OptionMenu(self.body_frame, self.diodecurrentstr, self.diodecurrentlist[0], *self.diodecurrentlist)
        self.diodecurrentmenu.grid(row = 6, column = 1, sticky = 'ew')
        #Temperature Limit
        self.tlimitlbl = tk.Label(self.body_frame, text = 'Temperature Limit (K)', font = ("tkDefaultFont", 16))
        self.tlimitlbl.grid(row = 5, column = 0, sticky = 'ew')
        self.tlimitstr = tk.StringVar()
        self.tlimitstr.set('0')
        self.tlimitentry = tk.Entry(self.body_frame, textvariable = self.tlimitstr)
        self.tlimitentry.grid(row = 6, column = 0, sticky = 'ew')

        #Button Frame
        self.buttonframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.buttonframe.grid(row = 3, column = 0, columnspan = 3, sticky = 'new')
        self.buttonframe.grid_columnconfigure(0, weight = 1)
        self.buttonframe.grid_columnconfigure(1, weight = 1)
        self.buttonframe.grid_columnconfigure(2, weight = 1)
        self.buttonframe.grid_columnconfigure(3, weight = 1)
        self.configbtn = ttk.Button(self.buttonframe, text = 'Config Heater', command = lambda: self.configinput())
        self.configbtn.grid(row = 0, column = 0, sticky = 'nsew')
        self.querybtn = ttk.Button(self.buttonframe, text = 'Query Heater', command = lambda: self.queryinput())
        self.querybtn.grid(row = 0, column = 1, sticky = 'nsew')
        self.openbtn = ttk.Button(self.buttonframe, text = 'Open Config', command = lambda: self.openconfig())
        self.openbtn.grid(row = 0, column = 2, sticky = 'nsew')
        self.savebtn = ttk.Button(self.buttonframe, text = 'Save Config', command = lambda: self.saveconfig())
        self.savebtn.grid(row = 0, column = 3, sticky = 'nsew')

    def updateenablecompbox(self):
        if self.enablecompvar.get():#then powerup is enabled
            self.enablecomptxtvar.set("On ")
        else:
            self.enablecomptxtvar.set("Off")

    def configinput(self):
        return None

    def queryinput(self):
        return None
    
    def openconfig(self):
        return None

    def saveconfig(self):
        return None