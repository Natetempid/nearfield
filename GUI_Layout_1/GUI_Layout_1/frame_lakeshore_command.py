
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

class lakeshore_command_frame(tk.Frame):
    def __init__(self, master, controller, lakeshore):
        tk.Frame.__init__(self, master)
        self.lakeshore = lakeshore
        response_frame = tk.Frame(self)
        response_frame.pack(side = "top", fill = tk.BOTH, expand = True)
        
        self.v = tk.StringVar()
        self.response_label = tk.Label(response_frame, background = "white", textvariable = self.v)
        self.response_label.pack(side = "top", fill = "both", expand = True, padx = 5, pady = 5)
        entry_frame = tk.Frame(self)
        entry_frame.pack(side = "bottom")

        self.entry = tk.Entry(entry_frame, background = "white")
        self.entry.pack(side = "left", fill = "both", expand = True, padx = 5, pady = 5)





