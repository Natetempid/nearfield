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

class thermal_resistor(tk.Frame):
    def __init__(self, master, root, location):
        tk.Frame.__init__(self, master)
        self.config(border = 2, relief = tk.GROOVE)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        #self.grid_columnconfigure(1, weight = 1)
        
        self.location = location #this is where the resistor is in the model.  location = 0 is the first resistor
        self.material = "Enter Material:"
        self.thickness = 0 #m
        self.length = 1 #m
        self.width = 1 #m
        self.area = 1 #m^2
        self.thermal_conductivity = 1
        self.resistance = 1     
        

        self.property_frame = tk.LabelFrame(self, text = 'Resistor #%d' % self.location)
        self.property_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.property_frame.grid_columnconfigure(0, weight = 1)
        self.property_frame.grid_columnconfigure(1, weight = 1)
        for k in range(0,5):
            self.property_frame.grid_rowconfigure(k, weight = 1)
        #Material
        self.material_str = tk.StringVar()
        self.material_str.set(self.material)
        self.material_entry = tk.Entry(self.property_frame, textvariable = self.material_str)
        self.material_entry.grid(row = 0, column = 0, columnspan = 2, sticky = 'nsew')
        self.material_btn = ttk.Button(self.property_frame, text = 'Set', command = lambda: self.set_material())
        self.material_btn.grid(row = 0, column = 2, sticky = 'nsew')
        #self.material_btn.bind('<Return>', self.set_material)
        #Thickness
        self.thickness_lbl = tk.Label(self.property_frame, text = 'Set Thickness (m):')
        self.thickness_lbl.grid(row = 1, column = 0, sticky = 'nsew')
        self.thickness_str = tk.StringVar()
        self.thickness_str.set(str(self.thickness))
        self.thickness_entry = tk.Entry(self.property_frame, textvariable = self.thickness_str)
        self.thickness_entry.grid(row = 1, column = 1, sticky = 'nsew')
        self.thickness_btn = ttk.Button(self.property_frame, text = 'Set', command = lambda: self.set_thickness())
        self.thickness_btn.grid(row = 1, column = 2, sticky = 'nsew')
        #Length
        self.length_lbl = tk.Label(self.property_frame, text = 'Set Length (m):')
        self.length_lbl.grid(row = 2, column = 0, sticky = 'nsew')
        self.length_str = tk.StringVar()
        self.length_str.set(str(self.length))
        self.length_entry = tk.Entry(self.property_frame, textvariable = self.length_str)
        self.length_entry.grid(row = 2, column = 1, sticky = 'nsew')
        self.length_btn = ttk.Button(self.property_frame, text = 'Set', command = lambda: self.set_length())
        self.length_btn.grid(row = 2, column = 2, sticky = 'nsew')
        #Width
        self.width_lbl = tk.Label(self.property_frame, text = 'Set Width (m):')
        self.width_lbl.grid(row = 3, column = 0, sticky = 'nsew')
        self.width_str = tk.StringVar()
        self.width_str.set(str(self.width))
        self.width_entry = tk.Entry(self.property_frame, textvariable = self.width_str)
        self.width_entry.grid(row = 3, column = 1, sticky = 'nsew')
        self.width_btn = ttk.Button(self.property_frame, text = 'Set', command = lambda: self.set_width())
        self.width_btn.grid(row = 3, column = 2, sticky = 'nsew')
        #Thermal Conductivity
        self.thermal_conductivity_lbl = tk.Label(self.property_frame, text = 'Set Thermal Conductivity (W/mK):')
        self.thermal_conductivity_lbl.grid(row = 4, column = 0, sticky = 'nsew')
        self.thermal_conductivity_str = tk.StringVar()
        self.thermal_conductivity_str.set(str(self.thermal_conductivity))
        self.thermal_conductivity_entry = tk.Entry(self.property_frame, textvariable = self.thermal_conductivity_str)
        self.thermal_conductivity_entry.grid(row = 4, column = 1, sticky = 'nsew')
        self.thermal_conductivity_btn = ttk.Button(self.property_frame, text = 'Set', command = lambda: self.set_thermal_conductivity())
        self.thermal_conductivity_btn.grid(row = 4, column = 2, sticky = 'nsew')

        #draw resistor
        self.canvas = tk.Canvas(self, width = 50, height = 75+120+15+30 )
        self.canvas.grid(row = 0, column = 1, sticky = 'nsew')
        self.p1 = self.canvas.create_polygon(20, 0, 20, 30, 30, 30, 30, 0, fill = 'black') #start
        self.p2 = self.canvas.create_polygon(20, 30, 5, 45, 15, 45, 30, 30, fill = 'black') #left short
        self.p3 = self.canvas.create_polygon(5, 45, 35, 75, 45, 75, 15, 45, fill = 'black') #right long
        self.p4 = self.canvas.create_polygon(35, 75, 5, 105, 15, 105, 45, 75, fill = 'black') #left long
        self.p5 = self.canvas.create_polygon(5, 45+60, 35, 75+60, 45, 75+60, 15, 45+60, fill = 'black') #right long
        self.p6 = self.canvas.create_polygon(35, 75+60, 5, 105+60, 15, 105+60, 45, 75+60, fill = 'black') #left long
        self.p7 = self.canvas.create_polygon(5, 45+120, 35, 75+120, 45, 75+120, 15, 45+120, fill = 'black') #right long
        self.p8 = self.canvas.create_polygon(35, 75+120, 20, 75+120+15, 30, 75+120+15, 45, 75+120, fill = 'black') #left short
        self.p9 = self.canvas.create_polygon(20, 75+120+15, 20, 75+120+15+30, 30, 75+120+15+30, 30, 75+120+15, fill = 'black') #end

    def set_material(self):
        self.material = self.material_str.get()
        # add some pre-programmed materials
        if self.material == 'Glass':
            self.thickness_str.set('0.001')
            self.length_str.set('0.0254')
            self.width_str.set('0.0254')
            self.thermal_conductivity_str.set('1.3')
            self.set_all()
        elif self.material == 'Interface':
            self.thickness_str.set('0.0005')
            self.length_str.set('0.0254')
            self.width_str.set('0.0254')
            self.thermal_conductivity_str.set('2')
            self.set_all()
        elif self.material == 'Cu' or self.material == 'Copper':
            self.thickness_str.set('0.001')
            self.length_str.set('0.0285')
            self.width_str.set('0.0351')
            self.thermal_conductivity_str.set('385')
            self.set_all()
        #print(self.material)

    def set_thickness(self):
        self.thickness = float(self.thickness_str.get())

    def set_length(self):
        self.length = float(self.length_str.get())

    def set_width(self):
        self.width = float(self.width_str.get())

    def set_all(self):
        self.set_thickness()
        self.set_length()
        self.set_width()
        self.set_thermal_conductivity()

    #def set_area(self):
    #    self.set_length()
    #    self.set_width()
    #    self.area = self.length * self.width
    
    def set_thermal_conductivity(self):
        self.thermal_conductivity =  float(self.thermal_conductivity_str.get())

    def set_resistance(self):
        self.resistance = self.thickness/(self.length*self.width*self.thermal_conductivity)

    
