
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
import threading
import time
import numpy as np

      
class lakeshore_measure_frame(tk.Frame):
    def __init__(self, master, controller, lakeshore ):
        tk.Frame.__init__(self, master)
        self.lakeshore = lakeshore
        self.running = False
        self.ani = None
        self.stopgraph_event = threading.Event()

        #data lists
        self.inputAlist_time = np.array([])
        self.inputAlist_data = np.array([])
        self.inputBlist_time = np.array([])
        self.inputBlist_data = np.array([])
        self.output1Ampslist_time = np.array([])
        self.output1Ampslist_data = np.array([])
        self.output2Ampslist_time = np.array([])
        self.output2Ampslist_data = np.array([])
        self.output1Percentlist_time = np.array([])
        self.output1Percentlist_data = np.array([])
        self.output2Percentlist_time = np.array([])
        self.output2Percentlist_data = np.array([])

        btns = tk.Frame(self)
        btns.pack()
        lbl = tk.Label(btns, text="Time Step (s)")
        lbl.pack(side=tk.LEFT)

        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(btns, textvariable = self.intervalstr, width=5)
        self.interval.pack(side=tk.LEFT)
        self.btn = ttk.Button(btns, text='Start', command=self.on_click)
        self.btn.pack(side=tk.LEFT)
        self.resetbtn = ttk.Button(btns, text = 'Reset Graphs', command = lambda: self.reset_graphs())
        self.resetbtn.pack(side = tk.LEFT)

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
            self.resetbtn.config(state = tk.DISABLED)
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani = False
            #self.ani.event_source.stop()
            self.lakeshore.stop_event.set()
            self.stopgraph_event.set()
            self.btn.config(text='Start')
            self.resetbtn.config(state = tk.NORMAL)
        else:
            self.btn.config(text='Stop')
            self.resetbtn.config(state = tk.DISABLED)
            return self.start()
        self.running = not self.running    

    def start(self):
        self.btn.config(text='Stop')
        self.lakeshore.measureAll(float(self.intervalstr.get()))
        t = threading.Thread(target = self.animation_target)
        t.start()
        print "Lakeshore Animation Thread-%d" % t.ident
        #self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = float(self.interval.get())*1000 + 1, repeat=False)
        self.ani = True
        self.running = True

        #self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = float(self.interval.get())*1000 + 1, repeat=False)
        self.running = True
        #self.ani._start()
    
    def update_graph(self):
        try:
            def totalseconds(x):
                return (x - datetime.datetime(1970,1,1)).total_seconds()
            totalseconds = np.vectorize(totalseconds)
            #update temperature graph
            while not (self.lakeshore.inputAq.empty() or self.lakeshore.inputBq.empty()): #only update graph when both tempA and tempB have been recorded
                #temperature from input A
                tempAdata = self.lakeshore.inputAq.get()
                timeA = tempAdata[0]
                tempA = tempAdata[1]
                self.inputAlist_time = np.append(self.inputAlist_time,timeA)
                self.inputAlist_data = np.append(self.inputAlist_data, tempA)
                self.lineT1.set_data(totalseconds(self.inputAlist_time), self.inputAlist_data )
                #temperature from input B
                tempBdata = self.lakeshore.inputBq.get()
                timeB = tempBdata[0]
                tempB = tempBdata[1]
                self.inputBlist_time = np.append(self.inputBlist_time,timeB)
                self.inputBlist_data = np.append(self.inputBlist_data, tempB)
                self.lineT2.set_data(totalseconds(self.inputBlist_time), self.inputBlist_data )
                self.ax1.relim()
                self.ax1.autoscale_view()
                #change axes
                if self.inputAlist_time.size > 0 and self.inputAlist_data.size > 0 and self.inputBlist_time.size > 0 and self.inputBlist_data.size > 0:
                    self.ax1.set_title('Temp A: %.2f K | Temp B: %.2f K' % (self.inputAlist_data[-1], self.inputBlist_data[-1]))
            #update heater output amps graphs
            while not (self.lakeshore.output1Ampsq.empty() and self.lakeshore.output2Ampsq.empty()):
                #output from heater 1
                heater1Ampsdata = self.lakeshore.output1Ampsq.get()
                time1Amps = heater1Ampsdata[0]
                data1Amps = heater1Ampsdata[1]
                self.output1Ampslist_time = np.append(self.output1Ampslist_time, time1Amps)
                self.output1Ampslist_data = np.append(self.output1Ampslist_data, data1Amps)
                self.lineAmp1.set_data(totalseconds(self.output1Ampslist_time), self.output1Ampslist_data)
                #output from heater 2
                heater2Ampsdata = self.lakeshore.output2Ampsq.get()
                time2Amps = heater2Ampsdata[0]
                data2Amps = heater2Ampsdata[1]
                self.output2Ampslist_time = np.append(self.output2Ampslist_time, time2Amps)
                self.output2Ampslist_data = np.append(self.output2Ampslist_data, data2Amps)
                self.lineAmp2.set_data(totalseconds(self.output2Ampslist_time), self.output2Ampslist_data)
                #change axes
                self.ax2.relim()
                self.ax2.autoscale_view()
                #change title
                if self.output1Ampslist_data.size > 0 and self.output2Ampslist_data.size > 0 and self.output1Ampslist_time.size > 0 and self.output2Ampslist_time.size > 0:
                    self.ax2.set_title('Output 1: %.2f A | Output 2: %.2f A' % (self.output1Ampslist_data[-1],self.output2Ampslist_data[-1]))
            #upate heater ouput percent graphs
            while not (self.lakeshore.output1Percentq.empty() and self.lakeshore.output2Percentq.empty()):
                #output from heater 1
                heater1Percentdata = self.lakeshore.output1Percentq.get()
                time1Percent = heater1Percentdata[0]
                data1Percent = heater1Percentdata[1]
                self.output1Percentlist_time = np.append(self.output1Percentlist_time, time1Percent)
                self.output1Percentlist_data = np.append(self.output1Percentlist_data, data1Percent)
                self.linePercent1.set_data(totalseconds(self.output1Percentlist_time), self.output1Percentlist_data)
                #output from heater 2
                heater2Percentdata = self.lakeshore.output2Percentq.get()
                time2Percent = heater2Percentdata[0]
                data2Percent = heater2Percentdata[1]
                self.output2Percentlist_time = np.append(self.output2Percentlist_time, time2Percent)
                self.output2Percentlist_data = np.append(self.output2Percentlist_data, data2Percent)
                self.linePercent2.set_data(totalseconds(self.output2Percentlist_time), self.output2Percentlist_data)
                #change axes
                self.ax3.relim()
                self.ax3.autoscale_view()
                #change title
                if self.output1Percentlist_data.size > 0 and self.output2Percentlist_data.size > 0 and self.output1Percentlist_time.size > 0 and self.output2Percentlist_time.size > 0:
                    self.ax3.set_title('Output 1: %.2f %% | Output 2: %.2f %%' % (self.output1Percentlist_data[-1],self.output2Percentlist_data[-1]))
            self.canvas.draw_idle()
        except RuntimeError,e:
            print '%s: %s' % ("Lakeshore",e.message)
            if "dictionary changed size during iteration" in e.message:
                #disable the start button
                self.btn.config(state = tk.DISABLED)
                #stop the graph animation
                self.ani = False
                self.stopgraph_event.set()
                #wait for animation to finish
                time.sleep(1.1)
                #restart thread
                t = threading.Thread(target = self.animation_target)
                t.start()
                print "Lakeshore Animation Thread-%d" % t.ident
                self.ani = True
                #renable start button
                self.btn.config(state = tk.NORMAL) 


    #instead of doing the animating in a separate thread, it should be done everytime the tkinter loop runs
    def animation_target(self):
        self.stopgraph_event.clear()
        while(not self.stopgraph_event.is_set()):
            #time.sleep(float(self.intervalstr.get()))
            self.stopgraph_event.wait(1)
            self.update_graph()
        self.stopgraph_event.set() #once animation stops, reset the stop event to trigger again

    def reset_graphs(self):
        self.inputAlist_time = np.array([])
        self.inputAlist_data = np.array([])
        self.inputBlist_time = np.array([])
        self.inputBlist_data = np.array([])
        self.output1Ampslist_time = np.array([])
        self.output1Ampslist_data = np.array([])
        self.output2Ampslist_time = np.array([])
        self.output2Ampslist_data = np.array([])
        self.output1Percentlist_time = np.array([])
        self.output1Percentlist_data = np.array([])
        self.output2Percentlist_time = np.array([])
        self.output2Percentlist_data = np.array([])

        self.lineT1.set_data(self.inputAlist_time, self.inputAlist_data )
        self.lineT2.set_data(self.inputBlist_time, self.inputBlist_data )
        self.lineAmp1.set_data(self.output1Ampslist_time, self.output1Ampslist_data)
        self.lineAmp2.set_data(self.output2Ampslist_time, self.output2Ampslist_data)
        self.linePercent1.set_data(self.output1Percentlist_time, self.output1Percentlist_data)
        self.linePercent2.set_data(self.output2Percentlist_time, self.output2Percentlist_data)
        self.canvas.draw_idle()