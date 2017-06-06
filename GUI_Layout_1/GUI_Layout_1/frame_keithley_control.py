import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import threading

class keithley_control_frame(tk.Frame):
    def __init__(self,master,controller, keithley):
        tk.Frame.__init__(self,master)       
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        #self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(1,weight=1)

        self.master = master
        self.keithley = keithley

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
        self.voltageframe = tk.Frame(self.leftframe, borderwidth = 5, relief = tk.GROOVE)
        self.voltageframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.voltageframe.grid_rowconfigure(0,weight=1)
        self.voltageframe.grid_columnconfigure(0,weight=1)
        #right frame
        self.rightframe = tk.Frame(self)
        self.rightframe.grid_rowconfigure(0,weight=1)
        self.rightframe.grid_rowconfigure(1,weight=1)
        self.rightframe.grid_columnconfigure(0,weight=1)
        self.rightframe.grid(row=0,column=1,sticky='nsew')
        self.currentframe = tk.Frame(self.rightframe, borderwidth = 5, relief = tk.GROOVE)
        self.currentframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.resistanceframe = tk.Frame(self.rightframe, borderwidth = 5, relief = tk.GROOVE)
        self.resistanceframe.grid(row = 1, column = 0, sticky = 'nsew')

        #Voltage Control
        self.voltagestartlbl = tk.Label(self.controlframe,text = "Voltage Ramp Start", font = ("tkDefaultFont",18))
        self.voltagestartlbl.grid(row = 0, column = 0, sticky = 'nsw')
        self.voltagestartstr = tk.StringVar()
        self.voltagestartstr.set('0')
        self.voltagestartentry = tk.Entry(self.controlframe, textvariable = self.voltagestartstr)
        self.voltagestartentry.grid(row = 1, column = 0, sticky = 'nsw')

        self.voltageendlbl = tk.Label(self.controlframe,text = "Voltage Ramp End", font = ("tkDefaultFont",18))
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

        self.startbtn = tk.Button(self.controlframe, text = "Start Ramp", font = ("tkDefaultFont",14), background = "green4", command = lambda: self.startramp())
        self.startbtn.grid(row = 2, column = 0, sticky = 'nsew', padx = 5, pady = 5)

        self.abortbtn = tk.Button(self.controlframe, text = "Abort Ramp", font = ("tkDefaultFont",14), foreground = "white", background = "red", command = lambda: self.abortramp())
        self.abortbtn.grid(row = 2, column = 2, sticky = 'nsew', padx = 5, pady = 5)

        #graphs
        self.fig1 = plt.Figure(figsize=(5,5))
        self.ax1 = self.fig1.add_subplot(1,1,1)
        self.ax1.set_title('Applied Bias')
        self.line1, = self.ax1.plot([], [], color='r')
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.voltageframe)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas1._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)