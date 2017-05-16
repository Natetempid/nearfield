
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

        #Plotting
        self.fig = plt.Figure(figsize=(5,5))
        self.ax1 = self.fig.add_subplot(1,2,1)
        self.ax2 = self.fig.add_subplot(2,2,2)
        self.ax3 = self.fig.add_subplot(2,2,4)

        #Plot 1 - Temperature
        self.lineT1, = self.ax1.plot([], [], lw=2, label = 'A', color = 'b')
        self.lineT2, = self.ax1.plot([], [], lw=2, label = 'B', color = 'r')
        self.ax1.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.ax1.set_title('Temp A: %.2fK | Temp B: %.2fK' % (0,0))

        #Plot 2 - Heater output current
        self.lineAmp1, = self.ax2.plot([], [], lw=2, label = '1', color = 'b')
        self.lineAmp2, = self.ax2.plot([], [], lw=2, label = '2', color = 'r')
        #self.ax2.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.ax2.set_title('Output 1: %.2f A | Output 2: %.2f A' % (0,0))
        
        #Plot 3 - Heater output percentage of max
        self.linePercent1, = self.ax3.plot([], [], lw=2, label = '1', color = 'b')
        self.linePercent2, = self.ax3.plot([], [], lw=2, label = '2', color = 'r')
        self.ax3.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.ax3.set_title('Output 1: %.2f %% | Output 2: %.2f %%' % (0,0))
        
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
            self.btn.config(text='Stop')
            return self.start()
        self.running = not self.running

    def start(self):
        self.lakeshore.measureAll(int(self.interval.get()))
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = int(self.interval.get())*1000 + 1, repeat=False)
        self.running = True
        self.btn.config(text='Stop')
        self.ani._start()

    def update_graph(self, i):
        #Temperature from Input A and B
        xlistA = []
        ylistA = []
        xlistB = []
        ylistB = []
        for elem in self.lakeshore.listA:
            xlistA.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistA.append(elem['data']) 
        self.lineT1.set_data(xlistA,ylistA)
        for elem in self.lakeshore.listB:
            xlistB.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistB.append(elem['data'])
        self.lineT2.set_data(xlistB,ylistB)
        #adjust axes
        if xlistA and ylistA and xlistB and ylistB:
            self.ax1.set_ylim(min([min(ylistA), min(ylistB)])-1, max([max(ylistA), max(ylistB)])+1)
            self.ax1.set_xlim(min([min(xlistA), min(xlistB)]), max([max(xlistA), max(xlistB)]))
            self.ax1.set_title('Temp A: %.2f K | Temp B: %.2f K' % (ylistA[-1], ylistB[-1]))
        
        #Heater Current from Outputs 1 and 2 - Amps
        xlist1 = []
        ylist1 = []
        xlist2 = []
        ylist2 = []
        if self.lakeshore.outputAmps1:
            for elem in self.lakeshore.outputAmps1:
                xlist1.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
                ylist1.append(elem['data']) 
            self.lineAmp1.set_data(xlist1,ylist1)
        if self.lakeshore.outputAmps2:
            for elem in self.lakeshore.outputAmps2:
                xlist2.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
                ylist2.append(elem['data'])
            self.lineAmp2.set_data(xlist2,ylist2)
        #adjust axes
        if xlist1 and ylist1 and xlist2 and ylist2:
            self.ax2.set_ylim(min([min(ylist1), min(ylist2)]), max([max(ylist1), max(ylist2)])+1)
            self.ax2.set_xlim(min([min(xlist1), min(xlist2)]), max([max(xlist1), max(xlist2)]))
            self.ax2.set_title('Output 1: %.2f A | Output 2: %.2f A' % (ylist1[-1], ylist2[-1]))

        #Heater Current from Outputs 1 and 2 - Amps
        xlist1_percent = []
        ylist1_percent = []
        xlist2_percent = []
        ylist2_percent = []
        if self.lakeshore.outputPercent1:
            for elem in self.lakeshore.outputPercent1:
                xlist1_percent.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
                ylist1_percent.append(elem['data']) 
            self.linePercent1.set_data(xlist1_percent,ylist1_percent)
        if self.lakeshore.outputPercent2:
            for elem2 in self.lakeshore.outputPercent2:
                xlist2_percent.append((elem2['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
                ylist2_percent.append(elem2['data'])
            self.linePercent2.set_data(xlist2_percent,ylist2_percent)
        #adjust axes
        if xlist1_percent and ylist1_percent and xlist2_percent and ylist2_percent:
            self.ax3.set_ylim(min([min(ylist1_percent), min(ylist2_percent)]), max([max(ylist1_percent), max(ylist2_percent)])+1)
            self.ax3.set_xlim(min([min(xlist1_percent), min(xlist2_percent)]), max([max(xlist1_percent), max(xlist2_percent)]))
            self.ax3.set_title('Output 1: %.2f %% | Output 2: %.2f %%' % (ylist1_percent[-1], ylist2_percent[-1]))
   
