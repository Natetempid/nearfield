
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from lakeshore335 import lakeshore335
from keithley2410 import keithley2410
from fluke8808a import fluke8808a

import matplotlib.animation as animation
import datetime
import ttk

class instrument_command_frame(tk.Frame):
    def __init__(self, master, controller, instruments):
        tk.Frame.__init__(self, master)
        #self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight = 1)
        self.grid_columnconfigure(0,weight = 1)
        self.instruments = instruments
        self.lakeshore = self.instruments['lakeshore']
        self.fluke8808a = self.instruments['fluke8808a']
        self.keithley = self.instruments['keithley']
        self.selectedinstrument = self.lakeshore

        self.instrument_frame = tk.Frame(self)
        self.instrument_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.instrument_frame.grid_rowconfigure(0,weight=1)
        self.instrument_frame.grid_columnconfigure(0,weight=1)
        self.instrumentstr = tk.StringVar()
        self.instrumentlist = self.instruments.keys()
        self.instrumentstr.set(self.instrumentlist[0])
        self.instrumentmenu = ttk.OptionMenu(self.instrument_frame, self.instrumentstr, self.instrumentlist[0], *self.instrumentlist)
        self.instrumentmenu.grid(row = 0, column = 0, sticky = 'nsew')
        self.setinstrumentbtn = ttk.Button(self.instrument_frame, text = "Set Instrument", command = lambda: self.set_instrument())
        self.setinstrumentbtn.grid(row = 0, column = 1, sticky = 'wns')

        self.response_frame = tk.Frame(self)
        self.response_frame.grid(row = 1, column = 0, sticky = 'nsew')
        self.response_frame.grid_rowconfigure(0, weight = 1)
        self.response_frame.grid_columnconfigure(0,weight = 1)
        
        self.v = tk.StringVar()
        self.response_txt = tk.Text(self.response_frame, background = "white", )
        self.response_txt.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.scrollb = ttk.Scrollbar(self.response_frame, command = self.response_txt.yview)
        self.scrollb.grid(row = 0, column = 1, sticky = 'nsew')
        self.response_txt['yscrollcommand'] = self.scrollb.set
        
        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row = 2, column = 0, sticky = 'ew')
        self.entry_frame.grid_rowconfigure(0, weight = 1)
        self.entry_frame.grid_columnconfigure(0, weight = 1)
                
        self.entry = ttk.Entry(self.entry_frame, background = "white")
        self.entry.pack(side = "left", fill = tk.X, expand = True, padx = 5, pady = 5)

        self.btn_send = ttk.Button(self.entry_frame, text = "Send", command = lambda: self.send_query())
        self.btn_send.pack(side = "left")

    def send_query(self):
        if isinstance(self.selectedinstrument, lakeshore335):
            if self.lakeshore.stop_event.is_set():
                send_str = self.entry.get()
                receive_str = self.lakeshore.lakestr2str(self.lakeshore.ctrl.query(send_str))
                time_str = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
                self.response_txt.insert(tk.END, "[Lakeshore Send %s]: %s\n[Receive %s]: %s\n" % (time_str, send_str, time_str, receive_str))   
            else:
                self.response_txt.insert(tk.END, "[Lakeshore ERROR %s]: LakeShore thread is currently active\n" % str(datetime.datetime.now().time().strftime("%H:%M:%S")))
                #self.threadtext.set('No')
                #self.threadlbl.config(background = 'red')
        
        if isinstance(self.selectedinstrument, keithley2410):
            send_str = self.entry.get()
            receive_str = self.keithley.ctrl.query(send_str)
            time_str = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
            self.response_txt.insert(tk.END, "[Keithley Send %s]: %s\n[Receive %s]: %s\n" % (time_str, send_str, time_str, receive_str))   
    def set_instrument(self):
        self.selectedinstrument = self.instruments[self.instrumentstr.get()]