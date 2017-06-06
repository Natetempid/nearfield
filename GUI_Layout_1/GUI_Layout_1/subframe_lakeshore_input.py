import Tkinter as tk
import tkFileDialog
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
from frame_instrument_command import instrument_command_frame
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
        self.curve_list = ["None", "DT-470", "DT-670", "DT-500-D", "DT-500-E1", "Reserved", "PT-100", "PT-1000", "RX-102A-AA", 
                           "RX-202A-AA", "Reserved", "Reserved", "Type K", "Type E", "Type T", "AuFe 0.03%", "AuFe 0.07%"]
        #for k in range (21, 60):
        #   self.curve_list.append('User %d' % k)
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
        self.configbtn = ttk.Button(self.buttonframe, text = 'Config Input', command = lambda: self.configinput())
        self.configbtn.grid(row = 0, column = 0, sticky = 'nsew')
        self.querybtn = ttk.Button(self.buttonframe, text = 'Query Input', command = lambda: self.queryinput())
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
        self.configbtn.config(state = tk.DISABLED)
        input = self.get_input()
        #Intype
        input.type_str = self.type_str.get()
        input.typestr2nums() #sets type, autorange and range
        input.compensation = self.enablecompvar.get()
        input.units = self.preferredunitslist.index(self.preferredunitsstr.get()) + 1
        #DIOCUR
        input.diodecurrent = self.diodecurrentlist.index(self.diodecurrentstr.get())
        #INCRV
        input.curve_str = self.curve_str.get()
        input.curve = self.curve_list.index(self.curve_str.get())
        #TLIMIT
        input.tlimit = float(self.tlimitstr.get())
        if self.master.master.master.frames[lakeshore_measure_frame].running:
            tkMessageBox.showwarning('Warning', 'Cannot configure input while measurement is running')
        else:
            input.config()
        self.configbtn.config(state = tk.NORMAL)

    def queryinput(self):
        self.querybtn.config(state = tk.DISABLED)
        input = self.get_input()
        if self.master.master.master.frames[lakeshore_measure_frame].running:
            #then temperature and output current are being measured and the thread needs to be paused
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #stops the measurement
            while (not self.lakeshore.stop_event.is_set()):
                #waits for ehe thread to truly stop
                time.sleep(0.001)
            time.sleep(0.002)
            input.query()
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #restarts the measurement
        else:
            input.query()
        input.curve_str = self.curve_list[input.curve]
        self.update_inputframe(input)
        self.querybtn.config(state = tk.NORMAL)

    def update_inputframe(self, input):
        self.type_str.set(input.type_str) #this string value has been set in the input.query command
        self.curve_str.set(input.curve_str) #this string was establish in the self.queryinput command
        self.enablecompvar.set(input.compensation)
        self.updateenablecompbox()
        self.preferredunitsstr.set(self.preferredunitslist[input.units - 1])
        self.diodecurrentstr.set(self.diodecurrentlist[input.diodecurrent])
        self.tlimitstr.set(str(input.tlimit))     


    def openconfig(self):
        f = tkFileDialog.askopenfile(initialdir = 'input_config', defaultextension = '.dat')
        property_list = []
        for line in f:
            property_list.append(line.strip('\n'))
        widget_list = [self.type_str,
                      self.curve_str,
                      self.enablecompvar,
                      self.preferredunitsstr,
                      self.diodecurrentstr,
                      self.tlimitstr]

        if len(property_list) is len(widget_list):
            for i in range(0,len(property_list)):
                widget_list[i].set(property_list[i])
        self.updateenablecompbox()

    def saveconfig(self):
        #get all values from widgets in frames above
        config_str = [self.type_str.get(),
                      self.curve_str.get(),
                      self.enablecompvar.get(),
                      self.preferredunitsstr.get(),
                      self.diodecurrentstr.get(),
                      self.tlimitstr.get()]
        today = datetime.date.today().strftime('%Y%m%d')
        config_name = 'input_%s_%s' % (self.ID, today)
        f = tkFileDialog.asksaveasfile(mode = 'w', initialdir = 'input_config', initialfile = config_name, defaultextension = '.dat')
        for str_elem in config_str:
            f.write('%s\n' % str_elem)
        return None

    def get_input(self):
        if self.ID == 'A':
            return self.lakeshore.inputA
        elif self.ID == 'B':
            return self.lakeshore.inputB
        else:
            self.master.master.master.frames[instrument_command_frame].response_txt.insert(tk.END, "[ERROR %s]: LakeShore input ID is neither A nor B\n" % str(datetime.datetime.now().time().strftime("%H:%M:%S")))
            #this sends the command to the command prompt frame
            #First master is the lakeshore_measure_frame
            #second master is the container frame in GUI_Layout
            #Third master is the GraphTk instance, which has the frames property
            return None