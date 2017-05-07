
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
from lakeshore335 import lakeshore335
from frame_lakeshore_measure import lakeshore_measure_frame
from frame_lakeshore_command import lakeshore_command_frame
from frame_lakeshore_config import lakeshore_config_frame
import ttk

lkshr = lakeshore335('ASRL3::INSTR')
LARGE_FONT= ("Verdana", 12)

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="right", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        testfrm = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        testfrm.pack(side = "left", fill = "both", padx = 5, pady = 5)
        #btn1 = tk.Button(testfrm, text = "LakeShore Measure", command = lambda: self.show_frame(lakeshore_measure_frame), width = 30)
        btn1 = tk.Button(testfrm, text = "Home", command = lambda: self.show_frame(StartPage), width = 30)
        btn1.grid(row = 0, column = 0)
        #btn2 = tk.Button(testfrm, text = "LakeShore Config", command = lambda: self.show_frame(PageOne), width = 30)
        btn2 = tk.Button(testfrm, text = "LakeShore Measure", command = lambda: self.show_frame(lakeshore_measure_frame), width = 30)
        btn2.grid(row = 1, column = 0)
        btn3 = tk.Button(testfrm, text = "LakeShore Config", command = lambda: self.show_frame(lakeshore_config_frame), width = 30)
        btn3.grid(row = 2, column = 0)
        #btn3 = tk.Button(testfrm, text = "LakeShore Command", command = lambda: self.show_frame(lakeshore_command_frame), width = 30)
        btn4 = tk.Button(testfrm, text = "LakeShore Command", command = lambda: self.show_frame(lakeshore_command_frame), width = 30)
        btn4.grid(row = 3, column = 0)
        
        self.frames = {}

        for F in (StartPage, lakeshore_measure_frame, lakeshore_command_frame, lakeshore_config_frame):

            frame = F(container, self, lkshr)

            self.frames[F] = frame
            #frame.pack()
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage) #makes start page be to setup the instruments

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


        
class StartPage(tk.Frame):

    def __init__(self, parent, controller, lakeshore):
        tk.Frame.__init__(self,parent)
        
        
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()


def main():
    app = GraphTk()
    app.geometry('1500x900')
    app.mainloop()
    lkshr.close()

if __name__ == '__main__':
    main()