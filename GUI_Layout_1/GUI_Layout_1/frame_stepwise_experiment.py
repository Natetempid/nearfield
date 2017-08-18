
import Tkinter as tk
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk
import threading
import time
import numpy as np
from math import factorial

class stepwise_experiment_frame(tk.Frame):
    """description of class"""

    def __init__(self, master, controller, root, instruments):
        tk.Frame.__init__(self,master)
        self.grid_rowconfigure(0, weight = 1)
        #self.grid_rowconfigure(2, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.controller = controller
        #instruments
        self.instruments = dict(instruments) #self.instruments is a copy of the instruments dictionary and isn't the actually instant
        del self.instruments['usbswitch']
        self.instrument_list = ['Lakeshore Input A', 'Lakeshore Input B', 'DAQ Channel 0', 'DAQ Channel 1', 'DAQ Channel 2', 'DAQ Channel 3']
        self.purpose_list = ['Absorber Temperature', 'Emitter Temperature', 'Cold Finger Temperature', 'Heat Flux Sensor']
        self.ip_pairs = []

        self.get_data_thread = threading.Thread()
        self.get_data_event = threading.Event()
        self.get_data_event.set()

        self.is_equilibrated_thread = threading.Thread()
        self.is_equilibrated_event = threading.Event()
        self.is_equilibrated_event.set()
        
        #setup frame
        self.setup_label_frame = tk.LabelFrame(self, text = 'Experimental Setup Step:', font = ('tkDefaultFont', 20))
        self.setup_label_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.setup_label_frame.grid_rowconfigure(2, weight = 1)
        self.setup_label_frame.grid_columnconfigure(0, weight = 1)                

        self.temp_sensors_frame = tk.LabelFrame(self.setup_label_frame, text = 'Temperature Sensors', font = ('tkDefaultFont', 16))
        self.temp_sensors_frame.grid(row = 0, column = 0, sticky = 'nsew')
        #self.temp_sensors_frame.grid_rowconfigure(1, weight = 1)
        self.temp_sensors_frame.grid_rowconfigure(3, weight = 1)
        self.temp_sensors_frame.grid_columnconfigure(0,weight = 1)
        self.temp_sensors_frame.grid_columnconfigure(1,weight = 1)
        self.temp_sensors_frame.grid_columnconfigure(3,weight = 1)

        self.instruments_lbl = tk.Label(self.temp_sensors_frame, text = 'Instruments', font = ('tkDefaultFont', 14))
        self.instruments_lbl.grid(row = 0, column = 0, sticky = 'ew')
        self.purpose_lbl = tk.Label(self.temp_sensors_frame, text = 'Purpose', font = ('tkDefaultFont', 14))
        self.purpose_lbl.grid(row = 0, column = 1, sticky = 'ew')
        self.pairing_lbl = tk.Label(self.temp_sensors_frame, text = 'Instrument Pairs', font = ('tkDefaultFont', 14))
        self.pairing_lbl.grid(row = 0, column = 3, sticky = 'ew')

        self.instruments_listbox = tk.Listbox(self.temp_sensors_frame, exportselection = False)
        self.instruments_listbox.grid(row = 1, column = 0, sticky = 'nsew')
        for item in self.instrument_list:
            self.instruments_listbox.insert(tk.END, item)

        self.purpose_listbox = tk.Listbox(self.temp_sensors_frame, exportselection = False)
        self.purpose_listbox.grid(row = 1, column = 1, sticky = 'nsew')
        for item in self.purpose_list:
            self.purpose_listbox.insert(tk.END, item)
        
        #button frame within setup frame
        self.setup_btn_frame = tk.Frame(self.temp_sensors_frame)
        self.setup_btn_frame.grid(row = 1, column = 2, sticky = 'ns')
        self.setup_btn_frame.grid_rowconfigure(0, weight = 1)
        self.setup_btn_frame.grid_rowconfigure(1, weight = 1)
        self.create_pair_btn = ttk.Button(self.setup_btn_frame, text = 'Pair ->', command = lambda: self.pair())
        self.create_pair_btn.grid(row = 0, column = 0, sticky = 'nsew')
        self.undo_pair_btn = ttk.Button(self.setup_btn_frame, text = '<- Unpair', command = lambda: self.unpair())
        self.undo_pair_btn.grid(row = 1, column = 0, sticky = 'nsew')

        self.pairing_listbox = tk.Listbox(self.temp_sensors_frame, exportselection = False)
        self.pairing_listbox.grid(row = 1, column = 3, sticky = 'nsew')

        self.runsetup_btn = ttk.Button(self.setup_label_frame, text = 'Run Setup', command = lambda: self.run_setup())
        self.runsetup_btn.grid(row = 1, column = 0, sticky = 'ew')

        #frame for widgets necessary for determining equilibration
        self.equilibration_frame = tk.Frame(self.setup_label_frame, border = 2, relief = tk.GROOVE)
        self.equilibration_frame.grid(row = 2, column = 0, sticky = 'nsew')
        #self.equilibration_frame.grid_rowconfigure(0, weight = 1)
        self.equilibration_frame.grid_columnconfigure(0, weight = 1)
        self.equilibration_frame.grid_columnconfigure(1, weight = 1)
        #self.equilibration_frame.grid_columnconfigure(2, weight = 1)
        
        self.setpts_lbl_frame = tk.LabelFrame(self.equilibration_frame, text = 'Set Points', font = ('tkDefaultFont', 14))
        self.setpts_lbl_frame.grid(row = 0, column = 0, sticky = 'nsew')
        self.setpts_lbl_frame.grid_rowconfigure(1, weight = 1)
        self.setpts_lbl_frame.grid_rowconfigure(3, weight = 1)
        self.setpts_lbl_frame.grid_columnconfigure(0, weight = 1)
        #cold finger and emitter set points
        self.cf_setpt_lbl = tk.Label(self.setpts_lbl_frame, text = 'Cold Finger Set Point:')
        self.cf_setpt_lbl.grid(row = 0, column = 0, sticky = 'w')
        self.cf_setpt_str = tk.StringVar()
        self.cf_setpt_str.set('0')
        self.cf_setpt_entry = tk.Entry(self.setpts_lbl_frame, textvariable = self.cf_setpt_str, font = ('tkDefaultFont', 12))
        self.cf_setpt_entry.grid(row = 1, column = 0, sticky = 'nsew')

        self.emitter_setpt_lbl = tk.Label(self.setpts_lbl_frame, text = 'Emitter Set Point:')
        self.emitter_setpt_lbl.grid(row = 2, column = 0, sticky = 'w')
        self.emitter_setpt_str = tk.StringVar()
        self.emitter_setpt_str.set('0')
        self.emitter_setpt_entry = tk.Entry(self.setpts_lbl_frame, textvariable = self.emitter_setpt_str, font = ('tkDefaultFont', 12))
        self.emitter_setpt_entry.grid(row = 3, column = 0, sticky = 'nsew')

        #Realtime Frame
        self.realtime_lbl_frame = tk.LabelFrame(self.equilibration_frame, text = 'Real Time Temperature', font = ('tkDefaultFont', 14))
        self.realtime_lbl_frame.grid(row = 0, column = 1, sticky = 'nsew')
        for k in range(0,6):
            self.realtime_lbl_frame.grid_rowconfigure(k, weight = 1)
        self.realtime_lbl_frame.grid_columnconfigure(1, weight = 1)
        #self.realtime_lbl_frame.grid_columnconfigure(0, weight = 1)
        #Emitter
        self.realtime_emitter_lbl = tk.Label(self.realtime_lbl_frame, text = 'Emitter Temperature (K):', font = ('tkDefaultFont', 12))
        self.realtime_emitter_lbl.grid(row = 0, column = 0, sticky = 'w')
        self.realtime_emitter_str = tk.StringVar()
        self.realtime_emitter_str.set('0')
        self.realtime_emitter_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_emitter_str, font = ('tkDefaultFont', 12))
        self.realtime_emitter_entry.grid(row = 0, column = 1, sticky = 'ew')
        #Absorber
        self.realtime_absorber_lbl = tk.Label(self.realtime_lbl_frame, text = 'Absorber Temperature (K):', font = ('tkDefaultFont', 12))
        self.realtime_absorber_lbl.grid(row = 1, column = 0, sticky = 'w')
        self.realtime_absorber_str = tk.StringVar()
        self.realtime_absorber_str.set('0')
        self.realtime_absorber_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_absorber_str, font = ('tkDefaultFont', 12))
        self.realtime_absorber_entry.grid(row = 1, column = 1, sticky = 'ew')
        #Cold Finger
        self.realtime_cf_lbl = tk.Label(self.realtime_lbl_frame, text = 'Cold Finger Temperature (K):', font = ('tkDefaultFont', 12))
        self.realtime_cf_lbl.grid(row = 2, column = 0, sticky = 'w')
        self.realtime_cf_str = tk.StringVar()
        self.realtime_cf_str.set('0')
        self.realtime_cf_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_cf_str, font = ('tkDefaultFont', 12))
        self.realtime_cf_entry.grid(row = 2, column = 1, sticky = 'ew')
        #Heat Flux Sensor
        self.realtime_hfs_lbl = tk.Label(self.realtime_lbl_frame, text = 'Heat Flux Sensor (V):', font = ('tkDefaultFont', 12))
        self.realtime_hfs_lbl.grid(row = 3, column = 0, sticky = 'w')
        self.realtime_hfs_str = tk.StringVar()
        self.realtime_hfs_str.set('0')
        self.realtime_hfs_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_hfs_str, font = ('tkDefaultFont', 12))
        self.realtime_hfs_entry.grid(row = 3, column = 1, sticky = 'ew')
        #Fluke Primary
        self.realtime_fp_lbl = tk.Label(self.realtime_lbl_frame, text = 'Fluke Primary (V):', font = ('tkDefaultFont', 12))
        self.realtime_fp_lbl.grid(row = 4, column = 0, sticky = 'w')
        self.realtime_fp_str = tk.StringVar()
        self.realtime_fp_str.set('0')
        self.realtime_fp_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_fp_str, font = ('tkDefaultFont', 12))
        self.realtime_fp_entry.grid(row = 4, column = 1, sticky = 'ew')
        #Fluke Secondary
        self.realtime_fs_lbl = tk.Label(self.realtime_lbl_frame, text = 'Fluke Secondary (A):', font = ('tkDefaultFont', 12))
        self.realtime_fs_lbl.grid(row = 5, column = 0, sticky = 'w')
        self.realtime_fs_str = tk.StringVar()
        self.realtime_fs_str.set('0')
        self.realtime_fs_entry = tk.Entry(self.realtime_lbl_frame, textvariable = self.realtime_fs_str, font = ('tkDefaultFont', 12))
        self.realtime_fs_entry.grid(row = 5, column = 1, sticky = 'ew')


        self.equilibration_indicators_frame = tk.LabelFrame(self.equilibration_frame, text = 'Equilibrated?', font = ('tkDefaultFont', 14))
        self.equilibration_indicators_frame.grid(row = 0, column = 2, sticky = 'nsew')

        self.equilibration_time_frame = tk.Frame(self.equilibration_indicators_frame)
        self.equilibration_time_frame.grid(row = 0, column = 0, sticky = 'ew')
        self.equilibration_time_frame.grid_columnconfigure(0, weight = 1)
        self.equilibration_time_str = tk.StringVar()
        self.equilibration_time_str.set('15')
        self.equilibration_time_lbl = tk.Label(self.equilibration_time_frame, text = 'Equilibration Time (min):')
        self.equilibration_time_lbl.grid(row = 0, column = 0, sticky = 'ew')
        self.equilibration_time_entry = tk.Entry(self.equilibration_time_frame, textvariable = self.equilibration_time_str)
        self.equilibration_time_entry.grid(row = 0, column = 1, sticky = 'nsew')

        for k in range(0,7):
            self.equilibration_indicators_frame.grid_rowconfigure(k, weight = 1)
        self.equilibration_indicators_frame.grid_columnconfigure(0, weight = 1)
        #Emitter
        self.equilibrated_emitter = equilbrated_indicator(self.equilibration_indicators_frame, 'Emitter:')
        self.equilibrated_emitter.grid(row = 1, column = 0, sticky = 'ew')
        #Absorber
        self.equilibrated_absorber = equilbrated_indicator(self.equilibration_indicators_frame, 'Absorber:')
        self.equilibrated_absorber.grid(row = 2, column = 0, sticky = 'ew')
        #Cold Finger
        self.equilibrated_cf = equilbrated_indicator(self.equilibration_indicators_frame, 'Cold Finger:')
        self.equilibrated_cf.grid(row = 3, column = 0, sticky = 'ew')
        #Heat Flux Sensor
        self.equilibrated_hfs = equilbrated_indicator(self.equilibration_indicators_frame, 'Heat Flux Sensor:')
        self.equilibrated_hfs.grid(row = 4, column = 0, sticky = 'ew')
        #Fluke Primary
        self.equilibrated_fp = equilbrated_indicator(self.equilibration_indicators_frame, 'Fluke Primary:')
        self.equilibrated_fp.grid(row = 5, column = 0, sticky = 'ew')
        #Fluke Secondary
        self.equilibrated_fs = equilbrated_indicator(self.equilibration_indicators_frame, 'Fluke Secondary:')
        self.equilibrated_fs.grid(row = 6, column = 0, sticky = 'ew')

        #Stop Setup Button: Stops the is equilibrated thread        
        self.stopsetup_btn = ttk.Button(self.setup_label_frame, text = 'Stop Setup', command = lambda: self.stop_setup())
        self.stopsetup_btn.grid(row = 7, column = 0, sticky = 'ew')

        #next step frame
        self.step_label_frame = tk.LabelFrame(self, text = 'Next Steps:', font = ('tkDefaultFont', 20))
        self.step_label_frame.grid(row = 0, column = 1, sticky = 'snew')

    def pair(self):
        #get selected instrument
        instrument_str = self.instruments_listbox.get(self.instruments_listbox.curselection()[0])
        purpose_str = self.purpose_listbox.get(self.purpose_listbox.curselection()[0])
        try:
            ip_pair = instrument_purpose_pair(self.instruments, instrument_str, purpose_str)
            self.pairing_listbox.insert(tk.END, ip_pair.name)
            self.ip_pairs.append(ip_pair)
        except IndexError:
            tkMessageBox.showerror('Error', 'DAQ not yet configured')


    def pair_fluke(self):
        ip_pair = instrument_purpose_pair(self.instruments, 'Fluke Primary', 'Input Voltage')
        self.pairing_listbox.insert(tk.END, ip_pair.name)
        self.ip_pairs.append(ip_pair)
        ip_pair2 = instrument_purpose_pair(self.instruments, 'Fluke Secondary', 'Input Current')
        self.pairing_listbox.insert(tk.END, ip_pair2.name)
        self.ip_pairs.append(ip_pair2)

    def unpair(self):
        index = self.pairing_listbox.curselection()[0]
        del self.ip_pairs[index]
        self.pairing_listbox.delete(index)

    def run_setup(self):
        #add fluke primary and fluke secondary to ip_pairs list
        self.pair_fluke()
        #get the set points for colf finger and emitter
        for ip_pair in self.ip_pairs:
            ip_pair.get_set_point()
            if ip_pair.set_point != None:
                #Update the set point entries
                if ip_pair.purpose_str == 'Emitter Temperature':
                    self.emitter_setpt_str.set(str(ip_pair.set_point))
                elif ip_pair.purpose_str == 'Cold Finger Temperature':
                    self.cf_setpt_str.set(str(ip_pair.set_point))
        
        self.start_get_data_thread()
        self.start_isequilibrated_thread()

    def start_get_data_thread(self):
        self.get_data_thread = threading.Thread(target = self.__get_data_target)
        self.get_data_thread.start()

    def __get_data_target(self):
        #get data from queues and put data onto realtime entries
        self.get_data_event.clear()
        while (not self.get_data_event.is_set()):
            self.get_data_event.wait(1)
            for ip_pair in self.ip_pairs:
                ip_pair.get_queue_data()

                if (ip_pair.purpose_str == 'Emitter Temperature'):
                    self.realtime_emitter_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
                elif ip_pair.purpose_str == 'Absorber Temperature':
                    self.realtime_absorber_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
                elif ip_pair.purpose_str == 'Cold Finger Temperature':
                    self.realtime_cf_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
                elif ip_pair.purpose_str == 'Heat Flux Sensor':
                    self.realtime_hfs_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
                elif ip_pair.purpose_str == 'Input Voltage':
                    self.realtime_fp_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
                elif ip_pair.purpose_str == 'Input Current':
                    self.realtime_fs_str.set(str(np.mean(np.array(ip_pair.recent_data_list))) )
        
                

    def start_isequilibrated_thread(self):
        self.is_equilibrated_thread = threading.Thread(target = self.__is_equilibrated_target)
        self.is_equilibrated_thread.start()

    def __is_equilibrated_target(self):
        self.is_equilibrated_event.clear()
        while (not self.is_equilibrated_event.is_set()):
            self.is_equilibrated_event.wait(1)
            for ip_pair in self.ip_pairs:
                if 'Heat Flux Sensor' in ip_pair.purpose_str:
                    derivative_bound = 1e-7 #might need to change sensitivity here
                #elif 'Temperature' in ip_pair.purpose_str:
                #    derivative_bound = 0.01
                elif 'Absorber Temperature' in ip_pair.purpose_str: #DAQ temperature flucutuates more than the lakeshore PID controlled ones
                    derivative_bound = 0.02
                elif 'Emitter Temperature' or 'Cold Finger Temperature' in ip_pair.purpose_str:
                    derivative_bound = 0.005

                ip_pair.is_equilibrated(float(self.equilibration_time_str.get()), derivative_bound)

                if (ip_pair.purpose_str == 'Emitter Temperature'):
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_emitter.set_equilibrated_true()
                    else:
                        self.equilibrated_emitter.set_equilibrated_false()
                elif ip_pair.purpose_str == 'Absorber Temperature':
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_absorber.set_equilibrated_true()
                    else:
                        self.equilibrated_absorber.set_equilibrated_false()
                elif ip_pair.purpose_str == 'Cold Finger Temperature':
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_cf.set_equilibrated_true()
                    else:
                        self.equilibrated_cf.set_equilibrated_false()
                elif ip_pair.purpose_str == 'Heat Flux Sensor':
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_hfs.set_equilibrated_true()
                    else:
                        self.equilibrated_hfs.set_equilibrated_false()    
                elif ip_pair.purpose_str == 'Input Voltage':
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_fp.set_equilibrated_true()
                    else:
                        self.equilibrated_fp.set_equilibrated_false()    
                elif ip_pair.purpose_str == 'Input Current':
                    if ip_pair.bool_is_equilibrated:
                        self.equilibrated_fs.set_equilibrated_true()
                    else:
                        self.equilibrated_fs.set_equilibrated_false()    
                
    
    def stop_setup(self):
        self.stop_get_data_thread()
        self.stop_isequilibrated_thread()

    def stop_isequilibrated_thread(self):
        self.is_equilibrated_event.set()
        time.sleep(0.002)

    def stop_get_data_thread(self):
        self.get_data_event.set()
        time.sleep(0.002)

class instrument_purpose_pair():

    def __init__(self, instruments, instrument_str, purpose_str):
        #instruments is instruments dictionary
        self.instruments = instruments
        self.instrument_str = instrument_str
        self.purpose_str = purpose_str #['Absorber Temperature', 'Emitter Temperature', 'Cold Finger Temperature', 'Heat Flux Sensor']
        self.name = '%s,%s' % (self.instrument_str, self.purpose_str)
        self.instrument = None
        self.queue = None
        self.set_point = None

        self.time_list = []
        self.recent_data_list = []
        self.data_list = []

        self.bool_is_equilibrated = False

        self.determine_q()
    
    #need to determine the measurement queue from which to take data
    #['Lakeshore Input A', 'Lakeshore Input B', 'DAQ Channel 0', 'DAQ Channel 1', 'DAQ Channel 2', 'DAQ Channel 3']
    def determine_q(self):
        if self.instrument_str == 'Lakeshore Input A':
            self.instrument = self.instruments['lakeshore']
            self.queue = self.instrument.inputAq #this is the queue that lakeshore uses to plot data
        elif self.instrument_str == 'Lakeshore Input B':
            self.instrument = self.instruments['lakeshore']
            self.queue = self.instrument.inputBq
        elif 'DAQ' in self.instrument_str:
            self.instrument = self.instruments['daq9211']
            for k in range(0,4):
                if 'Channel %d' % k in self.instrument_str:
                    self.queue = data = self.instrument.channels[k].dataq
        elif self.instrument_str ==  'Fluke Primary':
            self.instrument = self.instruments['fluke8808a']
            self.queue = self.instrument.primaryq
        elif self.instrument_str ==  'Fluke Secondary':
            self.instrument = self.instruments['fluke8808a']
            self.queue = self.instrument.secondaryq
    
    def get_set_point(self):
        # only the temperature sensors connected to the lakeshore have a set point
        if self.instrument == self.instruments['lakeshore']:
            #need to iterate over the heater objects in the lakeshores class to see which one has the input corresponding to any of the temperature sensors
            if self.instrument_str == 'Lakeshore Input A':
                if self.instrument.heater1.input == 1: #input as 1 corresponds to A and 2 corresponds to B
                    self.set_point = self.instrument.heater1.setpoint
                elif self.instrument.heater2.input == 1: #input as 1 corresponds to A and 2 corresponds to B
                    self.set_point = self.instrument.heater2.setpoint
            elif self.instrument_str == 'Lakeshore Input B':
                if self.instrument.heater1.input == 2: #input as 1 corresponds to A and 2 corresponds to B
                    self.set_point = self.instrument.heater1.setpoint
                elif self.instrument.heater2.input == 2: #input as 1 corresponds to A and 2 corresponds to B
                    self.set_point = self.instrument.heater2.setpoint

    def get_queue_data(self):
        while not self.queue.empty():
            #fluke data are in np_arrays
            # primarydata = self.fluke8808a.primaryq.get()
            # timeprimary = primarydata[0]
            # tempprimary = primarydata[1]
            # unitprimary = primarydata[2]

            #lakeshore:
            # tempAdata = self.lakeshore.inputAq.get()
            # timeA = tempAdata[0]
            # tempA = tempAdata[1]

            #daq:
            # data = self.daq9211.channels[k].dataq.get()
            # time_val = data[0]
            # val = data[1]

            in_data = self.queue.get()
            in_time = in_data[0]
            in_val = in_data[1]

            self.recent_data_list = in_val
            self.time_list.append(in_time)
            self.data_list.append(in_val)

    def is_equilibrated(self, equilibration_time, derivative_bound):
        #equilibration time is in minutes. 
        #Over equilibration_time take means for patches of data ever mean_time # of seconds.  See if data are constant to within a deriative_bound
        if len(self.time_list) > 0:
            t_end = self.time_list[-1]
            t_start = t_end
            t_start -= datetime.timedelta(minutes = equilibration_time)
        
            #if at any point in the last equilibration_time number of minutes the derivative goes over the derivative bound, then the signal hasn't equilibrated
            relevant_data = [self.data_list[k] for k, time_elem in enumerate(self.time_list) if time_elem > t_start]
            relevant_smoothed_data = self.savitzky_golay(np.array(relevant_data), 51, 3) #np array #use the savitzky_golay method to smooth the noisy data to get good derivatives
            relevant_derivatives = np.diff(relevant_smoothed_data)

            #Any element in the self.relevant derivates list that is above the derivative_bound will be False.  All elements in the is_equilibrated_list must be True for the status to be "equilibrated"
            is_equilibrated_list = [True if np.abs(derivative_elem) <= derivative_bound else False for derivative_elem in relevant_derivatives]

            self.bool_is_equilibrated = all(is_equilibrated_list)
        


    def delete_data(self):
        self.data = []

    def savitzky_golay(self, y, window_size, order, deriv=0, rate=1): #this function smoothes out the noisey data
        try:
            window_size = np.abs(np.int(window_size))
            order = np.abs(np.int(order))
        except ValueError, msg:
            raise ValueError("window_size and order have to be of type int")
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        order_range = range(order+1)
        half_window = (window_size -1) // 2
        # precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve( m[::-1], y, mode='valid')

class equilbrated_indicator(tk.Frame):

    def __init__(self, master, name):
        tk.Frame.__init__(self, master)
        self.config(border = 2)
        self.grid_columnconfigure(0, weight = 1)
        self.name = name
        self.equilibrated = False
        self.lbl = tk.Label(self, text = self.name, font = ('tkDefaultFont', 12))
        self.lbl.grid(row = 0, column = 0, sticky = 'e')
        self.canvas = tk.Canvas(self, width = 25, height = 25)
        self.canvas.grid(row = 0, column = 1, sticky = 'w')
        self.indicator = self.canvas.create_oval(5,5,20,20, fill = 'red4')

    def set_equilibrated_true(self):
        self.equilbrated = True
        self.canvas.itemconfig(self.indicator, fill = "green2")

    def set_equilibrated_false(self):
        self.equilbrated = False
        self.canvas.itemconfig(self.indicator, fill = "red4")