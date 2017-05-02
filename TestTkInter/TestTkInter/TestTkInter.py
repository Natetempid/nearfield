import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import Tkinter as tk
from instruments import lakeshore335
import threading
import datetime

lkshr = lakeshore335('ASRL3::INSTR')

LARGE_FONT= ("Verdana", 12)
    
f = Figure(figsize=(5,5), dpi = 100)
a = f.add_subplot(111)

def animate(i):   
    a.clear()
    xlist = []
    ylist = []
    for elem in lkshr.listA:
        xlist.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
        ylist.append(elem['data'])

    a.plot(xlist,ylist)


class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        btn1 = tk.Button(self, text = "Measure", command = lambda: lkshr.measureA(1))
        btn1.pack()
        btn2 = tk.Button(self, text = "Stop Measure", command = lambda: lkshr.stopThread())
        btn2.pack()
        btn3 = tk.Button(self, text = "Reset Measure", command = lambda: lkshr.configThread())
        btn3.pack()

        self.entry1 = tk.Entry(self)
        self.entry1.pack()

        self.lbl1 = tk.Label(self)
        self.lbl1.pack()
        
        btn4 = tk.Button(self, text = "Query", command = lambda: self.runQuery())
        btn4.pack()
        
        
        #a.plot([1,2,3,4,5,6,7,8], [1,4,1,5,7,3,9,6])
        #a.set_title('Test')

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)

        canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
     
    def runQuery(self):
        str = self.entry1.get
        self.lbl1.config(text = str)
# Do I need to put a class that inherits from threading.Thread?

app = GraphTk()
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
lkshr.close()