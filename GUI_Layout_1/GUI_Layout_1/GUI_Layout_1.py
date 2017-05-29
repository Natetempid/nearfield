
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
from lakeshore335 import lakeshore335
from daq9211 import daq9211
from usbswitch import usbswitch
from fluke8808a import fluke8808a
from frame_lakeshore_measure import lakeshore_measure_frame
from frame_lakeshore_command import lakeshore_command_frame
from frame_lakeshore_config import lakeshore_config_frame
from frame_lakeshore_input import lakeshore_input_frame
from frame_daq_config import daq_config_frame
from frame_daq_measure import daq_measure_frame
from frame_usbswitch_diagram import usbswitch_diagram_frame
import ttk
import pyvisa

#lkshr = lakeshore335('ASRL3::INSTR')
LARGE_FONT= ("Verdana", 12)

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.instruments = {'lakeshore': None, 'fluke': None, 'keithley': None, 'usbswitch' : None}
        
        ##############################
        ## Instrument Configuration ##
        ##############################
        self.start_frame = start_frame(self)
        self.start_frame.grid(row = 0, column = 0, sticky = 'nsew')


class start_frame(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        #start_frame.grid_rowconfigure(0, weight=1)
        self.master = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.label = tk.Label(self, text="Instrument Configuration", justify = tk.CENTER, font = ("tkDefaultFont",24))
        self.label.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        
        #listbox for master instrument dictionary entries
        self.instrumentbox_lbl = tk.LabelFrame(self, text = "Instruments", font = ("tkDefaultFont",22))
        self.instrumentbox_lbl.grid(row = 1, column = 0, sticky = 'ew')
        self.instrumentbox = tk.Listbox(self, exportselection=False)
        self.instrumentbox.grid(row = 2, column = 0, sticky ='ew', padx = 5)
        for item in master.instruments.keys():
            self.instrumentbox.insert(tk.END, item)
        
        #listbox for serial devices
        self.serialbox_lbl = tk.LabelFrame(self, text = "Instruments", font = ("tkDefaultFont",22))
        self.serialbox_lbl.grid(row = 1, column = 1, sticky = 'ew')
        self.serialbox = tk.Listbox(self, exportselection=False)
        self.serialbox.grid(row = 2, column = 1, sticky ='ew', padx = 5)
        for item in pyvisa.ResourceManager().list_resources():
            self.serialbox.insert(tk.END, item)

        self.btnframe = tk.Frame(self, borderwidth = 5)
        self.btnframe.grid(row = 3, column = 0, columnspan = 2, sticky = 'ew')
        self.init_btn = ttk.Button(self.btnframe, text = 'Initialize Instrument', command = lambda: self.init_instrument())
        self.init_btn.grid(row = 0, column = 0, sticky = 'ew')
        self.complete_btn = ttk.Button(self.btnframe, text = 'Initialization Complete', command = lambda: self.complete_init())
        self.complete_btn.grid(row = 1, column = 0, sticky = 'ew')
    
    def init_instrument(self):
        instrument_name = self.instrumentbox.get(self.instrumentbox.curselection()[0])
        serial_name = self.serialbox.get(self.serialbox.curselection()[0])
        #initialize proper instrument
        if instrument_name == 'lakeshore':
            self.master.instruments[instrument_name] = lakeshore335(serial_name)
        elif instrument_name == 'fluke':
            self.master.instruments[instrument_name] = fluke8808a(serial_name)
        elif instrument_name == 'keithley':
            self.master.instruments[instrument_name] = None
        elif instrument_name == 'usbswitch':
            self.master.instruments[instrument_name] = usbswitch(serial_name)
        else:
            return None
     
    def complete_init(self):
        #initialize the program_frame
        self.master.instruments['daq9211'] = daq9211('cDAQ1Mod1')
        self.master.program_frame = program_frame(self.master)
        self.master.program_frame.grid(row = 0, column = 0, sticky = 'nsew')
        
class program_frame(tk.Frame):

    def __init__(self, master):
        lakeshore = master.instruments['lakeshore']
        fluke = master.instruments['fluke']
        keithley = master.instruments['keithley']
        daq9211 = master.instruments['daq9211']
        usbswitch = master.instruments['usbswitch']

        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.btnframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.btnframe.grid(row = 0, column = 0, sticky = 'nsew')#.pack(side = "left", fill = "both", padx = 5, pady = 5)
        self.btn2 = tk.Button(self.btnframe, text = "LakeShore Measure", command = lambda: self.show_frame(lakeshore_measure_frame), width = 30)
        self.btn2.grid(row = 1, column = 0)
        self.btn3 = tk.Button(self.btnframe, text = "LakeShore Heater Config", command = lambda: self.show_frame(lakeshore_config_frame), width = 30)
        self.btn3.grid(row = 2, column = 0)
        self.btn4 = tk.Button(self.btnframe, text = "LakeShore Input Config", command = lambda: self.show_frame(lakeshore_input_frame), width = 30)
        self.btn4.grid(row = 3, column = 0)
        self.btnEnd = tk.Button(self.btnframe, text = "LakeShore Command Prompt", command = lambda: self.show_frame(lakeshore_command_frame), width = 30)
        self.btnEnd.grid(row = 4, column = 0)
        self.btndaq1 = tk.Button(self.btnframe, text = "DAQ Config", command = lambda: self.show_frame(daq_config_frame), width = 30)
        self.btndaq1.grid(row = 5, column = 0)
        self.btndaq2 = tk.Button(self.btnframe, text = "DAQ Measure", command = lambda: self.show_frame(daq_measure_frame), width = 30)
        self.btndaq2.grid(row = 6, column = 0)
        self.btnusb1 = tk.Button(self.btnframe, text = "USB Switch", command = lambda: self.show_frame(usbswitch_diagram_frame), width = 30)
        self.btnusb1.grid(row = 7, column = 0)

       

        self.container = tk.Frame(self)
        self.container.grid(row = 0, column = 1, sticky = 'nsew') #.pack(side="right", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (lakeshore_measure_frame, lakeshore_command_frame, lakeshore_config_frame, lakeshore_input_frame, daq_config_frame, daq_measure_frame, usbswitch_diagram_frame):
            if "lakeshore" in F.__name__:
                frame = F(self.container, self, lakeshore)
            elif "daq" in F.__name__:
                frame = F(self.container, self, daq9211)
            elif "usbswitch" in F.__name__:
                frame = F(self.container, self, usbswitch)
            else:
                frame = F(self.container, self, None)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")  

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

def main():
    app = GraphTk()
    app.geometry('1500x900')
    app.mainloop()
    app.instruments['lakeshore'].close()
    app.instruments['daq9211'].close()
    app.instruments['usbswitch'].close()

if __name__ == '__main__':
    main()