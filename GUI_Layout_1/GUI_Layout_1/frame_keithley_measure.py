
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

      
class keithley_measure_frame(tk.Frame):
    def __init__(self, master, controller, root, keithley ):
        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight = 1)
        self.master = master
        self.controller = controller
        self.root = root
        self.keithley = keithley

        self.measurement_running = False
        self.plot_running = False
        self.callback = None
        
        #Variables - Bias, Current, Resistance
        self.bias_time = []
        self.bias_data = []
        self.current_time = []
        self.current_data = []
        self.resistance_time = []
        self.resistance_data = []

        
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

        #Plot 1 - Applied Bias
        self.lineBias, = self.ax1.plot([], [], lw=2)
        self.ax1.set_title('Applied Bias: %.2fK' % 0)

        #Plot 2 - Measured Current
        self.lineCurrent, = self.ax2.plot([], [], lw=2)
        self.ax2.set_title('Measured Current: %.2f A' % 0)
        
        #Plot 3 - Measured Resistance
        self.lineResistance, = self.ax3.plot([], [], lw=2)
        self.ax3.set_title('Measured Resistance 1: %.2f Ohms' % 0)
        
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
        #setup Keithley to measure
        self.keithley.measure(float(self.intervalstr.get()))
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "green2")    
        self.indicatorstr.set('Keithley measuring...')
        #change measurement button
        self.measure_btn.config(text = 'Stop Measurement & Plot')
        #change measurement running state
        self.measurement_running = True

    def stop_instrument(self):
        self.keithley.stop_event.set()
        #change indicator
        self.indicator_canvas.itemconfig(self.indicator, fill = "red4")    
        self.indicatorstr.set('Keithley not measuring')
        #change measurement button
        self.measure_btn.config(text = 'Start Measurement')
        while self.keithley.thread_active:
            time.sleep(0.002) #wait for the measurement to stop
        #clear the measurement queue
        self.keithley.clear_queues()
        #change measurement running state
        self.measurement_running = False

    def start_graph(self):
        #change plot running state
        self.plot_running = True
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Stop Plot')
        #disable reset button
        self.resetbtn.config(state = tk.DISABLED)
        #update the graph
        #self.update_graph()
        self.reset_matplotlib()

    def stop_graph(self):
        #change plot running state
        self.plot_running = False
        #change measure and plot button
        self.measure_and_plot_btn.config(text = 'Start Measurement & Plot')
        #enable reset button
        self.resetbtn.config(state = tk.NORMAL)
        if self.callback is not None:
            self.root.after_cancel(self.callback)

    def update_graph(self):
        def totalseconds(x):
            return (x - datetime.datetime(1970,1,1)).total_seconds()
        totalseconds = np.vectorize(totalseconds)
        #update temperature graph
        while not (self.keithley.dataq.empty() ): 
            #get parsed data           
            parseddata = self.keithley.dataq.get()
   
            self.bias_time.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.bias_data.append(parseddata[1]) 
            self.lineBias.set_data(self.bias_time,self.bias_data)

            self.current_time.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.current_data.append(parseddata[2])
            self.lineCurrent.set_data(self.current_time,self.current_data)
        
            self.resistance_time.append((parseddata[0] - datetime.datetime(1970,1,1)).total_seconds())
            self.resistance_data.append(parseddata[3])
            self.lineResistance.set_data(self.resistance_time,self.resistance_data)
        
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.ax3.relim()
            self.ax3.autoscale_view()

   
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

        self.lineBias, = self.ax1.plot([], [], lw=2)
        self.ax1.set_title('Applied Bias: %.2fK' % 0)

        #Plot 2 - Measured Current
        self.lineCurrent, = self.ax2.plot([], [], lw=2)
        self.ax2.set_title('Measured Current: %.2f A' % 0)
        
        #Plot 3 - Measured Resistance
        self.lineResistance, = self.ax3.plot([], [], lw=2)
        self.ax3.set_title('Measured Resistance 1: %.2f Ohms' % 0)

        self.canvas = FigureCanvasTkAgg(self.fig,self)
        self.canvas.show()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row = 1, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        time.sleep(0.005)

        self.update_graph()

    def reset_graphs(self):
        self.bias_time = []
        self.bias_data = []
        self.current_time = []
        self.current_data = []
        self.resistance_time = []
        self.resistance_data = []

        self.lineBias.set_data(self.bias_time, self.bias_data )
        self.lineCurrent.set_data(self.current_time, self.current_data)
        self.lineResistance.set_data(self.resistance_time, self.resistance_data)
        self.canvas.draw_idle()
