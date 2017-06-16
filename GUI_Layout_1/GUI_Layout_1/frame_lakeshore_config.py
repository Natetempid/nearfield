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
        self.controller = controller
       
        ##############
        ## Heater 1 ##
        ##############
        self.heaterframe1 = heater_subframe(self, self.controller, self.lakeshore, 1)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe1.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        ###############
        ### Heater 2 ##
        ###############
        self.heaterframe2 = heater_subframe(self, self.controller, self.lakeshore, 2)#tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.heaterframe2.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
