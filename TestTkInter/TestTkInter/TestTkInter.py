import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import Tkinter as tk
import ttk
from instruments import lakeshore335
import threading
import datetime
import numpy as np

lkshr = lakeshore335('ASRL3::INSTR')

LARGE_FONT= ("Verdana", 12)
    
f = Figure(figsize=(10,5), dpi = 100)
aA = f.add_subplot(121)
aB = f.add_subplot(122)

def animate(i):   
    aA.clear()
    aB.clear()
    xlistA = np.array((1,), dtype = float) #[]
    ylistA = np.array((1,), dtype = float) #[]
    for elem in lkshr.listA:
        np.append(xlistA,(elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
        np.append(ylistA,elem['data'])

    aA.plot(xlistA,ylistA)
   # aA.set_title("Input A: %.2fK" % ylistA[-1] )

    xlistB = np.array((1,), dtype = float) #[]
    ylistB = np.array((1,), dtype = float) #[]
    for elem in lkshr.listB:
        np.append(xlistB,(elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
        np.append(ylistB,elem['data'])

    aB.plot(xlistB,ylistB)
   # aB.set_title("Input B: %.2fK" % ylistB[-1] )


class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(2, weight=1)

        #self.frames = {}

        frame = Page(container, self)

        #self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
    #    self.show_frame(StartPage)

    #def show_frame(self, cont):

    #    frame = self.frames[cont]
    #    frame.tkraise()

        
class Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)

        btn1 = tk.Button(self, text = "Measure", command = lambda: lkshr.measureB(1))
        btn1.grid(row = 0, column = 0)
        #btn1.pack()
        btn2 = tk.Button(self, text = "Stop Measure", command = lambda: lkshr.stopThread())
        btn2.grid(row = 1, column = 0)
        #btn2.pack()
        btn3 = tk.Button(self, text = "Reset Measure", command = lambda: lkshr.configThread())
        btn3.grid(row = 2, column = 0)
        #btn3.pack()

        entry1 = tk.Entry(self)
        #entry1.pack()
        entry1.grid(row = 0, column = 1)
        
        v = tk.StringVar()
        lbl1 = tk.Label(self, textvariable = v)
        #lbl1.pack()
        lbl1.grid(row = 2, column = 1)
        
        btn4 = tk.Button(self, text = "Query", command = lambda: v.set(lkshr.lakestr2str(lkshr.ctrl.query(entry1.get()))))
        #btn4.pack()
        btn4.grid(row = 1, column = 1)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        #canvas.get_tk_widget().pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        canvas.get_tk_widget().grid(row = 0, column = 2, rowspan = 3, columnspan = 2)
        #canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        canvas._tkcanvas.grid(row = 0, column = 2, rowspan = 3, columnspan = 2)     

        
# Do I need to put a class that inherits from threading.Thread?

app = GraphTk()
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
lkshr.close()