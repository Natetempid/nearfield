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

class heater_subframe(tk.Frame):
    def __init__(self, master, lakeshore, IDnumber):
        #master is program_frame
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.ID = IDnumber
        self.lakeshore = lakeshore

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        #Title frame
        self.titleframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.titleframe.grid(row = 0, column = 0, columnspan = 3, sticky = 'ew')
        self.titleframe.grid_columnconfigure(0, weight = 1)
        self.titleframe.grid_columnconfigure(1, weight = 1)
        self.titleframe.grid_columnconfigure(2, weight = 1)
        self.titleframe.grid_columnconfigure(3, weight = 1)
        self.lbl2 = tk.Label(self.titleframe, text = 'Heater %d' % self.ID, justify = tk.LEFT, font = ("tkDefaultFont",24))
        self.lbl2.grid(row = 0, column = 0, rowspan = 2, columnspan = 2)
        #Input Sensor
        self.inputlbl = tk.Label(self.titleframe, text = 'Input Sensor', font = ("tkDefaultFont",18))
        self.inputlbl.grid(row = 0, column = 2)
        self.inputstr = tk.StringVar()
        self.inputlist = ["A", "B"]
        self.inputstr.set(self.inputlist[0])
        self.inputmenu = ttk.OptionMenu(self.titleframe, self.inputstr, self.inputlist[0], *self.inputlist)
        self.inputmenu.grid(row = 1, column = 2)

        #Heater Setup Frame
        self.setupframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.setupframe.grid(row = 2, column = 0, columnspan = 2, sticky = 'nsew')
        self.setupframe.grid_columnconfigure(0, weight = 1)
        self.setupframe.grid_columnconfigure(1, weight = 1)
        #Output Type
        self.typelbl = tk.Label(self.setupframe, text = 'Output Type', font = ("tkDefaultFont",16))
        self.typelbl.grid(row = 0, column = 0, sticky = 'ew')
        self.typestr = tk.StringVar()
        self.typelist = ["Current", "Voltage"]
        self.typestr.set(self.typelist[0])
        self.typemenu = ttk.OptionMenu(self.setupframe, self.typestr, self.typelist[0], *self.typelist)
        self.typemenu.grid(row = 1, column = 0, sticky = 'ew')
        #Polarity
        self.polaritylbl = tk.Label(self.setupframe, text = 'Polarity', font = ("tkDefaultFont",16))
        self.polaritylbl.grid(row = 0, column = 1, sticky = 'ew')
        self.polaritystr = tk.StringVar()
        self.polaritylist = ["Unipolar", "Bipolar"]
        self.polaritystr.set(self.polaritylist[0])
        self.polaritymenu = ttk.OptionMenu(self.setupframe, self.polaritystr, self.polaritylist[0], *self.polaritylist)
        self.polaritymenu.grid(row = 1, column = 1, sticky = 'ew')
        #Resistance
        self.resistancelbl = tk.Label(self.setupframe, text = 'Resistance', font = ("tkDefaultFont",16))
        self.resistancelbl.grid(row = 2, column = 0, sticky = 'ew')
        self.resistancestr = tk.StringVar()
        self.resistancelist = ["25 Ohm", "50 Ohm"]
        self.resistancestr.set(self.resistancelist[1])
        self.resistancemenu = ttk.OptionMenu(self.setupframe, self.resistancestr, self.resistancelist[1], *self.resistancelist)
        self.resistancemenu.grid(row = 3, column = 0, sticky = 'ew')
        #Feedback Mode
        self.modelbl = tk.Label(self.setupframe, text = 'Mode', font = ("tkDefaultFont",16))
        self.modelbl.grid(row = 2, column = 1, sticky = 'ew')
        self.modestr = tk.StringVar()
        self.modelist = ["Off", "Closed Loop PID", "Zone", "Open Loop", "Monitor Out", "Warmup Supply"]
        self.modestr.set(self.modelist[0])
        self.modemenu = ttk.OptionMenu(self.setupframe, self.modestr, self.modelist[0], *self.modelist)
        self.modemenu.grid(row = 3, column = 1, sticky = 'ew')
        #Max Current
        self.maxcurrentlbl = tk.Label(self.setupframe, text = 'Max Current', font = ("tkDefaultFont",16))
        self.maxcurrentlbl.grid(row = 4, column = 0, sticky = 'ew')
        self.maxcurrentstr = tk.StringVar()
        self.maxcurrentlist = ["User Specified", "0.707 A", "1 A", "1.141 A", "1.732 A"]
        self.maxcurrentstr.set(self.maxcurrentlist[0])
        self.maxcurrentmenu = ttk.OptionMenu(self.setupframe, self.maxcurrentstr, self.maxcurrentlist[0], *self.maxcurrentlist)
        self.maxcurrentmenu.grid(row = 5, column = 0, sticky = 'ew')
        #Power Up Enable
        self.poweruplbl = tk.Label(self.setupframe, text = 'Power Up Enable', font = ("tkDefaultFont",16))
        self.poweruplbl.grid(row = 4, column = 1, sticky = 'ew')
        self.powerupvar = tk.IntVar()
        self.poweruptxtvar = tk.StringVar()
        self.poweruptxtvar.set("Off")
        self.powerupbox = tk.Checkbutton(self.setupframe, textvariable = self.poweruptxtvar, variable = self.powerupvar, command = lambda: self.updatepowerupbox())
        self.powerupbox.grid(row = 5, column = 1)
        #Max User Current
        self.maxuserlbl = tk.Label(self.setupframe, text = 'Max User Current', font = ("tkDefaultFont",16)) 
        self.maxuserlbl.grid(row = 6, column = 0, sticky = 'ew')
        self.maxuserstr = tk.StringVar()
        self.maxuserstr.set("0")
        self.maxuserentry = tk.Entry(self.setupframe, textvariable = self.maxuserstr, width = 20)
        self.maxuserfloat = float(self.maxuserstr.get())
        self.maxuserentry.grid(row = 7, column = 0)
        #Heater Output Type
        self.heateroutputlbl = tk.Label(self.setupframe, text = 'Heater Output Type', font = ("tkDefaultFont",16))
        self.heateroutputlbl.grid(row = 6, column = 1, sticky = 'ew')
        self.heateroutputstr = tk.StringVar()
        self.heateroutputlist = ["Current", "Power"]
        self.heateroutputstr.set(self.heateroutputlist[0])
        self.heateroutputmenu = ttk.OptionMenu(self.setupframe, self.heateroutputstr, self.heateroutputlist[0], *self.heateroutputlist)#Current is for enum #1 not 0
        self.heateroutputmenu.grid(row = 7, column = 1, sticky = 'ew')

        #PID Frame
        self.pidframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.pidframe.grid(row = 2, column = 2, sticky = 'new')
        self.pidframe.grid_columnconfigure(0, weight = 1)
        self.pidframe.grid_columnconfigure(1, weight = 1)
        #Gain - P
        self.plbl = tk.Label(self.pidframe, text = 'Gain (P) (50.0)', font = ("tkDefaultFont",16)) 
        self.plbl.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        self.pstr = tk.StringVar()
        self.pstr.set("50.0")
        self.pentry = tk.Entry(self.pidframe, textvariable = self.pstr, width = 20)
        self.pfloat = float(self.pstr.get())
        self.pentry.grid(row = 1, column = 0, columnspan = 2)
        #Reset - I
        self.ilbl = tk.Label(self.pidframe, text = 'Reset (I) (20.0)', font = ("tkDefaultFont",16)) 
        self.ilbl.grid(row = 2, column = 0, columnspan = 2, sticky = 'ew')
        self.istr = tk.StringVar()
        self.istr.set("20.0")
        self.ientry = tk.Entry(self.pidframe, textvariable = self.istr, width = 20)
        self.ifloat = float(self.istr.get())
        self.ientry.grid(row = 3, column = 0, columnspan = 2)
        #Rate - D
        self.dlbl = tk.Label(self.pidframe, text = 'Rate (D) (0.0 %)', font = ("tkDefaultFont",16)) 
        self.dlbl.grid(row = 4, column = 0, columnspan = 2, sticky = 'ew')
        self.dstr = tk.StringVar()
        self.dstr.set("0.0")
        self.dentry = tk.Entry(self.pidframe, textvariable = self.dstr, width = 20)
        self.dfloat = float(self.dstr.get())
        self.dentry.grid(row = 5, column = 0, columnspan = 2)
        #Setpoint
        self.setptlbl = tk.Label(self.pidframe, text = 'Setpoint (K)', font = ("tkDefaultFont",16)) 
        self.setptlbl.grid(row = 6, column = 0, columnspan = 2, sticky = 'ew')
        self.setptstr = tk.StringVar()
        self.setptstr.set("0.0000")
        self.setptentry = tk.Entry(self.pidframe, textvariable = self.setptstr, width = 20)
        self.setptfloat = float(self.setptstr.get())
        self.setptentry.grid(row = 7, column = 0, columnspan = 2)
        #Setpoint Ramping
        self.setptramplbl = tk.Label(self.pidframe, text = 'Setpoint Ramping', font = ("tkDefaultFont",16))
        self.setptramplbl.grid(row = 10, column = 0, sticky = 'ew')
        self.setptrampvar = tk.IntVar()
        self.setptramptxtvar = tk.StringVar()
        self.setptramptxtvar.set("Off")
        self.setptrampbox = tk.Checkbutton(self.pidframe, textvariable = self.setptramptxtvar, variable = self.setptrampvar, command = lambda: self.updatesetptrampbox())
        self.setptrampbox.grid(row = 10, column = 1)
        #Setpoint Ramp Rate
        self.setptratelbl = tk.Label(self.pidframe, text = 'Setpoint Ramp Rate', font = ("tkDefaultFont",16)) 
        self.setptratelbl.grid(row = 8, column = 0, columnspan = 2, sticky = 'ew')
        self.setptratestr = tk.StringVar()
        self.setptratestr.set("0.0")
        self.setptrateentry = tk.Entry(self.pidframe, textvariable = self.setptratestr, width = 20)
        self.setptratefloat = float(self.setptratestr.get())
        self.setptrateentry.grid(row = 9, column = 0, columnspan = 2)

        #Button Frame
        self.buttonframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.buttonframe.grid(row = 3, column = 0, columnspan = 3, sticky = 'new')
        self.buttonframe.grid_columnconfigure(0, weight = 1)
        self.buttonframe.grid_columnconfigure(1, weight = 1)
        self.buttonframe.grid_columnconfigure(2, weight = 1)
        self.buttonframe.grid_columnconfigure(3, weight = 1)
        self.configbtn = ttk.Button(self.buttonframe, text = 'Config Heater', command = lambda: self.configheater())
        self.configbtn.grid(row = 0, column = 0, sticky = 'nsew')
        self.querybtn = ttk.Button(self.buttonframe, text = 'Query Heater', command = lambda: self.queryheater())
        self.querybtn.grid(row = 0, column = 1, sticky = 'nsew')
        self.openbtn = ttk.Button(self.buttonframe, text = 'Open Config', command = lambda: self.openconfig())
        self.openbtn.grid(row = 0, column = 2, sticky = 'nsew')
        self.savebtn = ttk.Button(self.buttonframe, text = 'Save Config', command = lambda: self.saveconfig())
        self.savebtn.grid(row = 0, column = 3, sticky = 'nsew')
        
        #Heater On/Off Frame
        self.onoffframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.onoffframe.grid(row = 4, column = 0, columnspan = 3, sticky = 'new')
        #self.onoffframe.grid_columnconfigure(0,weight = 1)
        self.onoffframe.grid_columnconfigure(1,weight = 1)
        self.onoffframe.grid_columnconfigure(2,weight = 1)
        self.onoffframe.grid_columnconfigure(3,weight = 1)
        self.rangelabel = tk.Label(self.onoffframe, text = 'Heater Power', font = ("tkDefaultFont", 16))
        self.rangelabel.grid(row = 0, column = 2, sticky = 'ew')
        self.heaterrange_list = ['Off', 'Low', 'Medium', 'High']
        self.heaterrange_str = tk.StringVar()
        self.heaterrange_str.set(self.heaterrange_list[0])
        self.heaterrange = ttk.OptionMenu(self.onoffframe, self.heaterrange_str, self.heaterrange_list[0], *self.heaterrange_list)
        self.heaterrange.grid(row = 1, column = 2, sticky = 'ew')
        self.indicator_canvas = tk.Canvas(self.onoffframe, width = 100, height = 100)
        self.indicator_canvas.grid(row = 0, column = 0, rowspan = 2, sticky = 'ns')
        self.indicator = self.indicator_canvas.create_oval(10,10,80,80, fill = 'red4')
        self.scale = tk.Scale(self.onoffframe, from_=3, to=0, troughcolor = 'red', relief = tk.SUNKEN, tickinterval = 1, width = 30, state = tk.DISABLED)
        self.scale.set(self.heaterrange_list.index(self.heaterrange_str.get()))
        self.scale.grid(row = 0, column = 1, rowspan = 2, sticky = 'ns')
        
        
        self.onbtn = ttk.Button(self.onoffframe, text = 'Go', command = lambda: self.heatergo())
        self.onbtn.grid(row = 0, column = 3, rowspan = 2, sticky = 'nsew')


    def updatepowerupbox(self):
        if self.powerupvar.get():#then powerup is enabled
            self.poweruptxtvar.set("On ")
        else:
            self.poweruptxtvar.set("Off")
    def updatesetptrampbox(self):
        if self.setptrampvar.get():#then powerup is enabled
            self.setptramptxtvar.set("On ")
        else:
            self.setptramptxtvar.set("Off")
    
    #########################
    ## Get Heater Instance ##
    #########################

    def get_heater(self):
        if self.ID == 1:
            return self.lakeshore.heater1
        elif self.ID == 2:
            return self.lakeshore.heater2
        else:
            self.master.master.master.frames[lakeshore_command_frame].response_txt.insert(tk.END, "[ERROR %s]: LakeShore heater ID is neither 1 nor 2\n" % str(datetime.datetime.now().time().strftime("%H:%M:%S")))
            #this sends the command to the command prompt frame
            #First master is the lakeshore_measure_frame
            #second master is the container frame in GUI_Layout
            #Third master is the GraphTk instance, which has the frames property
            return None
    
    ###################
    ## Config Heater ##
    ###################

    def assignvalues2heater(self, heater):
        #Output
        heater.mode = self.modelist.index(self.modestr.get())
        heater.input = self.inputlist.index(self.inputstr.get()) + 1 #Input A is 1 and Input B is 2
        heater.powerupenable = self.powerupvar.get()
        #Polarity
        heater.outputtype = self.typelist.index(self.typestr.get())
        heater.polarity = self.polaritylist.index(self.polaritystr.get())
        #Heater Setup
        heater.type = self.typelist.index(self.typestr.get())
        heater.resistance = self.resistancelist.index(self.resistancestr.get()) + 1
        heater.maxcurrent = self.maxcurrentlist.index(self.maxcurrentstr.get())
        heater.maxusercurrent = self.maxuserfloat
        heater.iorw = self.heateroutputlist.index(self.heateroutputstr.get()) + 1 #current is 1 and voltage is 2
        #PID
        heater.p = float(self.pstr.get())
        heater.i = float(self.istr.get())
        heater.d = float(self.dstr.get())
        #Setpoint
        heater.setpoint = float(self.setptstr.get())#self.setptfloat
        heater.setpointramp = float(self.setptratestr.get())
        heater.setpointrampenable = self.setptrampvar.get() 

    def configheater(self):
        self.configbtn.config(state =  tk.DISABLED)
        if self.lakeshore.thread_active:
            #then temperature and output current are being measured and the thread needs to be paused
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #stops the measurement
            while self.lakeshore.thread_active:
                #ask if the thread has truly stopped
                time.sleep(0.002)
            heater = self.get_heater()
            self.assignvalues2heater(heater)
            heater.config()
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #restarts the measurement
        else:
            time.sleep(0.002)
            heater = self.get_heater()
            self.assignvalues2heater(heater)
            heater.config()
        self.configbtn.config(state = tk.NORMAL)
    ##################
    ## Query Heater ##
    ##################

    def queryheater(self):
        self.querybtn.config(state = tk.DISABLED)
        if self.lakeshore.thread_active: #then measurement is running
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #end measurement
            while self.lakeshore.thread_active:
                time.sleep(0.002)
            heater = self.get_heater()
            heater.query()
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #restarts the measurement
        else:
            time.sleep(0.002)
            heater = self.get_heater()
            heater.query()
        self.update_heatframe(heater)
        self.querybtn.config(state = tk.NORMAL)

    def update_heatframe(self, heater):       
        #Output
        self.modestr.set(self.modelist[heater.mode])
        self.inputstr.set(self.inputlist[heater.input - 1])
        self.powerupvar.set(heater.powerupenable)
        self.updatepowerupbox()
        #Polarity
        self.typestr.set(self.typelist[heater.type])
        self.polaritystr.set(self.polaritylist[heater.polarity])
        #Heater Setup
        self.resistancestr.set(self.resistancelist[heater.resistance - 1])
        self.maxcurrentstr.set(self.maxcurrentlist[heater.maxcurrent])
        self.maxuserstr.set(str(heater.maxusercurrent))
        self.heateroutputstr.set(self.heateroutputlist[heater.iorw - 1])
        #PID
        self.pstr.set(str(heater.p))
        self.istr.set(str(heater.i))
        self.dstr.set(str(heater.d))
        #Setpoint
        self.setptstr.set(str(heater.setpoint))
        self.setptratestr.set(str(heater.setpointramp))
        self.setptrampvar.set(heater.setpointrampenable)
        self.updatesetptrampbox()
      
    ########################
    ## Turn Heater On/Off ##
    ########################
            
    def heatergo(self):
        #get heater values
        heater = self.get_heater()
        heater.range = self.heaterrange_list.index(self.heaterrange_str.get())

        #disable putting
        self.onbtn.config(state = tk.DISABLED)
        #check if measurement is ongoing
        if self.master.master.master.frames[lakeshore_measure_frame].running:
            #then temperature and output current are being measured and the thread needs to be paused
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #stops the measurement
            while not( self.lakeshore.stop_event.is_set()):
                #ask if the thread has truly stopped
                time.sleep(0.001)
            heater.set_range()
            time.sleep(0.002)
            heater_status = heater.query_range()
            self.master.master.master.frames[lakeshore_measure_frame].on_click() #restarts the measurement
        else:
            heater.set_range()
            time.sleep(0.002)
            heater_status = heater.query_range()
        self.onbtn.config(state = tk.NORMAL)

        if heater_status > 0: #then the heater is on
            #change indicator oval
            self.indicator_canvas.itemconfig(self.indicator, fill = "green2")
            #change button to stop
            self.onbtn.config(text = "Stop")
        else: #then heater is off
            self.indicator_canvas.itemconfig(self.indicator, foreground = "red4")
            self.onbtn.config(text = "Go")
        



    ########################
    ## Save Heater Object ##
    ########################

    def saveconfig(self):
        #get all values from widgets in frames above
        config_str = [self.inputstr.get(),
        self.typestr.get(),
        self.polaritystr.get(),
        self.resistancestr.get(),
        self.modestr.get(),
        self.maxcurrentstr.get(),
        self.powerupvar.get(),
        self.maxuserstr.get(),
        self.heateroutputstr.get(),
        self.pstr.get(),
        self.istr.get(),
        self.dstr.get(),
        self.setptstr.get(),
        self.setptrampvar.get(),
        self.setptratestr.get()]
        today = datetime.date.today().strftime('%Y%m%d')
        config_name = 'heater_%d_%s' % (self.ID, today)
        f = tkFileDialog.asksaveasfile(mode = 'w', initialdir = 'heater_config', initialfile = config_name, defaultextension = '.dat')
        for str_elem in config_str:
            f.write('%s\n' % str_elem)
        return None

    ########################
    ## Open Heater Object ##
    ########################

    def openconfig(self):
        f = tkFileDialog.askopenfile(initialdir = 'heater_config', defaultextension = '.dat')
        property_list = []
        for line in f:
            property_list.append(line.strip('\n'))
        widget_list = [self.inputstr,
        self.typestr,
        self.polaritystr,
        self.resistancestr,
        self.modestr,
        self.maxcurrentstr,
        self.powerupvar,
        self.maxuserstr,
        self.heateroutputstr,
        self.pstr,
        self.istr,
        self.dstr,
        self.setptstr,
        self.setptrampvar,
        self.setptratestr]

        if len(property_list) is len(widget_list):
            for i in range(0,len(property_list)):
                widget_list[i].set(property_list[i])