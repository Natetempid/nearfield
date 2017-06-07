import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import threading
from frame_usbswitch_diagram import usbswitch_diagram_frame

class fluke8808a_plot_subframe(tk.Frame):
    def __init__(self,master,fluke8808a):
        tk.Frame.__init__(self,master)
        self.fluke8808a = fluke8808a
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.grid_rowconfigure(0,weight = 1)
        self.grid_rowconfigure(1,weight = 1)
        self.grid_columnconfigure(0,weight = 1)
        self.grid(row = 0, column = 1, rowspan = 2, sticky = 'nsew')
        
        self.primarypltframe = tk.Frame(self)
        self.primarypltframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.primarypltframe.grid_rowconfigure(0, weight = 1)
        self.primarypltframe.grid_columnconfigure(0, weight = 1)
        self.fig1 = plt.Figure()
        self.ax1 = self.fig1.add_subplot(1,1,1)
        self.line1, = self.ax1.plot([], [], lw=2, color = 'r')
        self.ax1.set_title('Primary Display:')
        self.canvas1 = FigureCanvasTkAgg(self.fig1,self.primarypltframe)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas1._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.secondarypltframe = tk.Frame(self)
        self.secondarypltframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.secondarypltframe.grid_rowconfigure(0, weight = 1)
        self.secondarypltframe.grid_columnconfigure(0, weight = 1)
        self.fig2 = plt.Figure()
        self.ax2 = self.fig2.add_subplot(1,1,1)
        self.ax2.set_title('Secondary Display:')
        self.line2, = self.ax2.plot([], [], lw=2, color = 'r')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.secondarypltframe)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas2._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.intervalframe = tk.Frame(self)
        self.intervalframe.grid(row = 2, column = 0, sticky = 'nsew')
        self.intervalframe.grid_columnconfigure(0,weight = 1)
        self.intervalframe.grid_columnconfigure(1,weight = 1)
        self.intervalframe.grid_columnconfigure(2,weight = 1)
        self.intervallbl = tk.Label(self.intervalframe, text = "Time Step (s)")
        self.intervallbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.interval = tk.Entry(self.intervalframe, width=5)
        self.interval.insert(0, '1')
        self.interval.grid(row = 0, column = 1, sticky = 'nsew')
        self.startbtn = ttk.Button(self.intervalframe, text='Start', command= lambda: self.on_click())
        self.startbtn.grid(row = 0, column = 2, sticky = 'nsew')


    def on_click(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani = False
            self.fluke8808a.stop_event.set()
            self.stopgraph_event.set()
            self.startbtn.config(text='Start')
        else:
            self.startbtn.config(text='Stop')
            return self.start()
        self.running = not self.running

    def start(self):
        self.startbtn.config(text='Stop')
        self.fluke8808a.measureBothDisplays(float(self.interval.get()))
        t = threading.Thread(target = self.animation_target)
        t.start()
        self.ani = True
        self.running = True

    def update_graph(self):
        xlist1 = []
        ylist1 = []
        xlist2 = []
        ylist2 = []
        for elem1 in self.fluke8808a.list1:
            xlist1.append((elem1['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            #need to interpet the units
            ylist1.append(elem1['data']) 
        self.line1.set_data(xlist1,ylist1)
        for elem2 in self.fluke8808a.list2:
            xlist2.append((elem2['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylist2.append(elem2['data'])
        self.line2.set_data(xlist2,ylist2)
        #adjust axes
        if xlist1 and ylist1:
            self.ax1.set_ylim(min(ylist1), max(ylist1))
            self.ax1.set_xlim(min(xlist1), max(xlist1))
            self.ax1.set_title('Primary Display: %s' % elem1['unit'])
        if xlist2 and ylist2:
            self.ax2.set_ylim(min(ylist2), max(ylist2))
            self.ax2.set_xlim(min(xlist2), max(xlist2))
            self.ax2.set_title('Secondary Display: %s' % elem2['unit'])
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()

    def animation_target(self):
        self.stopgraph_event.clear()
        while(not self.stopgraph_event.is_set()):
            time.sleep(float(self.interval.get()))
            self.update_graph()
        self.stopgraph_event.set() #once animation stops, reset the stop event to trigger again
