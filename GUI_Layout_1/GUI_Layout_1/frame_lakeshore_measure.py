
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
    def __init__(self, master, controller, root, lakeshore ): #controller is the program frame instance, which is a child of the GraphTk class.  root is the GraphTk instance
        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight = 1)
        self.controller = controller
        self.root = root

        self.lakeshore = lakeshore
        self.measurement_running = False
        self.plot_running = False
        self.callback = None

        #self.stopgraph_event = threading.Event()

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

        #Header frame that includes all controls
        self.headerframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.headerframe.grid(row = 0, column = 0, sticky = 'nsew')
        self.headerframe.grid_rowconfigure(0,weight = 1)
        self.headerframe.grid_columnconfigure(3,weight=1)
        self.headerframe.grid_columnconfigure(4,weight=1)
        self.headerframe.grid_columnconfigure(5,weight=1)
        #canvas for indicator
        self.indicator_canvas = tk.Canvas(self.headerframe, width = 50, height = 50)
        self.indicator_canvas.grid(row = 0, column = 0, sticky = 'ns')
        self.indicator = self.indicator_canvas.create_oval(5,5,40,40, fill = 'red4')
        self.indicatorstr = tk.StringVar()
        self.indicatorstr.set('Lakeshore not measuring')
        self.indicatorlbl = tk.Label(self.headerframe, textvariable = self.indicatorstr, font = ('tkDefaultFont', 12))
        self.indicatorlbl.grid(row = 0, column = 1, sticky = 'nsew')
        #Time interval
        self.intervalframe = tk.Frame(self.headerframe,borderwidth = 5)
        self.intervalframe.grid(row = 0, column = 2, sticky = 'nsew')
        self.intervalframe.grid_rowconfigure(0,weight = 1)
        self.intervalframe.grid_columnconfigure(0, weight = 1)
        self.interval_lbl = tk.Label(self.intervalframe, text = 'Measurement Time Step (s)')
        self.interval_lbl.grid(row = 0, column = 0)
        self.intervalstr = tk.StringVar()
        self.intervalstr.set('1')
        self.interval = tk.Entry(self.intervalframe, textvariable = self.intervalstr, width=5)
        self.interval.grid(row = 1, column = 0, sticky = 'nsew')
        #Measure Button
        self.measure_btn = ttk.Button(self.headerframe, text = 'Start Measurement', command = lambda:self.measure_click())
        self.measure_btn.grid(row = 0, column = 3, sticky = 'nsew')
        #Plot Button
        self.measure_and_plot_btn = ttk.Button(self.headerframe, text = 'Start Measurement & Plot', command = lambda: self.measure_and_plot_click())
        self.measure_and_plot_btn.grid(row = 0, column = 4, sticky = 'nsew')
        #Reset Plot Button
        #self.resetbtn = ttk.Button(self.headerframe, text = 'Reset Graphs', command = lambda: self.reset_matplotlib())
        self.resetbtn = ttk.Button(self.headerframe, text = 'Reset Graphs', command = lambda: self.reset_graphs())
        self.resetbtn.grid(row = 0, column = 5, sticky = 'nsew')

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
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 1, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
     
    #Click Methods

    def measure_click(self):
        if self.measurement_running: #then user wants to stop the Measurement
            self.stop_instrument()
            self.stop_graph() #stopping the measurement also stops the graph
        else: #then user wants to start the measurement without running the graph
            self.start_instrument()

    def measure_and_plot_click(self):
        if self.measurement_running and not self.plot_running: #then user has started measuring and wants to graph
            self.start_graph()
        elif self.measurement_running and self.plot_running: #then user wants to stop the graph but keep the measurement going
            self.stop_graph()
        elif not self.measurement_running and not self.plot_running: #then user wants to start the measurement and start the graph
            self.start_instrument()
            self.start_graph()
        #note the user cannot stop the measurement from the measure_and_plot button. To stop the Measurement, the user must click the measure_btn
      
    def start_instrument(self):
        self.lakeshore.measureAll(float(self.intervalstr.get()))
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "green2")    
        self.indicatorstr.set('Lakeshore measuring...')
        #change measurement button
        self.measure_btn.config(text = 'Stop Measurement & Plot')
        #change measurement running state
        self.measurement_running = True

    def stop_instrument(self):
        self.lakeshore.stop_event.set()
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "red4")    
        self.indicatorstr.set('Lakeshore not measuring')
        #change measurement button
        self.measure_btn.config(text = 'Start Measurement')
        while self.lakeshore.thread_active:
            time.sleep(0.002) #wait for the measurement to stop
        #clear the measurement queue
        self.lakeshore.clear_queues()
        #change measurement running state
        self.measurement_running = False

    def start_graph(self):
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Stop Plot')
        #disable reset button
        self.resetbtn.config(state = tk.DISABLED)
        #update the graph
        #self.update_graph()
        self.reset_matplotlib()
        #change plot running state
        self.plot_running = True

    def stop_graph(self):
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Start Measurement & Plot')
        #enable reset button
        self.resetbtn.config(state = tk.NORMAL)
        if self.callback is not None:
            self.root.after_cancel(self.callback)
        #change plot running state
        self.plot_running = False

    def update_graph(self):
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

        #the draw_idle method seems to throw an error within the Tkinter callback occasioanlly. 
        #When that happens, stop the update_graph, re-intialize the plots, wait 5 milliseconds and restart the update graph method

        plt.pause(0.003)
        try: 
            self.canvas.draw_idle()
        except SystemError,e:
            if 'Negative size passed to PyString_FromStringAndSize' in e.message:
                return self.reset_matplotlib()
        self.callback = self.root.after(100, self.update_graph)

    def reset_matplotlib(self):
        print "resetting matplotlib at %s"  % str(datetime.datetime.now())
        #stop the update_graph
        self.stop_graph()
        #destroy canvas widget
        self.canvas_widget.destroy()
        
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
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 1, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        time.sleep(0.005)

        self.update_graph()

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