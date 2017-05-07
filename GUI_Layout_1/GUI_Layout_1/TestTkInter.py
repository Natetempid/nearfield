import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt

import Tkinter as tk
import ttk
from instruments import lakeshore335
import threading
import datetime
import numpy as np

lkshr = lakeshore335('ASRL3::INSTR')

LARGE_FONT= ("Verdana", 12)
    
#f = Figure(figsize=(10,5), dpi = 100)
#aA = f.add_subplot(121)
#aB = f.add_subplot(122)

#def animate(i):   
#    aA.clear()
#    aB.clear()
#    xlistA = []#np.array((1,), dtype = float) #[]
#    ylistA = []#np.array((1,), dtype = float) #[]
#    for elem in lkshr.listA:
#        #np.append(xlistA,(elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
#        #np.append(ylistA,elem['data'])
#        xlistA.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
#        ylistA.append(elem['data'])
#    aA.plot(xlistA,ylistA)
#   # aA.set_title("Input A: %.2fK" % ylistA[-1] )

#    xlistB = []#np.array((1,), dtype = float) #[]
#    ylistB = []#np.array((1,), dtype = float) #[]
#    for elem in lkshr.listB:
#        #np.append(xlistB,(elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
#        #np.append(ylistB,elem['data'])
#        xlistB.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
#        ylistB.append(elem['data'])
#    aB.plot(xlistB,ylistB)
#   # aB.set_title("Input B: %.2fK" % ylistB[-1] )    


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
        self.running = False
        self.ani = None
        #label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)
        
        self.btn1 = ttk.Button(self, text = "Measure", command = lambda: self.measureA)
        #btn1 = tk.Button(self, text = "Measure", command = lambda: threading.Thread(target = measure, args=(1,)).start() ) #change args to timestep
        self.btn1.grid(row = 0, column = 0)
        #btn1.pack()
        self.btn2 = ttk.Button(self, text = "Stop Measure", command = lambda: lkshr.stopThread())
        self.btn2.grid(row = 1, column = 0)
        #btn2.pack()
        self.btn3 = ttk.Button(self, text = "Reset Measure", command = lambda: lkshr.configThread())
        self.btn3.grid(row = 2, column = 0)
        #btn3.pack()

        self.entry1 = tk.Entry(self)
        #entry1.pack()
        self.entry1.grid(row = 0, column = 1)
        
        self.v = tk.StringVar()
        self.lbl1 = tk.Label(self, textvariable = self.v)
        #lbl1.pack()
        self.lbl1.grid(row = 2, column = 1)
        
        self.btn4 = ttk.Button(self, text = "Query", command = lambda: self.v.set(lkshr.lakestr2str(lkshr.ctrl.query(self.entry1.get()))))
        #btn4.pack()
        self.btn4.grid(row = 1, column = 1)
        
            
        self.f = Figure(figsize=(10,5), dpi = 100)
        self.aA = self.f.add_subplot(121)
        self.lineA, = self.aA.plot([], [], lw=2)
        self.aB = self.f.add_subplot(122)
        self.lineB, = self.aB.plot([], [], lw=2)


        self.canvas = FigureCanvasTkAgg(self.f, parent)
        self.canvas.show()
        #canvas.get_tk_widget().pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.canvas.get_tk_widget().grid(row = 0, column = 2, rowspan = 3, columnspan = 2)
        #canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        #self.canvas._tkcanvas.grid(row = 0, column = 2, rowspan = 3, columnspan = 2)     
    
    def measureA(self):
        lkshr.measureA(1)
        if self.ani is None:
            return self.start()
        if self.running:
            self.ani.event_source.stop()
            self.btn1.config(text='Un-Pause')
        else:
            self.ani.event_source.start()
            self.btn1.config(text='Pause')
        self.running = not self.running

    def start(self):
        self.ani = animation.FuncAnimation(self.f, self.update_graph, interval = 1000, repeat= False)
        self.running = True
        self.btn1.config(text = 'Pause')
        self.ani._start()

    def update_graph(self, i):
        xlistA = []#np.array((1,), dtype = float) #[]
        ylistA = []#np.array((1,), dtype = float) #[]
        for elem in lkshr.listA:
            #np.append(xlistA,(elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            #np.append(ylistA,elem['data'])
            xlistA.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistA.append(elem['data'])
    
        self.lineA.set_data(xlistA, ylistA)     
        
        if xlistA and ylistA:
            self.aA.set_ylim(min(ylistA), max(ylistA))
            self.aA.set_xlim(min(xlistA), max(xlistA))
      
        return self.lineA,



def main():
    app = GraphTk()
    #ani = animation.FuncAnimation(f, animate, interval=1000)
    app.mainloop()
    lkshr.close()

if __name__ == '__main__':
    main()