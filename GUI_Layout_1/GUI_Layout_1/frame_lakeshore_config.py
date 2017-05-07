import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

from subframe_lakeshore_heater import heater_subframe


class lakeshore_config_frame(tk.Frame):
    def __init__(self,master,controller,lakeshore):
        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.lakeshore = lakeshore
       
        ##############
        ## Heater 1 ##
        ##############
        self.heaterframe1 = heater_subframe(self,self.lakeshore, 1)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe1.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        ###############
        ### Heater 2 ##
        ###############
        self.heaterframe2 = heater_subframe(self,self.lakeshore, 2)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe2.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        
        #self.heaterframe1.grid_columnconfigure(0, weight = 1)
        #self.heaterframe1.grid_columnconfigure(1, weight = 1)
        #self.heaterframe1.grid_columnconfigure(2, weight = 1)
        #self.lbl1 = tk.Label(self.heaterframe1, text = 'Heater 1', justify = tk.LEFT, font = ("tkDefaultFont",24))
        #self.lbl1.grid(row = 0, column = 0, rowspan = 2, columnspan = 2)
        ##Input Sensor
        #self.inputlbl1 = tk.Label(self.heaterframe1, text = 'Input Sensor', font = ("tkDefaultFont",18))
        #self.inputlbl1.grid(row = 0, column = 2)
        #self.inputstr1 = tk.StringVar()
        #self.inputstr1.set("None")
        #self.inputmenu1 = ttk.OptionMenu(self.heaterframe1, self.inputstr1, "None","A", "B")
        #self.inputmenu1.grid(row = 1, column = 2)
        ##Output Type
        #self.typelbl1 = tk.Label(self.heaterframe1, text = 'Output Type')
        #self.typelbl1.grid(row = 3, column = 0)
        #self.typestr1 = tk.StringVar()
        #self.typestr1.set("Current")
        #self.typemenu1 = ttk.OptionMenu(self.heaterframe1, self.typestr1, "Current", "Voltage")
        #self.typemenu1.grid(row = 4, column = 0)
        ##Polarity
        #self.polaritylbl1 = tk.Label(self.heaterframe1, text = 'Polarity')
        #self.polaritylbl1.grid(row = 3, column = 1)
        #self.polaritystr1 = tk.StringVar()
        #self.polaritystr1.set("Unipolar")
        #self.polaritymenu1 = ttk.OptionMenu(self.heaterframe1, self.polaritystr1, "Unipolar", "Bipolar") #this isn't the way to do a menu
        #self.polaritymenu1.grid(row = 4, column = 1)
        ##Heater Resistance
        #self.resistancelbl1 = tk.Label(self.heaterframe1, text = 'Heater Resistance')
        #self.resistancelbl1.grid(row = 3, column = 2)
        #self.resistancestr1 = tk.StringVar()
        #self.resistancestr1.set("25 Ohm")
        #self.resistancemenu1 = ttk.OptionMenu(self.heaterframe1, self.resistancestr1, "25 Ohm", "50 Ohm") #the lakshore number for 25 Ohm is 1 andfor 50 Ohm is 2,  even though it is the first element in the enum
        #self.resistancemenu1.grid(row = 4, column = 2)
        
        ###############
        ### Heater 2 ##
        ###############
        #self.heaterframe2 = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        #self.heaterframe2.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        #self.heaterframe2.grid_columnconfigure(0, weight = 1)
        #self.heaterframe2.grid_columnconfigure(1, weight = 1)
        #self.heaterframe2.grid_columnconfigure(2, weight = 1)
      
        ##title frame
        #self.titleframe2 = tk.Frame(self.heaterframe2, borderwidth = 5, relief = tk.GROOVE)
        #self.titleframe2.grid(row = 0, column = 0, columnspan = 3, sticky = 'ew')
        #self.titleframe2.grid_columnconfigure(0, weight = 1)
        #self.titleframe2.grid_columnconfigure(1, weight = 1)
        #self.titleframe2.grid_columnconfigure(2, weight = 1)
        #self.lbl2 = tk.Label(self.titleframe2, text = 'Heater 2', justify = tk.LEFT, font = ("tkDefaultFont",24))
        #self.lbl2.grid(row = 0, column = 0, rowspan = 2, columnspan = 2)
        ##Input Sensor
        #self.inputlbl2 = tk.Label(self.titleframe2, text = 'Input Sensor', font = ("tkDefaultFont",18))
        #self.inputlbl2.grid(row = 0, column = 2)
        #self.inputstr2 = tk.StringVar()
        #self.inputlist2 = ["A", "B"]
        #self.inputmenu2 = ttk.OptionMenu(self.titleframe2, self.inputstr2, self.inputlist2[1], *self.inputlist2)
        #self.inputmenu2.grid(row = 1, column = 2)

        ##Heater 2 Setup Frame
        #self.setupframe2 = tk.Frame(self.heaterframe2, borderwidth = 5, relief = tk.GROOVE)
        #self.setupframe2.grid(row = 2, column = 0, columnspan = 2, sticky = 'ew')
        #self.setupframe2.grid_columnconfigure(0, weight = 1)
        #self.setupframe2.grid_columnconfigure(1, weight = 1)
        ##Output Type
        #self.typelbl2 = tk.Label(self.setupframe2, text = 'Output Type', font = ("tkDefaultFont",16))
        #self.typelbl2.grid(row = 0, column = 0, sticky = 'ew')
        #self.typestr2 = tk.StringVar()
        #self.typelist2 = ["Current", "Voltage"]
        #self.typemenu2 = ttk.OptionMenu(self.setupframe2, self.typestr2, self.typelist2[0], *self.typelist2)
        #self.typemenu2.grid(row = 1, column = 0, sticky = 'ew')
        ##Polarity
        #self.polaritylbl2 = tk.Label(self.setupframe2, text = 'Polarity', font = ("tkDefaultFont",16))
        #self.polaritylbl2.grid(row = 0, column = 1, sticky = 'ew')
        #self.polaritystr2 = tk.StringVar()
        #self.polaritylist2 = ["Unipolar", "Bipolar"]
        #self.polaritymenu2 = ttk.OptionMenu(self.setupframe2, self.polaritystr2, self.polaritylist2[0], *self.polaritylist2) #this isn't the way to do a menu
        #self.polaritymenu2.grid(row = 1, column = 1, sticky = 'ew')
        ##Resistance
        #self.resistancelbl2 = tk.Label(self.setupframe2, text = 'Resistance', font = ("tkDefaultFont",16))
        #self.resistancelbl2.grid(row = 2, column = 0, sticky = 'ew')
        #self.resistancestr2 = tk.StringVar()
        #self.resistancelist2 = ["25 Ohm", "50 Ohm"]
        #self.resistancemenu2 = ttk.OptionMenu(self.setupframe2, self.resistancestr2, self.resistancelist2[1], *self.resistancelist2)
        #self.resistancemenu2.grid(row = 3, column = 0, sticky = 'ew')
        ##Max Current
        #self.maxcurrentlbl2 = tk.Label(self.setupframe2, text = 'Resistance', font = ("tkDefaultFont",16))
        #self.maxcurrentlbl2.grid(row = 2, column = 1, sticky = 'ew')
        #self.maxcurrentstr2 = tk.StringVar()
        #self.maxcurrentlist2 = ["User Specified", "0.707 A", "1 A", "1.141 A", "1.732 A"]
        #self.maxcurrentmenu2 = ttk.OptionMenu(self.setupframe2, self.maxcurrentstr2, self.maxcurrentlist2[0], *self.maxcurrentlist2)
        #self.maxcurrentmenu2.grid(row = 3, column = 1, sticky = 'ew')


