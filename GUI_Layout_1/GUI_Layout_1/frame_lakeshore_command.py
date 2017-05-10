
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

class lakeshore_command_frame(tk.Frame):
    def __init__(self, master, controller, lakeshore):
        tk.Frame.__init__(self, master)
        self.lakeshore = lakeshore
        response_frame = tk.Frame(self)
        response_frame.pack(side = "top", fill = tk.BOTH, expand = True)
        response_frame.grid_rowconfigure(0, weight = 1)
        response_frame.grid_columnconfigure(0,weight = 1)
        
        self.v = tk.StringVar()
        self.response_txt = tk.Text(response_frame, background = "white", )
        self.response_txt.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)
        self.scrollb = ttk.Scrollbar(response_frame, command = self.response_txt.yview)
        self.scrollb.grid(row = 0, column = 1, sticky = 'nsew')
        self.response_txt['yscrollcommand'] = self.scrollb.set
        
        entry_frame = ttk.Frame(self)
        entry_frame.pack(side = "bottom", fill = tk.X, expand = True)
        entry_frame.grid_rowconfigure(0, weight = 1)
        entry_frame.grid_columnconfigure(0, weight = 1)
                
        self.entry = ttk.Entry(entry_frame, background = "white")
        self.entry.pack(side = "left", fill = tk.X, expand = True, padx = 5, pady = 5)

        self.btn_send = ttk.Button(entry_frame, text = "Send", command = lambda: self.send_query())
        self.btn_send.pack(side = "left")

    def send_query(self):
        if self.lakeshore.stop_event.is_set():
            send_str = self.entry.get()
            receive_str = self.lakeshore.lakestr2str(self.lakeshore.ctrl.query(send_str))
            time_str = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
            self.response_txt.insert(tk.END, "[Send %s]: %s\n[Receive %s]: %s\n" % (time_str, send_str, time_str, receive_str))   
        else:
            self.response_txt.insert(tk.END, "[ERROR %s]: LakeShore thread is currently active\n" % str(datetime.datetime.now().time().strftime("%H:%M:%S")))
            #self.threadtext.set('No')
            #self.threadlbl.config(background = 'red')