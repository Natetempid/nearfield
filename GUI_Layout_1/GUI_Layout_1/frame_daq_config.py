import PyDAQmx
from daq9211 import *

import Tkinter as tk
import tkFileDialog
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

class daq_config_frame(tk.Frame):
    def __init__(self, master, controller, daq9211):
        tk.Frame.__init__(self,master)
        self.master = master
        self.daq9211 = daq9211
        self.selectedchannel = tk.IntVar()
        self.selectedchannel.set(0)
        #keep track of raised tc or voltage frames
        self.selectedframes = [None, None, None, None]


        #self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        #self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(3, weight = 1)
        self.label = tk.Label(self, text="DAQ Configuration", justify = tk.CENTER, font = ("tkDefaultFont",24))
        self.label.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        
        #add button frame to add and delete channels
        self.btnframe = tk.Frame(self)
        self.btnframe.grid(row = 1, column = 0, sticky = 'ne')
        self.selectedlbl_str = tk.StringVar()
        self.selectedlbl_str.set('Selected Channel: %d' % self.selectedchannel.get())
        self.selectedlbl = tk.Label(self.btnframe, textvariable = self.selectedlbl_str, font = ("tkDefaultFont",16))
        self.selectedlbl.grid(row = 0, column = 0, sticky = 'ew')
        self.addtcbtn = ttk.Button(self.btnframe, text = "Add Thermocouple", command = lambda: self.raise_frame(self.thermocouple_frames[self.selectedchannel.get()]))
        self.addtcbtn.grid(row = 1, column = 0, sticky = 'ew')
        self.addvolbtn = ttk.Button(self.btnframe, text = "Add Analog Voltage", command = lambda: self.raise_frame(self.voltage_frames[self.selectedchannel.get()]))
        self.addvolbtn.grid(row = 2, column = 0, sticky = 'ew')
        
        # ID frames - consisting of btn_ID_frames
        self.btn_ID_frame = tk.Frame(self,borderwidth = 5, relief = tk.GROOVE)
        self.btn_ID_frame.grid(row = 2, column = 0, sticky = 'new')
        for i in range (0,4):
            self.btn_ID_frame.grid_rowconfigure(i, weight = 1)
        self.btn_ID_frame.grid_columnconfigure(0, weight = 1)
        self.channelID_frames = []
        for i in range(0,4):
            self.channelID_frames.append(daq_channelID_frame(self.btn_ID_frame,controller,daq9211,i))
            self.channelID_frames[i].grid(row = i, column = 0, sticky = 'nsew')
        
        self.configbtn_frame = tk.Frame(self)
        self.configbtn_frame.grid_columnconfigure(0,weight = 1)
        self.configbtn_frame.grid(row = 3, column = 0, sticky = 'new')
        self.openconfig_btn = ttk.Button(self.configbtn_frame, text = "Open Config", command = lambda: self.open_config())
        self.openconfig_btn.grid(row = 0, column = 0, sticky = 'nsew')
        self.saveconfig_btn = ttk.Button(self.configbtn_frame, text = "Save Config", command = lambda: self.save_config())
        self.saveconfig_btn.grid(row = 1, column = 0, sticky = 'nsew')
    
        # tc and voltage frames
        self.mainchannelframe = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.mainchannelframe.grid(row = 1, column = 1, rowspan = 3, sticky = 'nsew')
        self.mainchannelframe.grid_columnconfigure(0, weight = 1)
        self.mainchannelframe.grid_rowconfigure(0, weight = 1)
        self.mainchannelframe.grid_rowconfigure(1, weight = 1)
        self.mainchannelframe.grid_rowconfigure(2, weight = 1)
        self.mainchannelframe.grid_rowconfigure(3, weight = 1)
        
        #tc channel frame
        self.thermocouple_frames = []
        for i in range(0,4):
            self.thermocouple_frames.append(daq_thermocouple_frame(self.mainchannelframe,controller,daq9211,i))
            self.thermocouple_frames[i].grid(row = i, column = 0, sticky = 'nsew')
        
        #voltage channel frame
        self.voltage_frames = []
        for i in range(0,4):
            self.voltage_frames.append(daq_voltage_frame(self.mainchannelframe,controller,daq9211,i))
            self.voltage_frames[i].grid(row = i, column = 0, sticky = 'nsew')

        #raise the click frames
        for frame in self.channelID_frames:
            frame.tkraise()
        
        #add frame to record configuration of daq instance
        self.config_frame = tk.Frame(self, borderwidth = 5, relief = tk.GROOVE)
        self.config_frame.grid(row = 1, column = 2, rowspan = 3, sticky = 'nsew')
        self.config_frame.grid_columnconfigure(0, weight = 1)
        self.config_frame.grid_columnconfigure(1, weight = 1)
        self.config_frame.grid_rowconfigure(1, weight = 1)
        #list box to show configureations
        self.config_lbl = tk.Label(self.config_frame, text = "Configured Channels", font = ("tkDefaultFont", 14))
        self.config_lbl.grid(row = 0, column = 0, columnspan = 2, sticky = 'new')
        self.config_listbox = tk.Listbox(self.config_frame)
        self.config_listbox.grid(row = 1, rowspan = 2, column = 0, columnspan = 2, sticky = 'nsew')
      #  self.setuptask_btn = ttk.Button(self.config_frame, text = 'Setup Channel Tasks', command = lambda: self.run_tasksetup())
       # self.setuptask_btn.grid(row = 3, column = 0, columnspan = 2, sticky = 'ew')

    def raise_frame(self, frame):
        self.selectedframes[self.selectedchannel.get()] = frame
        frame.tkraise()

    def open_config(self):
        f = tkFileDialog.askopenfile(initialdir = 'daq_config', defaultextension = '.dat')
       
        for line in f:
            if "Channel" in line:
                #get the channel ID
                channel_ID =  int(line.strip('Channel: ').strip('\n'))
                self.selectedchannel.set(channel_ID)
            if "Sensor" in line:
                if "Thermocouple" in line:
                    selected_frame = self.thermocouple_frames[self.selectedchannel.get()]
                    selected_frame.ID = channel_ID
                    self.raise_frame(selected_frame)
                elif "Voltage" in line:
                    selected_frame = voltage_frames[self.selectedchannel.get()]
                    selected_frame.ID = channel_ID
                    self.raise_frame(selected_frame)
                else:
                    selected_frame = None
            if "Type" in line:
                selected_frame.type_str.set(line.strip('Type: ').strip('\n'))
            if "Min" in line:
                selected_frame.min_str.set(line.strip('Min: ').strip('\n'))
            if "Max" in line:
                selected_frame.max_str.set(line.strip('Max: ').strip('\n'))
                #self.selectedchannel.set()#set the selected channel to be the one from the file
            if "CJC" in line:
                selected_frame.cjc_str.set(line.strip('CJC: ').strip('\n'))
            

    def save_config(self):
        #get configs from each of the 4 channel frames
        today = datetime.date.today().strftime('%Y%m%d')
        config_name = 'daq9211_%s' % today
        f = tkFileDialog.asksaveasfile(mode = 'w', initialdir = 'daq_config', initialfile = config_name, defaultextension = '.dat')
        for i in range(0,4):
            data = self.get_channel_info(i)
            if data is not None:
                if data['sensor'] == 'Thermocouple':
                    #write thermocouple config_str
                    config_str = 'Channel: %d\nSensor: Thermocouple\nType: %s\nMin: %s\nMax: %s\nCJC: %s\n' % (data['ID'], data['type'], data['min'], data['max'], data['cjc'])
                    f.write(config_str)
                elif data['sensor'] == 'Voltage':
                    #write voltage config_str
                    config_str = 'Channel: %d\n, Sensor: Voltage\n' % (data['ID'])
                    f.write(config_str)
                else:
                    config_str = ""

    def get_channel_info(self,ID):
        frame = self.selectedframes[ID]
        data = {}
        if isinstance(frame, daq_thermocouple_frame):
            data['sensor'] = 'Thermocouple'
            data['ID'] = frame.ID
            data['type'] = frame.type_str.get()
            data['min'] = frame.min_str.get()
            data['max'] = frame.max_str.get()
            data['cjc'] = frame.cjc_str.get()
            return data
        elif isinstance(frame,daq_voltage_frame):
            data['sensor'] = 'Voltage'
            data['ID'] = frame.ID


        else:
            return None

    def run_tasksetup(self):
        for i in range(0,len(self.daq9211.channels)):
            self.daq9211.channels[i].setup_task()

    



class daq_channelID_frame(tk.Frame):
    def __init__(self, master, controller, daq9211, ID):
        tk.Frame.__init__(self,master)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.ID = ID
        self.btn = tk.Button(self,text = '%d' % self.ID, font = ("tkDefaultFont",16), command = lambda: self.update_selectedchannel())
        self.btn.grid(row = 0, column = 0, sticky = 'nsew')
    def update_selectedchannel(self):
        self.master.master.selectedchannel.set(self.ID)
        self.master.master.selectedlbl_str.set('Selected Channel: %d' % self.master.master.selectedchannel.get())

class daq_thermocouple_frame(tk.Frame):
    def __init__(self, master, controller, daq9211, ID):
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE)
        self.grid_rowconfigure(7, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
       # self.grid_columnconfigure(2, weight = 1)
        self.ID = ID
        self.daq9211 = daq9211
        self.lbl = tk.Label(self, text = 'Thermocouple: Channel %d' % self.ID, font = ("tkDefaultFont",14))
        self.lbl.grid(row = 0, column = 0, sticky = 'nw')

        #thermocouple type menu
        self.type_lbl = tk.Label(self, text = 'Thermocouple Type', font = ("tkDefaultFont",12))
        self.type_lbl.grid(row = 1, column = 0, columnspan = 2, sticky = 'nw' )
        self.type_str = tk.StringVar()
        #self.type_list = ["J","K","N","R","S","T","B","E"]
        self.type_list = ["K", "E"]
        self.type_str.set(self.type_list[0])
        self.type_menu = ttk.OptionMenu(self, self.type_str, self.type_list[0], *self.type_list)
        self.type_menu.grid(row = 2, column = 0, columnspan = 2, sticky = 'nw')
        
        self.min_lbl = tk.Label(self, text = 'Temperature Min', font = ("tkDefaultFont", 12))
        self.min_lbl.grid(row = 3, column = 0, sticky = 'nw')
        self.min_str = tk.StringVar()
        self.min_str.set('77')
        self.min_entry = tk.Entry(self, textvariable = self.min_str)
        self.min_entry.grid(row = 4, column = 0, sticky = 'nw')        
        
        self.max_lbl = tk.Label(self, text = 'Temperature Max', font = ("tkDefaultFont", 12))
        self.max_lbl.grid(row = 3, column = 1, sticky = 'nw')
        self.max_str = tk.StringVar()
        self.max_str.set('1000')
        self.max_entry = tk.Entry(self, textvariable = self.max_str)
        self.max_entry.grid(row = 4, column = 1, padx = 10, sticky = 'nw')

        self.cjc_lbl = tk.Label(self, text = 'Cold Junction Compensation', font = ("tkDefaultFont",12))
        self.cjc_lbl.grid(row = 5, column = 0, sticky = 'nw' )
        self.cjc_str = tk.StringVar()
        self.cjc_list = ["Built-in", "Constant"]
        self.cjc_str.set(self.type_list[0])
        self.cjc_menu = ttk.OptionMenu(self, self.cjc_str, self.cjc_list[0], *self.cjc_list)
        self.cjc_menu.grid(row = 6, column = 0, columnspan = 2, sticky = 'nw')
        

        self.config_btn = ttk.Button(self, text = 'Configure Channel', command = lambda: self.config_channel())
        self.config_btn.grid(row = 1, column = 2, rowspan = 7, padx = 5, sticky = 'nsew')


    def config_channel(self):
        #master is the mainchannel frame
        #master.master is daq_config_frame
        #self.ID is the channel ID
        #add channel information to listbox in master.master.config_listbox
        tc = thermocouple(self.type_str.get(), self.min_str.get(), self.max_str.get(), self.cjc_str.get())
        chan = channel('%s/ai%d' % (self.daq9211.name, self.ID), tc, int(self.ID))
        self.daq9211.add_channel(chan)
        item_str = "Channel: %s" % (chan.name)
        time_item_str = '[%s] %s' % (str(datetime.datetime.now().time().strftime("%H:%M:%S")),item_str)
        #first get all elements in the listbox
        all_elements = self.master.master.config_listbox.get(0,tk.END)
        for index, elem in enumerate(all_elements):
            if item_str in elem: #then the channel corresponding to index has been configured and needs to be overwritten
                self.master.master.config_listbox.delete(index)
        self.master.master.config_listbox.insert(tk.END, time_item_str)

class daq_voltage_frame(tk.Frame):
    def __init__(self, master, controller, daq9211, ID):
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE, width = 100, height = 50)
        self.grid_rowconfigure(1,weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
       # self.grid_columnconfigure(2, weight = 1)
        self.ID = ID
        self.daq9211 = daq9211
        self.lbl = tk.Label(self, text = 'Voltage: Channel %d' % self.ID, font = ("tkDefaultFont",14))
        self.lbl.grid(row = 0, column = 0, sticky = 'nw')
        self.config_btn = ttk.Button(self, text = 'Configure Channel', command = lambda: self.config_channel())
        self.config_btn.grid(row = 1, column = 2, padx = 5, sticky = 'nsew')
    
    def config_channel(self):
        #master is the mainchannel frame
        #master.master is daq_config_frame
        #self.ID is the channel ID
        #add channel information to listbox in master.master.config_listbox
        tc = voltage(self.ID)
        chan = channel('%s/ai%d' % (self.daq9211.name, self.ID), tc, int(self.ID))
        self.daq9211.add_channel(chan)
        item_str = "Channel: %s" % (chan.name)
        time_item_str = '[%s] %s' % (str(datetime.datetime.now().time().strftime("%H:%M:%S")),item_str)
        #first get all elements in the listbox
        all_elements = self.master.master.config_listbox.get(0,tk.END)
        for index, elem in enumerate(all_elements):
            if item_str in elem: #then the channel corresponding to index has been configured and needs to be overwritten
                self.master.master.config_listbox.delete(index)
        self.master.master.config_listbox.insert(tk.END, time_item_str)