import Tkinter as tk
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
from lakeshore335 import heater
from subframe_lakeshore_input import input_subframe
import time

class lakeshore_input_frame(tk.Frame):
    def __init__(self, master, controller, lakeshore):
        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.lakeshore = lakeshore
       
        #############
        ## Input A ##
        #############
        self.inputframeA = input_subframe(self, self.lakeshore, 'A')#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.inputframeA.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        ##############
        ### Input B ##
        ##############
        self.inputframeB = input_subframe(self, self.lakeshore, 'B')#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.inputframeB.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)