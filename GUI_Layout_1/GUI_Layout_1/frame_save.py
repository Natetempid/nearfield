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

from lakeshore335 import lakeshore335
from daq9211 import daq9211
from fluke8808a import fluke8808a
from keithley2410 import keithley2410

import numpy as np
import Queue as q
import os

class save_frame(tk.Frame):
    def __init__(self, master, controller, instruments):
        tk.Frame.__init__(self,master)
        #self.grid_rowconfigure(0, weight = 1)
        #self.grid_rowconfigure(1, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.controller = controller
        #instruments
        self.instruments = dict(instruments) #self.instruments is a copy of the instruments dictionary and isn't the actually instant
        del self.instruments['usbswitch']
        self.logging = False
        self.logging_thread_event = threading.Event()
        #self.file_notes = -1

        #need to get data from each instrument
        #dictionary specifying whether measure each instrumnet
        self.measurebools = {'lakeshore': False, 'daq9211': False, 'fluke8808a': False, 'keithley': False}

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

        #frame to select instruments
        self.instrumentframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.instrumentframe.grid(row = 1, column = 0, sticky = 'nsew')
        self.instrumentframe.grid_rowconfigure(1, weight = 1)
        self.instrumentframe.grid_columnconfigure(0, weight = 1)
        self.instrumentframe.grid_columnconfigure(2, weight = 1)
        self.toselectlbl = tk.Label(self.instrumentframe, text = "Select Instruments to Log:")
        self.toselectlbl.grid(row = 0, column = 0, sticky = 'nw')
        self.toselectbox = tk.Listbox(self.instrumentframe, exportselection=False)
        self.toselectbox.grid(row = 1, column = 0, sticky ='nsew', padx = 5)
        
        for item in self.instruments: #fill listbox
            #if not (item == "usbswitch"):
            self.toselectbox.insert(tk.END, item)

        #frame for action buttons
        self.selectbtnframe = tk.Frame(self.instrumentframe)
        self.selectbtnframe.grid(row = 1, column = 1, sticky = 'nsew')
        for k in range(0,4):
            self.selectbtnframe.grid_rowconfigure(k,weight = 1)
        self.btnaddall = ttk.Button(self.selectbtnframe, text = 'Select All', command = lambda: self.addall())
        self.btnaddall.grid(row = 0, column = 0, sticky = 'nsew')
        self.btnadd = ttk.Button(self.selectbtnframe, text = 'Add ->', command = lambda: self.addinstrument())
        self.btnadd.grid(row = 1, column = 0, sticky = 'nsew')
        self.btnremove = ttk.Button(self.selectbtnframe, text = '<- Remove', command = lambda: self.removeinstrument())
        self.btnremove.grid(row = 2, column = 0, sticky = 'nsew')
        self.btnremoveall= ttk.Button(self.selectbtnframe, text = 'Remove All', command = lambda: self.removeall())
        self.btnremoveall.grid(row = 3, column = 0, sticky = 'nsew')

        self.selectedlbl = tk.Label(self.instrumentframe, text = "Selected Instruments:")
        self.selectedlbl.grid(row = 0, column = 2, sticky = 'nw')
        self.selectedbox = tk.Listbox(self.instrumentframe, exportselection=False)
        self.selectedbox.grid(row = 1, column = 2, sticky ='nsew', padx = 5)
        #frame for time delay
        self.timedelayframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.timedelayframe.grid(row = 2, column = 0, sticky = 'nsew')
        self.timedelaylbl = tk.Label(self.timedelayframe, text = 'Time Delay to Write Data:', font = ('tkDefaultFont', 18))
        self.timedelaylbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.time_delay = tk.StringVar()
        self.time_delay.set('30')
        self.timedelayentry = tk.Entry(self.timedelayframe, textvariable = self.time_delay, font = ('tkDefaultFont', 14))
        self.timedelayentry.grid(row = 0, column = 1, sticky = 'nsew')


        #frame to start and stop logging
        self.loggingframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.loggingframe.grid(row = 3, column = 0, sticky = 'nsew')
        self.loggingframe.grid_columnconfigure(2, weight = 1)
        self.indicator_canvas = tk.Canvas(self.loggingframe, width = 100, height = 100)
        self.indicator_canvas.grid(row = 0, column = 0, sticky = 'ns')
        self.indicator = self.indicator_canvas.create_oval(10,10,80,80, fill = 'red4')
        self.indicatorstr = tk.StringVar()
        self.indicatorstr.set('Not Logging')
        self.indicatorlbl = tk.Label(self.loggingframe, textvariable = self.indicatorstr, font = ('tkDefaultFont', 18))
        self.indicatorlbl.grid(row = 0, column = 1, sticky = 'nsew')
        self.loggingbtn = ttk.Button(self.loggingframe, text = "Enable Experiment Log", command = lambda: self.log_click())
        self.loggingbtn.grid(row = 0, column = 2, sticky = 'nsew')

        #Add ability to write notes
        self.noteframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.noteframe.grid(row = 4, column = 0, sticky = 'nsew')
        self.noteframe.grid_columnconfigure(0, weight = 1)
        self.noteframe.grid_columnconfigure(1, weight = 1)
        self.noteframe.grid_rowconfigure(1,weight = 1)
        self.note2addlbl = tk.Label(self.noteframe, text = "Note to Add", font = ('tkDefaultFont', 18))
        self.note2addlbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.addednoteslbl = tk.Label(self.noteframe, text = "Added Notes", font = ('tkDefaultFont', 18))
        self.addednoteslbl.grid(row = 0, column = 1, sticky = 'nsew')
        self.note2addstr = tk.StringVar()
        #self.note2addentry = tk.Entry(self.noteframe, textvariable = self.note2addstr)
        self.note2addentry = tk.Text(self.noteframe)#, textvariable = self.note2addstr)
        self.note2addentry.grid(row = 1, column = 0, sticky = 'nsew')
        self.addnotebtn = ttk.Button(self.noteframe, text = 'Add Note', state = tk.DISABLED, command = lambda: self.addnote())
        self.addnotebtn.grid(row = 2, column = 0, sticky = 'nsew')
        self.addednotestext = tk.Text(self.noteframe)
        self.addednotestext.grid(row = 1, column = 1, rowspan = 2, sticky = 'nsew')
        self.addednotesscrollbar = ttk.Scrollbar(self.noteframe)
        self.addednotesscrollbar.grid(row = 1, column = 2, rowspan = 2, sticky = 'nsew')
        self.addednotesscrollbar.config(command = self.addednotestext.yview)
        self.addednotestext.config(yscrollcommand = self.addednotesscrollbar.set)


    def addinstrument(self ):
        instrument_name = self.toselectbox.get(self.toselectbox.curselection()[0])
        if instrument_name == 'lakeshore':
            self.measurebools[instrument_name] = True
            self.instruments[instrument_name].logging = True
        elif instrument_name == 'daq9211':
            self.measurebools[instrument_name] = True
            self.instruments[instrument_name].logging = True
        elif instrument_name == 'fluke8808a':
            self.measurebools[instrument_name] = True
            self.instruments[instrument_name].logging = True
        elif instrument_name == 'keithley':
            self.measurebools[instrument_name] = True
            self.instruments[instrument_name].logging = True
        else:
            return None
        self.selectedbox.insert(tk.END, instrument_name)

    def removeinstrument(self ):
        instrument_name = self.selectedbox.get(self.selectedbox.curselection()[0])
        if instrument_name == 'lakeshore':
            self.measurebools[instrument_name] = False
            self.instruments[instrument_name].logging = False
        elif instrument_name == 'daq9211':
            self.measurebools[instrument_name] = False
            self.instruments[instrument_name].logging = False
        elif instrument_name == 'fluke8808a':
            self.measurebools[instrument_name] = False
            self.instruments[instrument_name].logging = False
        elif instrument_name == 'keithley':
            self.measurebools[instrument_name] = False
            self.instruments[instrument_name].logging = False
        else:
            return None
        self.selectedbox.delete(self.selectedbox.curselection()[0])
    
    def addall(self):
        for instrument_name in self.toselectbox.get(0,tk.END):
            if instrument_name == 'lakeshore':
                self.measurebools[instrument_name] = True
                self.instruments[instrument_name].logging = True
            elif instrument_name == 'daq9211':
                self.measurebools[instrument_name] = True
                self.instruments[instrument_name].logging = True
            elif instrument_name == 'fluke8808a':
                self.measurebools[instrument_name] = True
                self.instruments[instrument_name].logging = True
            elif instrument_name == 'keithley':
                self.measurebools[instrument_name] = True
                self.instruments[instrument_name].logging = True
            else:
                return None
            self.selectedbox.insert(tk.END, instrument_name)

    def removeall(self):
        for instrument_name in self.selectedbox.get(0,tk.END):
            if instrument_name == 'lakeshore':
                self.measurebools[instrument_name] = False
                self.instruments[instrument_name].logging = False
            elif instrument_name == 'daq9211':
                self.measurebools[instrument_name] = False
                self.instruments[instrument_name].logging = False
            elif instrument_name == 'fluke8808a':
                self.measurebools[instrument_name] = False
                self.instruments[instrument_name].logging = False
            elif instrument_name == 'keithley':
                self.measurebools[instrument_name] = False
                self.instruments[instrument_name].logging = False
            else:
                return None
            self.selectedbox.delete(0,tk.END)

    def set_directory(self):
        filename = tkFileDialog.askdirectory(initialdir = 'C:\Users\Nate\Dropbox (Minnich Lab)\\', title = 'Select Experiment Directory')
        self.defaultdirectorystr.set(filename)

    def init_experiment(self):
        #create experiment folder
        time_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        #file_str = 'C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data' #replace this with a default path that can be set in the OS
        file_str = self.defaultdirectorystr.get()
        newfile_str = '%s\\experiment_%s' % (file_str, time_str)
        if not os.path.exists(newfile_str):
            os.makedirs(newfile_str)
            return newfile_str
        else:
            return -1

    def init_datafiles(self, instrument, instrument_directory):
        #Lakeshore
        if isinstance(instrument, lakeshore335):
            file_inputA = open('%s\\inputA.dat' % instrument_directory, 'w',0)
            file_inputB = open('%s\\inputB.dat' % instrument_directory, 'w',0)
            file_output1Amps = open('%s\\output1Amps.dat' % instrument_directory, 'w',0)
            file_output2Amps = open('%s\\output2Amps.dat' % instrument_directory, 'w',0)
            file_output1Percent = open('%s\\output1Percent.dat' % instrument_directory, 'w',0)
            file_output2Percent = open('%s\\output2Percent.dat' % instrument_directory, 'w',0)
            return [file_inputA, file_inputB, file_output1Amps , file_output2Amps, file_output1Percent, file_output2Percent]
        #Fluke
        if isinstance(instrument, fluke8808a):
            file_primary = open('%s\\primarydisplay.dat' % instrument_directory, 'w',0)
            file_secondary = open('%s\\secondarydisplay.dat' % instrument_directory, 'w',0)
            return [file_primary, file_secondary]
        #Keithley
        if isinstance(instrument, keithley2410):
            file_appliedBias = open('%s\\appliedbias.dat' % instrument_directory, 'w',0)
            file_measuredCurrent = open('%s\\measuredcurrent.dat' % instrument_directory, 'w',0)
            file_measuredResistance = open('%s\\measuredresistance.dat' % instrument_directory, 'w',0)
            return [file_appliedBias, file_measuredCurrent, file_measuredResistance]
        #DAQ
        if isinstance(instrument, daq9211):
            file_channel0 = open('%s\\channel0.dat' % instrument_directory, 'w',0)
            file_channel1 = open('%s\\channel1.dat' % instrument_directory, 'w',0)
            file_channel2 = open('%s\\channel2.dat' % instrument_directory, 'w',0)
            file_channel3 = open('%s\\channel3.dat' % instrument_directory, 'w',0)
            return [file_channel0, file_channel1, file_channel2, file_channel3]
        

    def log_click(self):
        if self.logging:
            #stop running
            self.logging_thread_event.set()
            self.logging = False
            self.loggingbtn.config(text = 'Enable Experiment Log')
            self.indicator_canvas.itemconfig(self.indicator, fill = "red4")
            self.indicatorstr.set('Not Logging')
            self.addnotebtn.config(state = tk.DISABLED)
        else:
            self.logging = True
            self.loggingbtn.config(text = 'Stop Experiment Log')
            self.indicator_canvas.itemconfig(self.indicator, fill = "green2")     
            self.indicatorstr.set('Logging...')
            #initial experiment directories
            file_str = self.init_experiment()
            self.file_notes = open('%s\\notes.dat' % file_str, 'a+',0)
            self.addnotebtn.config(state = tk.NORMAL)
            #create sub directory for each instrument that is logging
            for instrument_name, instrument in self.instruments.iteritems():
                if instrument.logging:
                    instrument_directory = '%s\\%s' % (file_str, instrument_name)
                    os.makedirs(instrument_directory)
                    #initialize data files
                    datafiles = self.init_datafiles(instrument, instrument_directory)
                    self.start_logthread(instrument, datafiles)

    def start_logthread(self, instrument, datafiles):
        t = threading.Thread(target = self.log_instrument, args = [instrument, datafiles])
        t.start()
        print "%s Log Thread-%d" % (instrument, t.ident)

    def log_instrument(self, instrument, datafiles):
        
        def write_lakeshore(data, data2write, file_index, time_delay):
            data2write.append('%s,%.3f\n' % (data[0], data[1]))
            if len(data2write) >= time_delay:
                for item in data2write:
                    datafiles[file_index].write(item)
                os.fsync
                data2write = []
            return data2write

        def write_fluke(data, data2write, file_index, time_delay):
            data2write.append('%s,%g,%s\n' % (data[0], data[1], data[2]))
            if len(data2write) >= time_delay:
                for item in data2write:
                    datafiles[file_index].write(item)
                os.fsync
                data2write = []
            return data2write      

        def write_keithley(data, data2write_list, time_delay):
            for indx, elem in enumerate(data2write_list):
                elem.append('%s,%g\n' % (data[0], data[indx+1]))
                if len(elem) >= time_delay:
                    for item in elem:
                        datafiles[indx].write(item)
                    os.fsync
                    elem = []
            return data2write_list  

        def write_daq(data, data2write_list, channel_index, time_delay):
            data2write_list[channel_index].append('%s,%g\n' % (data[0], data[1]))
            if len(data2write_list[channel_index]) >= time_delay:
                for item in data2write_list[channel_index]:
                    datafiles[channel_index].write(item)
                os.fsync
                data2write_list[channel_index] = []
            return data2write_list
        
        self.logging_thread_event.clear()            

        #lakeshore
        data2write_inputA = []
        data2write_inputB = []
        data2write_output1Amps = []
        data2write_output2Amps = []
        data2write_output1Percent = []
        data2write_output2Percent = []
        #fluke
        data2write_primary = []
        data2write_secondary = []
        #keithley
        data2write_keithleylist = [ [], [], [] ]
        #daq
        data2write_daqlist = [[], [], [], [] ]
        while(not self.logging_thread_event.is_set()):
            #lakeshore
            if isinstance(instrument, lakeshore335):
                while not (instrument.inputA_logq.empty()):
                    #temperature from input A 
                    data2write_inputA = write_lakeshore(instrument.inputA_logq.get(), data2write_inputA, 0, float(self.time_delay.get()))
                while not (instrument.inputB_logq.empty()):
                    data2write_inputB = write_lakeshore(instrument.inputB_logq.get(), data2write_inputB, 1, float(self.time_delay.get()))
                while not (instrument.output1Amps_logq.empty()):
                    data2write_output1Amps = write_lakeshore(instrument.output1Amps_logq.get(), data2write_output1Amps, 2, float(self.time_delay.get()))
                while not (instrument.output2Amps_logq.empty()):
                    data2write_output2Amps = write_lakeshore(instrument.output2Amps_logq.get(), data2write_output2Amps, 3, float(self.time_delay.get()))
                while not (instrument.output1Percent_logq.empty()):
                    data2write_output1Percent = write_lakeshore(instrument.output1Percent_logq.get(), data2write_output1Percent, 4, float(self.time_delay.get()))
                while not (instrument.output2Percent_logq.empty()):
                    data2write_output2Percent = write_lakeshore(instrument.output2Percent_logq.get(), data2write_output2Percent, 5, float(self.time_delay.get()))
            #fluke
            if isinstance(instrument, fluke8808a):
                while not (instrument.primary_logq.empty()):
                    data2write_primary = write_fluke(instrument.primary_logq.get(), data2write_primary, 0, float(self.time_delay.get()))
                while not (instrument.secondary_logq.empty()):
                    data2write_secondary = write_fluke(instrument.secondary_logq.get(), data2write_secondary, 1, float(self.time_delay.get()))
            #keithley
            if isinstance(instrument, keithley2410):
                while not (instrument.data_logq.empty()):
                    data2write_keithleylist = write_keithley(instrument.data_logq.get(), data2write_keithleylist, float(self.time_delay.get()))
            ##daq
            if isinstance(instrument, daq9211):
                for k in range(0,len(instrument.channels)):
                    while (not instrument.channels[k].data_logq.empty()):
                        data = instrument.channels[k].data_logq.get()
                        data2write_daqlist = write_daq(data, data2write_daqlist, k, float(self.time_delay.get()))

    def addnote(self):
        #get note from note2addentry
        #str2write = '%s, %s\n' % (datetime.datetime.now(), self.note2addstr.get())
        str2write = '%s, %s' % (datetime.datetime.now(), self.note2addentry.get(1.0,tk.END))
        self.file_notes.write(str2write)
        os.fsync
        time.sleep(0.1)
        self.file_notes.seek(0)
        self.addednotestext.delete(1.0,tk.END)
        #read all notes and insert them into addednotestext
        for line in self.file_notes:
            self.addednotestext.insert(tk.END, line)

        
         
     




