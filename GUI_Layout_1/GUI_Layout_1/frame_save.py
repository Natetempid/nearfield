import Tkinter as tk
import tkFileDialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import ttk
import threading
from frame_lakeshore_measure import lakeshore_measure_frame
from frame_daq_measure import daq_measure_frame
from frame_fluke8808a_control import fluke8808a_control_frame
from frame_keithley_control import keithley_control_frame
import numpy as np
import Queue as q
import os

class save_frame(tk.Frame):
    def __init__(self, master, controller,instruments):
        tk.Frame.__init__(self,master)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.controller = controller
        #instruments
        self.instruments = instruments
        self.lakeshore = self.instruments['lakeshore']
        self.fluke8808a = self.instruments['fluke8808a']
        self.keithley = self.instruments['keithley']
        self.daq9211 = self.instruments['daq9211']
        self.usbswitch = self.instruments['usbswitch']
        #measure frames
        self.lakeshoreframe = self.controller.frames[lakeshore_measure_frame]
        self.daqframe = self.controller.frames[daq_measure_frame]
        self.flukeframe = self.controller.frames[fluke8808a_control_frame]
        self.keithleyframe = self.controller.frames[keithley_control_frame]

        #need to get data from lists in measurement frames

        #each experiment will be a folder in dropbox folder
        #each folder will contain lakeshore, daq, fluke, and keithley data if so selected
        #each folder will also contain notes with a timestamp, so the note can be mapped to an event during the experiment

        #note - need to set way to reset the data lists in each measure frame

        #need header in each experiment file
        self.defaultdirectorystr = tk.StringVar()
        self.defaultdirectorystr.set('C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data')

        #defaultdirectoryframe
        self.defaultdirectoryframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.defaultdirectoryframe.grid(row = 0, column = 0, sticky = 'new')
        self.defaultdirectoryframe.grid_columnconfigure(0, weight = 1)
        self.defaultdirectorylbl = tk.Label(self.defaultdirectoryframe, text = "Experiment File Directory", font = ("tkDefaultFont", 18))
        self.defaultdirectorylbl.grid(row = 0, column = 0, sticky = 'w')
        self.defaultdirectoryentry = tk.Label(self.defaultdirectoryframe, textvariable = self.defaultdirectorystr, background = 'white', justify = tk.LEFT)
        self.defaultdirectoryentry.grid(row = 1, column = 0, sticky = 'new')
        self.defaultdirectorybtn = ttk.Button(self.defaultdirectoryframe, text = "Set Directory", command = lambda: self.set_directory())
        self.defaultdirectorybtn.grid(row = 1, column = 1)
    
    def set_directory(self):
        filename = tkFileDialog.askdirectory(initialdir = 'C:\Users\Nate\Dropbox (Minnich Lab)\\', title = 'Select Experiment Directory')
        self.defaultdirectorystr.set(filename)

    def init_experiment(self):
        #create experiment folder
        time_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_str = 'C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data' #replace this with a default path that can be set in the OS
        newfile_str = '%s\\experiment_%s' % (file_str, time_str)
        if not os.path.exists(newfile_str):
            os.makedirs(newfile_str)

     


