
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
from lakeshore335 import lakeshore335
from frame_lakeshore_measure import lakeshore_measure_frame
from frame_lakeshore_command import lakeshore_command_frame
import ttk

lkshr = lakeshore335('ASRL3::INSTR')

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #create button frame to controller pages
        btnmenu = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        btnmenu.pack(side = "left", fill = "both", padx = 5, pady = 5)
        
        container = tk.Frame(self)
        container.pack(side="right", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        #container.grid_rowconfigure(1, weight=1)
        #container.grid_columnconfigure(1, weight=1)
        #container.grid_rowconfigure(2, weight=1)
        #container.grid_columnconfigure(2, weight=1)

        #self.frames = {}

        #frm_lkshrmeasure = lakeshore_measure_frame(container, self, lkshr)
        #frm_lkshrcommand = lakeshore_command_frame(container, self, lkshr)

        #frame.grid(row=0, column=0, sticky="nsew")
        #frm_lkshrmeasure.pack(padx = 5, pady = 5)
        #frm_lkshrcommand.pack(padx = 5, pady = 5)
        #self.frm_lkshrcommand.tkraise()

        btn_p1 = tk.Button(btnmenu, text = "LakeShore Measure", command= lambda: self.show_frame(lakeshore_measure_frame), width = 30)
        btn_p1.grid(row = 0, column = 0)
        btn_p2 = tk.Button(btnmenu, text = "LakeShore Configure", command = lambda: frm_lkshrconfig.tkraise(), width = 30)
        btn_p2.grid(row = 1, column = 0)
        btn_pend = tk.Button(btnmenu, text = "LakeShore Command Log", command = lambda: self.show_frame(lakeshore_command_frame), width = 30)
        btn_pend.grid(row = 2, column = 0)

        self.frames = {}

        for F in (lakeshore_measure_frame, lakeshore_command_frame):
            frame = F(container, self, lkshr)
            self.frames[F] = frame
            #frame.pack(padx = 5, pady = 5)
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(lakeshore_command_frame)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

 
def main():
    app = GraphTk()
    app.geometry('1200x800')
    app.mainloop()
    lkshr.close()

if __name__ == '__main__':
    main()