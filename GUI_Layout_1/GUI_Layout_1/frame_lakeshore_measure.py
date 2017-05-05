
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

      
class lakeshore_measure_frame(tk.Frame):
    def __init__(self, master, controller, lakeshore ):
        tk.Frame.__init__(self, master)
        self.lakeshore = lakeshore
        self.running = False
        self.ani = None

        btns = tk.Frame(self)
        btns.pack()
        
        lbl = tk.Label(btns, text="Time Step (s)")
        lbl.pack(side=tk.LEFT)

        self.interval = tk.Entry(btns, width=5)
        self.interval.insert(0, '1')
        self.interval.pack(side=tk.LEFT)

        self.btn = tk.Button(btns, text='Start', command=self.on_click)
        self.btn.pack(side=tk.LEFT)

        self.fig = plt.Figure(figsize=(5,5))
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.line, = self.ax1.plot([], [], lw=2, label = 'A', color = 'b')
        self.line2, = self.ax1.plot([], [], lw=2, label = 'B', color = 'r')
        self.ax1.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.ax1.set_title('Temp A: %.2fK | Temp B: %.2fK' % (0,0))
        self.canvas = FigureCanvasTkAgg(self.fig,self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
       

    def on_click(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani.event_source.stop()
            self.lakeshore.stop_event.set()
            self.btn.config(text='Start')
        else:
            return self.start()
            self.btn.config(text='Stop')
        self.running = not self.running

    def start(self):
        self.lakeshore.measureAandB(int(self.interval.get()))
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = int(self.interval.get())*1000 + 1, repeat=False)
        self.running = True
        self.btn.config(text='Stop')
        self.ani._start()

    def update_graph(self, i):
        xlistA = []
        ylistA = []
        xlistB = []
        ylistB = []
        for elem in self.lakeshore.listA:
            xlistA.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistA.append(elem['data']) 
        self.line.set_data(xlistA,ylistA)
        for elem in self.lakeshore.listB:
            xlistB.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistB.append(elem['data'])
        self.line2.set_data(xlistB,ylistB)
        #adjust axes
        if xlistA and ylistA and xlistB and ylistB:
            self.ax1.set_ylim(min([min(ylistA), min(ylistB)])-1, max([max(ylistA), max(ylistB)])+1)
            self.ax1.set_xlim(min([min(xlistA), min(xlistB)]), max([max(xlistA), max(xlistB)]))
            self.ax1.set_title('Temp A: %.2fK | Temp B: %.2fK' % (ylistA[-1], ylistB[-1]))
   
