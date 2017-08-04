from __future__ import print_function
import sys
import Tkinter as tk
import ttk
import numpy as np
import os
import datetime
from scipy import interpolate
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime

from thermal_resistor import thermal_resistor
from verticalscrollframe import verticalscrollframe

class model_frame(tk.Frame):

    def __init__(self, master, root):
        tk.Frame.__init__(self, master)
        self.config(border = 2)
        self.master = master
        self.root = root

        self.location = 0 #resistor location
        self.resistor_list = []
        
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        #calibration
        self.calibration = None
        
        #frame for inputs
        self.value_input_frame = tk.Frame(self, border = 2)
        self.value_input_frame.grid(row = 0, column = 0, sticky = 'nsew')
        #self.value_input_frame.grid_rowconfigure(0, weight = 1)
        self.value_input_frame.grid_rowconfigure(1, weight = 1)
        
        #Label Frame for Initial Values
        self.init_label_frame = tk.LabelFrame(self.value_input_frame, text = 'Initialize Values')
        self.init_label_frame.grid(row = 0, column = 0, sticky = 'nsew')
        #for k in range(0,4):
         #   self.init_label_frame.grid_rowconfigure(k, weight = 1)
        self.sensor_area_lbl = tk.Label(self.init_label_frame, text = r'Sensor Area (mm^2)')
        self.sensor_area_lbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.sensor_area_str = tk.StringVar()
        self.sensor_area_str.set('.001')
        self.sensor_area_entry = tk.Entry(self.init_label_frame, textvariable = self.sensor_area_str)
        self.sensor_area_entry.grid(row = 1, column = 0, sticky = 'nsew')
        self.calibration_factor_lbl = tk.Label(self.init_label_frame, text = 'Calibration Factor (uV per W/m2)')
        self.calibration_factor_lbl.grid(row = 2, column = 0, sticky = 'nsew')
        self.calibration_factor_str = tk.StringVar()
        self.calibration_factor_str.set('1.9')
        self.calibration_factor_entry = tk.Entry(self.init_label_frame, textvariable = self.calibration_factor_str)
        self.calibration_factor_entry.grid(row = 3, column = 0, sticky = 'nsew')
        self.calibration_factor_btn = ttk.Button(self.init_label_frame, text = 'Apply Calibration & Plot', command = lambda: self.apply_cal_and_plot())
        self.calibration_factor_btn.grid(row = 4, column = 0, sticky = 'nsew')
        #Label Frame for Resistor Buttons
        self.resistor_btn_frame = tk.LabelFrame(self.value_input_frame, text = 'Resistor Model:')
        self.resistor_btn_frame.grid(row = 1, column = 0, sticky = 'nsew')
        for k in range(0,3):
            self.resistor_btn_frame.grid_rowconfigure(k, weight = 1)
        self.resistor_btn_frame.grid_columnconfigure(0, weight = 1)
        self.add_resistor_btn = ttk.Button(self.resistor_btn_frame, text = 'Add Thermal Resistor', command = lambda: self.add_resistor())
        self.add_resistor_btn.grid(row = 0, column = 0, sticky = 'nsew')
        self.remove_resistor_btn = ttk.Button(self.resistor_btn_frame, text = 'Remove Thermal Resistor', command = lambda: self.remove_resistor())
        self.remove_resistor_btn.grid(row = 1, column = 0, sticky = 'nsew')
        self.update_btn = ttk.Button(self.resistor_btn_frame, text = 'Apply Model', command = lambda: self.apply_model())
        self.update_btn.grid(row = 2, column = 0, sticky = 'nsew')

        #frame for thermal resistors
        self.resistor_frame = verticalscrollframe(self)#, border = 2)
        #self.resistor_frame.config(border = 2)
        self.resistor_frame.grid(row = 0, column = 1, sticky = 'nsew')

        #frame for plots
        self.plot_frame = tk.Frame(self, border = 2, relief = tk.GROOVE)
        self.plot_frame.grid(row = 0, column = 2, sticky = 'nsew')
        self.plot_frame.grid_rowconfigure(0, weight = 1)
        self.plot_frame.grid_columnconfigure(0, weight = 1)
        #add plot for input power and measured power
        self.power_plot_frame = tk.Frame(self.plot_frame)
        self.power_plot_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.power_plot_frame.grid_rowconfigure(0, weight = 1)
        self.power_plot_frame.grid_columnconfigure(0, weight = 1)

        self.power_f = plt.Figure()
        self.power_ax = self.power_f.add_subplot(1,1,1)
        self.power_line_fluke, = self.power_ax.plot([],[], color = 'b', label = "Fluke Measurement")
        self.power_line_hfs, = self.power_ax.plot([],[], color = 'r', label = 'Heat Fluke Sensor')
        self.power_ax.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.power_ax.set_title('Heating Power')
        self.power_ax.set_ylabel('Heat (W)')
        self.power_ax.set_xlabel('Time (s)')
        
        self.power_canvas = FigureCanvasTkAgg(self.power_f,self.power_plot_frame)
        self.power_canvas.show()
        self.power_canvas_widget = self.power_canvas.get_tk_widget()
        self.power_canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.power_canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #add plot for input power and measured power
        self.hf_plot_frame = tk.Frame(self.plot_frame)
        self.hf_plot_frame.grid(row = 1, column = 0, sticky = 'nsew')
        self.hf_plot_frame.grid_rowconfigure(0, weight = 1)
        self.hf_plot_frame.grid_columnconfigure(0, weight = 1)

        self.hf_f = plt.Figure()
        self.hf_ax = self.hf_f.add_subplot(1,1,1)
        self.hf_line_model, = self.hf_ax.plot([],[], color = 'b', label = "Thermal Model")
        self.hf_line_hfs, = self.hf_ax.plot([],[], color = 'r', label = 'Heat Fluke Sensor', marker = 'o')
        self.hf_ax.legend(bbox_to_anchor=(0, 0.02, -.102, -0.102), loc=2, ncol = 2, borderaxespad=0)
        self.hf_ax.set_title('Model')
        self.hf_ax.set_ylabel('Heat (W)')
        self.hf_ax.set_xlabel(r'\Delta T (K)')
        
        self.hf_canvas = FigureCanvasTkAgg(self.hf_f,self.hf_plot_frame)
        self.hf_canvas.show()
        self.hf_canvas_widget = self.hf_canvas.get_tk_widget()
        self.hf_canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.hf_canvas._tkcanvas.grid(row = 0, column = 0, sticky = 'nsew')#pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.hf_navigator_frame = tk.Frame(self.hf_plot_frame)
        self.hf_navigator_frame.grid(row = 1, column = 0, sticky = 'nsew')
        self.hf_toolbar = NavigationToolbar2TkAgg(self.hf_canvas, self.hf_navigator_frame)
        self.hf_toolbar.update()

    def apply_cal_and_plot(self):
        self.get_calibration(float(self.calibration_factor_str.get())*1e-6)
        self.update_plots()

    def get_calibration(self, calibration_factor):
        calibration_file = open('calibrationfactor.csv', 'r')
        calibration_temp = [float(line.split(',')[0]) for line in calibration_file]
        calibration_file.seek(0)
        calibration_value = [calibration_factor*float(line.strip().split(',')[1]) for line in calibration_file]
        self.calibration = interpolate.interp1d(calibration_temp, calibration_value, kind = 'cubic')


    def update_plots(self):

        ###################
        ## Applied Power ##
        ###################

        #Fluke measurements
        time_primary = []
        time_secondary = []
        voltage = []
        current = []
        #DAQ Measurements
        time_daq0 = []
        data_daq0 = []
        temp_daq2 = [] #temperature of heat flux sensor for calibration
        
        for interpreter in self.root.interpreter_list:
            if interpreter.name == 'Fluke Primary':
                time_primary = interpreter.selected_time
                voltage = interpreter.selected_data
            if interpreter.name == 'Fluke Secondary':
                time_secondary = interpreter.selected_time
                current = interpreter.selected_data
            if interpreter.name == 'DAQ Channel 0':
                time_daq0 = interpreter.selected_time
                data_daq0 = interpreter.selected_data
            if interpreter.name == 'DAQ Channel 2':
                temp_daq2 = interpreter.selected_data
        #Fluke
        np_time_primary = np.array(time_primary)
        np_time_secondary = np.array(time_secondary)
        np_voltage = np.array(voltage)
        np_current = np.array(current)
        np_power = np.absolute(np_voltage*np_current)#/(float(self.emitter_area_str.get())*0.0254**2))
        #DAQ
        np_time_daq0 = np.array(time_daq0)
        updated_calibration_factors = self.calibration(np.array(temp_daq2))
        np_hf_daq0 = np.absolute(np.array(data_daq0)/updated_calibration_factors)*float(self.sensor_area_str.get())

        #Lines
        self.power_line_fluke.set_data(np_time_primary, np_power)
        self.power_line_hfs.set_data(np_time_daq0, np_hf_daq0)
        #self.power_line_hfs.set_data(np_time_daq0, np_power/np_hf_daq0)

        self.power_ax.relim()
        self.power_ax.autoscale_view()
        self.power_canvas.draw_idle()


    def add_resistor(self):
        resistor = thermal_resistor(self.resistor_frame.interior, self.root, self.location)
        resistor.grid(row = self.location, column = 0, sticky = 'nsew')
        self.resistor_list.append(resistor)
        self.location = self.location + 1

    def remove_resistor(self):
        self.location = self.location - 1
        self.resistor_list[self.location].grid_remove()
        self.resistor_list = self.resistor_list[0:-1]
               
    def apply_model(self):
        if np.max([resistor.location for resistor in self.resistor_list]) == len(self.resistor_list) - 1: #then the number of resistors in the model equals the last resistor location
            #Hence, the resistors are in sequential order and the list iteration won't go beyond list dimensions
        #calculate resistance of all resistors and then plot result
            resistances = np.empty(len(self.resistor_list))
            for resistor in self.resistor_list:
                resistor.set_resistance()
                resistances[resistor.location] = resistor.resistance
        total_resistance = np.sum(resistances) 

        
        ###################################
        ## Use Measured Temperature Data ##
        ###################################

        for interpreter in self.root.interpreter_list:
            if interpreter.name == "DAQ Channel 0":
                data = np.array(interpreter.mean_data)
            if interpreter.name == "DAQ Channel 2":
                absorber_temp = np.array(interpreter.mean_data)
                updated_calibration_factors = self.calibration(absorber_temp)
            if interpreter.name == 'Lakeshore Input B':
                emitter_temp = np.array(interpreter.mean_data)

        heat_measured = np.abs(data)/updated_calibration_factors*float(self.sensor_area_str.get())

        self.hf_line_model.set_data(emitter_temp - absorber_temp, (emitter_temp - absorber_temp)/total_resistance)
        self.hf_line_hfs.set_data(emitter_temp - absorber_temp, heat_measured)
        self.hf_ax.relim()
        self.hf_ax.autoscale_view()
        self.hf_canvas.draw_idle()