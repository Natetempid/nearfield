
import Tkinter as tk
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
from lakeshore335 import lakeshore335
from daq9211 import daq9211
from usbswitch import usbswitch
from fluke8808a import fluke8808a
from keithley2410 import keithley2410
from frame_lakeshore_measure import lakeshore_measure_frame
from frame_instrument_command import instrument_command_frame
from frame_lakeshore_config import lakeshore_config_frame
from frame_lakeshore_input import lakeshore_input_frame
from frame_lakeshore_control import lakeshore_control_frame
from frame_daq_config import daq_config_frame
from frame_daq_measure import daq_measure_frame
from frame_usbswitch_diagram import usbswitch_diagram_frame
from frame_fluke8808a_control import fluke8808a_control_frame
from frame_keithley_control import keithley_control_frame
from frame_save import save_frame
import ttk
import pyvisa

#lkshr = lakeshore335('ASRL3::INSTR')
LARGE_FONT= ("Verdana", 12)

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.instruments = {'lakeshore': None, 'fluke8808a': None, 'keithley': None, 'usbswitch' : None}
        
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
        self.root = master #the master is the GraphTk instance
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)
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

        #listbox for initialized devices
        self.initframe_lbl = tk.LabelFrame(self, text = "Initialized Instruments", font = ("tkDefaultFont",22))
        self.initframe_lbl.grid(row = 1, column = 2, sticky = 'ew')
        self.initbox = tk.Listbox(self, exportselection = False)
        self.initbox.grid(row = 2, column = 3, sticky = 'ew', padx = 5)
        
        self.btnframe = tk.Frame(self, borderwidth = 5)
        self.btnframe.grid(row = 2, column = 2, sticky = 'ew') 
        self.btnframe.grid_columnconfigure(0,weight = 1)
        self.init_btn = ttk.Button(self.btnframe, text = 'Initialize Instrument', command = lambda: self.init_instrument())
        self.init_btn.grid(row = 0, column = 0, sticky = 'ew')
        self.setdefault_btn = ttk.Button(self.btnframe, text = 'Set Default', command = lambda:self.set_default())
        self.setdefault_btn.grid(row = 1, column = 0, sticky = 'ew')
        self.loaddefault_btn = ttk.Button(self.btnframe, text = 'Load Default', command = lambda:self.load_default())
        self.loaddefault_btn.grid(row = 2, column = 0, sticky = 'ew')

     
        self.complete_btn = ttk.Button(self, text = 'Initialization Complete', command = lambda: self.complete_init())
        self.complete_btn.grid(row = 3, column = 0, sticky = 'nw', padx = 5)

    
    def init_instrument(self):
        instrument_name = self.instrumentbox.get(self.instrumentbox.curselection()[0])
        serial_name = self.serialbox.get(self.serialbox.curselection()[0])
        #initialize proper instrument
        if instrument_name == 'lakeshore':
            self.master.instruments[instrument_name] = lakeshore335(serial_name)
        elif instrument_name == 'fluke8808a':
            self.master.instruments[instrument_name] = fluke8808a(serial_name)
        elif instrument_name == 'keithley':
            self.master.instruments[instrument_name] = keithley2410(serial_name)
        elif instrument_name == 'usbswitch':
            self.master.instruments[instrument_name] = usbswitch(serial_name)
        else:
            return None
        self.initbox.insert(tk.END,'%s,%s' % (instrument_name, serial_name))

    def complete_init(self):
        #initialize the program_frame
        self.master.instruments['daq9211'] = daq9211('cDAQ1Mod1')
        self.master.program_frame = program_frame(self.master)
        self.master.program_frame.grid(row = 0, column = 0, sticky = 'nsew')

    def set_default(self):            
        today = datetime.date.today().strftime('%Y%m%d')
        config_name = 'defaultinstruments_%s' % (today)
        f = tkFileDialog.asksaveasfile(mode = 'w', initialdir = 'defaultinstruments', initialfile = config_name, defaultextension = '.dat')
        for str_elem in self.initbox.get(0,tk.END):
            f.write('%s\n' % str_elem)
        return None

    def load_default(self):
        f = tkFileDialog.askopenfile(initialdir = 'defaultinstruments', defaultextension = '.dat')
        for line in f:
            [instrument_name, serial_name] = line.strip('\n').split(',')
            if instrument_name == 'lakeshore':
                self.master.instruments[instrument_name] = lakeshore335(serial_name)
            elif instrument_name == 'fluke8808a':
                self.master.instruments[instrument_name] = fluke8808a(serial_name)
            elif instrument_name == 'keithley':
                self.master.instruments[instrument_name] = keithley2410(serial_name)
            elif instrument_name == 'usbswitch':
                self.master.instruments[instrument_name] = usbswitch(serial_name)
            else:
                return None
            self.initbox.insert(tk.END,'%s,%s' % (instrument_name, serial_name))    
        
class program_frame(tk.Frame):

    def __init__(self, master):
        self.master = master #master is the instance of GraphTk
        lakeshore = master.instruments['lakeshore']
        fluke8808a = master.instruments['fluke8808a']
        keithley = master.instruments['keithley']
        daq9211 = master.instruments['daq9211']
        usbswitch = master.instruments['usbswitch']

        tk.Frame.__init__(self, master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.btnframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.btnframe.grid(row = 0, column = 0, sticky = 'nsew')#.pack(side = "left", fill = "both", padx = 5, pady = 5)
        self.btnlakeshorectrl = tk.Button(self.btnframe, text = "Lakeshore 335 Control", command = lambda: self.show_frame(lakeshore_control_frame), width = 30)
        self.btnlakeshorectrl.grid(row = 1, column = 0)
        self.btn2 = tk.Button(self.btnframe, text = "LakeShore Measure", command = lambda: self.show_frame(lakeshore_measure_frame), width = 30)
        self.btn2.grid(row = 2, column = 0)
        #self.btn3 = tk.Button(self.btnframe, text = "LakeShore Heater Config", command = lambda: self.show_frame(lakeshore_config_frame), width = 30)
        #self.btn3.grid(row = 2, column = 0)
        #self.btn4 = tk.Button(self.btnframe, text = "LakeShore Input Config", command = lambda: self.show_frame(lakeshore_input_frame), width = 30)
        #self.btn4.grid(row = 3, column = 0)
        
        self.btnEnd = tk.Button(self.btnframe, text = "Instrument Command Prompt", command = lambda: self.show_frame(instrument_command_frame), width = 30)
        self.btnEnd.grid(row = 10, column = 0)
        self.btndaq1 = tk.Button(self.btnframe, text = "DAQ Config", command = lambda: self.show_frame(daq_config_frame), width = 30)
        self.btndaq1.grid(row = 5, column = 0)
        self.btndaq2 = tk.Button(self.btnframe, text = "DAQ Measure", command = lambda: self.show_frame(daq_measure_frame), width = 30)
        self.btndaq2.grid(row = 6, column = 0)
        #self.btnusb1 = tk.Button(self.btnframe, text = "USB Switch", command = lambda: self.show_frame(usbswitch_diagram_frame), width = 30)
        #self.btnusb1.grid(row = 7, column = 0)
        self.btnfluke1 = tk.Button(self.btnframe, text = "Fluke8808a Control", command = lambda: self.show_frame(fluke8808a_control_frame), width = 30)
        self.btnfluke1.grid(row = 8, column = 0)
        self.btnkeithley1 = tk.Button(self.btnframe, text = "Keithley 2410 Control", command = lambda: self.show_frame(keithley_control_frame), width = 30)
        self.btnkeithley1.grid(row = 9, column = 0)
    
        self.btnsaveexp = tk.Button(self.btnframe, text = "Log Experiment Data", command = lambda: self.show_frame(save_frame), width = 30)
        self.btnsaveexp.grid(row = 11, column = 0)

       

        self.container = tk.Frame(self)
        self.container.grid(row = 0, column = 1, sticky = 'nsew') #.pack(side="right", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (lakeshore_measure_frame, instrument_command_frame, lakeshore_control_frame, daq_config_frame, daq_measure_frame, fluke8808a_control_frame, keithley_control_frame, save_frame):
            if "lakeshore" in F.__name__:
                frame = F(self.container, self, self.master, lakeshore) #master is the GraphTk instance
            elif "daq" in F.__name__:
                frame = F(self.container, self, daq9211)
            elif "usbswitch" in F.__name__:
                frame = F(self.container, self, usbswitch)
            elif "fluke8808a" in F.__name__:
                frame = F(self.container, self, usbswitch, fluke8808a)
            elif "keithley" in F.__name__:
                frame = F(self.container, self, keithley, fluke8808a)
            elif "command" in F.__name__:
                frame = F(self.container, self, master.instruments)
            elif "save" in F.__name__:
                frame = F(self.container, self, master.instruments)
            else:
                frame = F(self.container, self, None)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")  

    def show_frame(self, cont):

        frame = self.frames[cont]
        #stop graphs from all other frames
        for loop_frame in (lakeshore_measure_frame, daq_measure_frame, fluke8808a_control_frame, keithley_control_frame):
            self.frames[loop_frame].stop_graph()
        frame.tkraise()

def main():
    app = GraphTk()
    app.geometry('1750x1000')
    app.mainloop()
    app.instruments['lakeshore'].close()
    app.instruments['daq9211'].close()
    app.instruments['usbswitch'].close()

if __name__ == '__main__':
    main()