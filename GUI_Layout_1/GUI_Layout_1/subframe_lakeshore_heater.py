import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
from frame_lakeshore_command import lakeshore_command_frame


class heater_subframe(tk.Frame):
    def __init__(self, master, lakeshore, IDnumber):
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.ID = IDnumber

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
        self.inputmenu = ttk.OptionMenu(self.titleframe, self.inputstr, self.inputlist[1], *self.inputlist)
        self.inputmenu.grid(row = 1, column = 2)

        #Heater 2 Setup Frame
        self.setupframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.setupframe.grid(row = 2, column = 0, columnspan = 2, sticky = 'nsew')
        self.setupframe.grid_columnconfigure(0, weight = 1)
        self.setupframe.grid_columnconfigure(1, weight = 1)
        #Output Type
        self.typelbl = tk.Label(self.setupframe, text = 'Output Type', font = ("tkDefaultFont",16))
        self.typelbl.grid(row = 0, column = 0, sticky = 'ew')
        self.typestr = tk.StringVar()
        self.typelist = ["Current", "Voltage"]
        self.typemenu = ttk.OptionMenu(self.setupframe, self.typestr, self.typelist[0], *self.typelist)
        self.typemenu.grid(row = 1, column = 0, sticky = 'ew')
        #Polarity
        self.polaritylbl = tk.Label(self.setupframe, text = 'Polarity', font = ("tkDefaultFont",16))
        self.polaritylbl.grid(row = 0, column = 1, sticky = 'ew')
        self.polaritystr = tk.StringVar()
        self.polaritylist = ["Unipolar", "Bipolar"]
        self.polaritymenu = ttk.OptionMenu(self.setupframe, self.polaritystr, self.polaritylist[0], *self.polaritylist) #this isn't the way to do a menu
        self.polaritymenu.grid(row = 1, column = 1, sticky = 'ew')
        #Resistance
        self.resistancelbl = tk.Label(self.setupframe, text = 'Resistance', font = ("tkDefaultFont",16))
        self.resistancelbl.grid(row = 2, column = 0, sticky = 'ew')
        self.resistancestr = tk.StringVar()
        self.resistancelist = ["25 Ohm", "50 Ohm"]
        self.resistancemenu = ttk.OptionMenu(self.setupframe, self.resistancestr, self.resistancelist[1], *self.resistancelist)
        self.resistancemenu.grid(row = 3, column = 0, sticky = 'ew')
        #Feedback Mode
        self.modelbl = tk.Label(self.setupframe, text = 'Mode', font = ("tkDefaultFont",16))
        self.modelbl.grid(row = 2, column = 1, sticky = 'ew')
        self.modestr = tk.StringVar()
        self.modelist = ["Off", "Closed Loop PID", "Zone", "Open Loop", "Monitor Out", "Warmup Supply"]
        self.modemenu = ttk.OptionMenu(self.setupframe, self.modestr, self.modelist[0], *self.modelist)
        self.modemenu.grid(row = 3, column = 1, sticky = 'ew')
        #Max Current
        self.maxcurrentlbl = tk.Label(self.setupframe, text = 'Max Current', font = ("tkDefaultFont",16))
        self.maxcurrentlbl.grid(row = 4, column = 0, sticky = 'ew')
        self.maxcurrentstr = tk.StringVar()
        self.maxcurrentlist = ["User Specified", "0.707 A", "1 A", "1.141 A", "1.732 A"]
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
        self.configbtn = ttk.Button(self.buttonframe, text = 'Config Heater', command = lambda: self.configheater())
        self.configbtn.grid(row = 0, column = 0, sticky = 'nsew')
       #str = self.getcommandstr()
       # print str
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
    
    def getcommandstr(self):
        #commands to send lakeshore are OUTMODE, POLARITY, HTRSET, PID
        #Outmode - need output mode, input, and power up enable=
        mode = self.modelist.index(self.modestr)
        input = self.inputlist.index(self.inputstr)
        powerupenable = self.powerupvar.get()
        outmodestr = 'OUTMODE %d,%d,%d,%d;' % (self.ID, mode, input, powerupenable)

        #Only setup polarity if heater output == 2 and  outputtype is voltage (this won't happen often, since output is usually current)

    def configheater(self):
        command_str = self.getcommandstr()
        #if this is heater frame 1 get heater frame 1, else get heater frame 2

        if self.ID == 1:
            self.lakeshore.heater1.ctrl.write(command_str)
        elif self.ID == 2:
            self.lakeshore.heater2.ctrl.write(command_str)
        else:
            self.master.master.frames[lakeshore_command_frame].response_txt.insert(tk.END, "[ERROR %s]: LakeShore heater ID is greater than 2\n" % str(datetime.datetime.now().time().strftime("%H:%M:%S")))
            #this sends the command to the command prompt frame
            #First master is the lakeshore_measure_frame
            #second master is the container frame in GUI_Layout
            #Third master is the GraphTk instance, which has the frames property
                          

    


