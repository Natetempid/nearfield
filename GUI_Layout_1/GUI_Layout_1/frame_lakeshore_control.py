import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

from subframe_lakeshore_heater import heater_subframe
from subframe_lakeshore_input import input_subframe

class lakeshore_control_frame(tk.Frame):
    def __init__(self,master,controller,lakeshore):
        tk.Frame.__init__(self,master)
        self.lakeshore = lakeshore
        self.controller = controller

        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1,weight=1)

        #config frames
        ##############
        ## Heater 1 ##
        ##############
        self.heaterframe1 = heater_subframe(self, self.controller, self.lakeshore, 1)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe1.grid(row=0, column=0, sticky='nsew')

        ###############
        ### Heater 2 ##
        ###############
        self.heaterframe2 = heater_subframe(self, self.controller, self.lakeshore, 2)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe2.grid(row = 0, column = 1, sticky = 'nsew')

        #input frames
        #############
        ## Input A ##
        #############
        self.inputframeA = input_subframe(self, self.controller, self.lakeshore, 'A')#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.inputframeA.grid(row = 1, column = 0, sticky = 'nsew')

        ##############
        ### Input B ##
        ##############
        self.inputframeB = input_subframe(self, self.controller, self.lakeshore, 'B')#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.inputframeB.grid(row = 1, column = 1, sticky = 'nsew')


