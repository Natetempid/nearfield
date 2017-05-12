import pyvisa
import threading
import Queue as q
import datetime
import numpy as np
from enum import Enum

rm = pyvisa.ResourceManager()

class lakeshore335():
    def __init__(self, name):
        self.ctrl = rm.open_resource(name)
        self.ctrl.baud_rate = 57600
        self.ctrl.parity = pyvisa.constants.Parity.odd
        self.ctrl.data_bits = 7

        self.identity = self.lakestr2str(self.ctrl.query("*IDN?"))
        self.status = self.ctrl.query("*TST?")
        self.queueA = q.Queue()

        #data storage

        #temperature for inputs A and B
        self.listA = []#np.ndarray((1,), dtype = float)
        self.listB = []#np.ndarray((1,), dtype = float)

        #status of heaters 1 and 2
        self.heater1 = heater(self,1)
        self.heater2 = heater(self,2)

        #threading
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread_active = False
        #inputs
        self.inputA = input(self, 'A')
        self.inputB = input(self, 'B')

    #methods for threading and measuring    

    def configThread(self):
        self.stop_event.clear()

#########################
## Measure Temperature ##
#########################
  
    def get_tempA(self):
        temp = self.ctrl.query("KRDG? A")
        return self.lakestr2float(temp)

    def __measureA(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            #self.queueA.put({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.listA.append({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.stop_event.wait(timestep)
        self.thread_active = False

    def measureA(self, timestep):
        self.thread = threading.Thread(target = self.__measureA, args=(timestep,))
        self.thread.start()

    def get_tempB(self):
        temp = self.ctrl.query("KRDG? B")
        return self.lakestr2float(temp)

    def __measureB(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            #self.queueA.put({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.listB.append({'datetime': datetime.datetime.now(), 'data': self.get_tempB()})
            self.stop_event.wait(timestep)
        self.thread_active = False
    
    def measureB(self, timestep):
        self.thread = threading.Thread(target = self.__measureB, args=(timestep,))
        self.thread.start()


    def get_tempAandB(self):
        tempstrlist = self.lakestr2str(self.ctrl.query("KRDG? A KRDG? B")).split(';')
        tempfltlist = []
        for elem in tempstrlist:
            tempfltlist.append(float(elem))
        return tempfltlist

    def __measureAandB(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            tempfltlist = self.get_tempAandB()
            self.listA.append({'datetime': datetime.datetime.now(), 'data': tempfltlist[0]})
            self.listB.append({'datetime': datetime.datetime.now(), 'data': tempfltlist[1]})
            self.stop_event.wait(timestep)
        self.thread_active = False

    def measureAandB(self, timestep):
        self.thread = threading.Thread(target = self.__measureAandB, args=(timestep,))
        self.thread.start()

    def stopThread(self):
        self.stop_event.set()

###########################
## Measure Heater Output ##
###########################
        
    def __measureHeater1and2(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            #need htrset to get max current or max user current
            #need range to get heating decade
            #need htr? to get output percentage
            send_str = '%s;%s;%s;%s;%s;%s' % (self.heater1.prepare_htrset_q(), self.heater1.prepare_range_q(), self.heater1.prepare_htr_q(), 
                                     self.heater2.prepare_htrset_q(), self.heater2.prepare_range_q(), self.heater2.prepare_htr_q())
            return_str = self.ctrl.query(send_str)
            [htrset_1_str, range_1_str, htr_1_str, htrset_2_str, range_2_str, htr_2_str] = return_str.split(';')
            self.heater1.output.append({'datetime': datetime.datetime.now(), 'data': self.__returnstr2heatoutput(htrset_1_str, range_1_str, htr_1_str)})
            self.heater2.output.append({'datetime': datetime.datetime.now(), 'data': self.__returnstr2heatoutput(htrset_2_str, range_2_str, htr_2_str)})
            self.stop_event.wait(timestep)
        self.thread_active = False

    def measureHeater1and2(self, timestep):
        self.thread = threading.Thread(target = self.__measureHeater1and2, args = (timestep,))
        self.thread.start()

    def __returnstr2heatoutput(self, htrset_str, range_str, htr_str):
        htrset_str_split = htrset_str.split(',')
        max_current_ind = int(htrset_str_split[2])
        if max_current_ind == 0:
            #then max current is user specified
            max_current = float(htrset_str_split[3])
        elif max_current_ind == 1:
            max_current = 0.707
        elif max_current_ind == 2:
            max_current = 1
        elif max_current_ind == 3:
            max_current = 1.141
        elif max_current_ind == 4:
            max_current = 1.732
        else:
            return None
        range = int(range_str)
        htr = float(htr_str)
        output = max_current*htr/(10**(3-range))
        return output

###########################################
## Measure Heater Output and Temperature ##
###########################################

    def __measureAll(self, timestep):
        self.stop_event.clear()
        self.thread_active = True
        while (not self.stop_event.is_set()):
            self.stop_event.wait(timestep)
            send_str = 'KRDG? A;KRDG? B;%s;%s;%s;%s;%s;%s' % (self.heater1.prepare_htrset_q(), self.heater1.prepare_range_q(), self.heater1.prepare_htr_q(), 
                                        self.heater2.prepare_htrset_q(), self.heater2.prepare_range_q(), self.heater2.prepare_htr_q())
            return_str = self.ctrl.query(send_str)
            print return_str
            [tempA, tempB, htrset_1_str, range_1_str, htr_1_str, htrset_2_str, range_2_str, htr_2_str] = return_str.split(';')
            self.listA.append({'datetime': datetime.datetime.now(), 'data': float(tempA)})
            self.listB.append({'datetime': datetime.datetime.now(), 'data': float(tempB)})
            self.heater1.outputAmps.append({'datetime': datetime.datetime.now(), 'data': self.__returnstr2heatoutput(htrset_1_str, range_1_str, htr_1_str)})
            self.heater2.outputAmps.append({'datetime': datetime.datetime.now(), 'data': self.__returnstr2heatoutput(htrset_2_str, range_2_str, htr_2_str)})
            self.heater1.outputPercent.append({'datetime': datetime.datetime.now(), 'data': float(htr_1_str)})
            self.heater2.outputPercent.append({'datetime': datetime.datetime.now(), 'data': float(htr_2_str)})
        self.thread_active = False
    
    def measureAll(self, timestep):
        self.thread = threading.Thread(target = self.__measureAll, args = (timestep,))
        self.thread.start()   

    #methods for writing serial commmands to lakeshore
    def close(self):
        self.ctrl.close()
  
    def lakestr2str(self, str):
        return str.strip("\r\n")

    def lakestr2float(self, str):
        return float(str.strip("\r\n"))


class heater():
    def __init__(self, parent, IDnumber):
        #parent is lakeshore instance
        self.parent = parent
        self.ID = IDnumber
        self.mode = None
        self.input = None
        self.powerupenable = None
        #Polarity
        heater.outputtype = None
        heater.polarity = None
        #Heater Setup
        heater.type = None
        heater.resistance = None
        heater.maxcurrent = None
        heater.maxusercurrent = None
        heater.iorw = None
        #PID
        heater.p = None
        heater.i = None
        heater.d = None
        #Setpoint
        heater.setpoint = None
        heater.setpointramp = None
        heater.setpointrampenable = None
        #Range
        heater.range = None
        heater.outputAmps = []
        heater.outputPercent = []

    #Configure Heater
    def prepare_outmode(self):
        return 'OUTMODE %d,%d,%d,%d' % (self.ID, self.mode, self.input, self.powerupenable)
    def prepare_polarity(self):
        return 'POLARITY 2,%d' % self.polarity
    def prepare_htrset(self):
        return 'HTRSET %d,%d,%d,%d,%.3f,%d' % (self.ID, self.type, self.resistance, self.maxcurrent, self.maxusercurrent, self.iorw)
    def prepare_pid(self):
        return 'PID %d,%.1f,%.1f,%.1f' % (self.ID, self.p, self.i, self.d)
    def prepare_ramp(self):
        return 'RAMP %d,%d,%.1f' % (self.ID, self.setpointrampenable, self.setpointramp)
    def prepare_setp(self):
        return 'SETP %d,%.4f' % (self.ID, self.setpoint)
    def prepare_range(self):
        return 'RANGE %d,%d' % (self.ID, self.range)

    def set_range(self):
        self.parent.ctrl.write(self.prepare_range)

    def query_range(self):
        return int(self.parent.ctrl.query(self.prepare_range_q)) #get what the range is without changing the instance property

    def config(self):
        if self.ID is 2 and self.outputtype is 2: #include polarity
            command_str = '%s;%s;%s;%s;%s;%s' % (self.prepare_outmode(), self.prepare_polarity(), self.prepare_htrset(), self.prepare_pid(), self.prepare_ramp(), self.prepare_setp())
        else:
            command_str = '%s;%s;%s;%s;%s' % (self.prepare_outmode(), self.prepare_htrset(), self.prepare_pid(), self.prepare_ramp(), self.prepare_setp())
        #print command_str
        self.parent.thread_active = True
        self.parent.ctrl.write(command_str)
        self.parent.thread_active = False

    #Query Heater
    def prepare_outmode_q(self):
        return 'OUTMODE? %d' % (self.ID)
    def prepare_polarity_q(self):
        return 'POLARITY? %d' % (self.ID)
    def prepare_htrset_q(self):
        return 'HTRSET? %d'% (self.ID)
    def prepare_pid_q(self):
        return 'PID? %d' % (self.ID)
    def prepare_ramp_q(self):
        return 'RAMP? %d' % (self.ID)
    def prepare_setp_q(self):
        return 'SETP? %d' % (self.ID)
    def prepare_range_q(self): #need to add range property
        return 'RANGE? %d' % (self.ID)
    def prepare_htr_q(self):
        return 'HTR? %d' % (self.ID)

    def query(self):
        command_str = '%s;%s;%s;%s;%s;%s' % (self.prepare_outmode_q(), self.prepare_polarity_q(), self.prepare_htrset_q(), self.prepare_pid_q(), self.prepare_ramp_q(), self.prepare_setp_q())
        self.parent.thread_active = True
        return_str = self.parent.ctrl.query(command_str)
        self.parent.thread_active = False
        [outmode_str, polarity_str, htrset_str, pid_str, ramp_str, setp_str] = return_str.split(';')
        [mode_str, input_str, powerupenable_str] = outmode_str.split(',')
        self.mode = int(mode_str)
        self.input = int(input_str)
        self.powerupenable = int(powerupenable_str)
        self.polarity = int(polarity_str)
        [type_str, resistance_str, maxcurrent_str, maxusercurrent_str, iorw_str] = htrset_str.split(',')
        self.type = int(type_str)
        self.resistance = int(resistance_str)
        self.maxcurrent = int(maxcurrent_str)
        self.maxusercurrent = float(maxusercurrent_str)
        self.iorw = int(iorw_str)
        [p_str, i_str, d_str] = pid_str.split(',')
        self.p = float(p_str)
        self.i = float(i_str)
        self.d = float(d_str)
        [setpointrampenable_str, setpointramp_str] = ramp_str.split(',')
        self.setpointrampenable = int(setpointrampenable_str)
        self.setpointramp = float(setpointramp_str)
        self.setpoint = float(setp_str)
    
class input():
    def __init__(self, parent, IDletter):
        self.parent = parent
        self.ID = IDletter
        #INTYPE
        self.type = None
        self.type_str = None #This will be the same string as viewed in the Gui
        self.autorange = None
        self.range = None
        self.compensation = None
        self.units = None
        #autorange to units properties are from INTYPE? command, and are predetermined for the each sensor type
        #DIOCUR
        self.diodecurrent = None #index of 0 means 10uA and index of 1 means 1mA
        #INCRV
        self.curve = None
        self.curve_str = None #This will be the same string as viewed in the Gui
        #TLIMIT
        self.tlimit = None
    ##########
    # Config #
    ##########
    def prepare_intype(self):
        return 'INTYPE %s,%d,%d,%d,%d,%d' % (self.ID,self.type,self.autorange,self.range,self.compensation,self.units)
    def prepare_diocur(self):
        return 'DIOCUR %s,%d' % (self.ID, self.diodecurrent)
    def prepare_incrv(self):
        return 'INCRV %s,%d' % (self.ID, self.curve)
    def prepare_tlimit(self):
        return 'TLIMIT %s,%.3f' % (self.ID, self.tlimit)
    def config(self):
        #only send diode current for a diode type temperature sensor
        if self.type == 1: #then the type is a diode
            command_str = '%s;%s;%s;%s' %(self.prepare_intype(), self.prepare_diocur(), self.prepare_incrv(), self.prepare_tlimit())
        else:
            command_str = '%s;%s;%s' %(self.prepare_intype(), self.prepare_incrv(), self.prepare_tlimit())
        self.parent.ctrl.write(command_str)
    
    #########
    # Query #
    #########

    def prepare_intype_q(self):
        return 'INTYPE? %s' % self.ID
    def prepare_diocur_q(self):
        return 'DIOCUR? %s' % self.ID
    def prepare_incrv_q(self):
        return 'INCRV? %s' % self.ID
    def prepare_tlimit_q(self):
        return 'TLIMIT? %s' % self.ID
    def query(self):
        #only send diode current for a diode type temperature sensor
        command_str = '%s;%s;%s;%s' %(self.prepare_intype_q(), self.prepare_diocur_q(), self.prepare_incrv_q(), self.prepare_tlimit_q())
        return_str = self.parent.ctrl.query(command_str)
        [intype_str, diocur_str, incrv_str, tlimit_str] = return_str.split(';')
        [type_str, autorange_str, range_str, compensation_str, units_str] = intype_str.split(',')
        #INTYPE
        self.type = int(type_str)
        self.autorange = int(autorange_str)
        self.range = int(range_str)
        self.compensation = int(compensation_str)
        self.units = int(units_str)
        self.nums2typestr() #sets self.type_str given the values of autorange, range, and compensation
        #DIOCUR
        self.diodecurrent = int(diocur_str)
        #INCRV
        self.curve = int(incrv_str)
        #TLIMIT
        self.tlimit = float(tlimit_str)




    ################################################
    # Go from String to numbers for serial command #
    ################################################

    def typestr2nums(self):
        typelist =  ["Disabled","Diode 2.5 V (Silicon)", "Diode 10 V (GaAlAs)", "PTC RTD Autorange", "PTC RTD 10 Ohm", "PTC RTD 30 Ohm", "PTC RTD 100 Ohm",
                          "PTC RTD 300 Ohm", "PTC RTD 1 kOhm", "PTC RTD 3 kOhm", "PTC RTD 10 kOhm", "NTC RTD Autorange", "NTC RTD 10 Ohm", "NTC RTD 30 Ohm", 
                          "NTC RTD 100 Ohm", "NTC RTD 300 Ohm", "NTC RTD 1 kOhm", "NTC RTD 3 kOhm", "NTC RTD 10 kOhm", "NTC RTD 30 kOhm", "NTC RTD 100 kOhm", "Thermocouple"]
        match_index = typelist.index(self.type_str)
        #long if statement
        if match_index == 0:
            self.assign_intypeparams(0,0,0)
        elif match_index == 1:
            self.assign_intypeparams(1,0,0)
        elif match_index == 2:
            self.assign_intypeparams(1,0,1)
        elif match_index == 3:
            self.assign_intypeparams(2,1,0)
        elif match_index == 4:
            self.assign_intypeparams(2,0,0)
        elif match_index == 5:
            self.assign_intypeparams(2,0,1)
        elif match_index == 6:
            self.assign_intypeparams(2,0,2)
        elif match_index == 7:
            self.assign_intypeparams(2,0,3)
        elif match_index == 8:
            self.assign_intypeparams(2,0,4)
        elif match_index == 9:
            self.assign_intypeparams(2,0,5)
        elif match_index == 10:
            self.assign_intypeparams(2,0,6)
        elif match_index == 11:
            self.assign_intypeparams(3,1,0)
        elif match_index == 12:
            self.assign_intypeparams(3,0,0)
        elif match_index == 13:
            self.assign_intypeparams(3,0,1)
        elif match_index == 14:
            self.assign_intypeparams(3,0,2)
        elif match_index == 15:
            self.assign_intypeparams(3,0,3)
        elif match_index == 16:
            self.assign_intypeparams(3,0,4)
        elif match_index == 17:
            self.assign_intypeparams(3,0,5)
        elif match_index == 18:
            self.assign_intypeparams(3,0,6)
        elif match_index == 19:
            self.assign_intypeparams(3,0,7)
        elif match_index == 20:
            self.assign_intypeparams(3,0,8)
        elif match_index == 21:
            self.assign_intypeparams(4,0,0)

    def assign_intypeparams(self,type,autorange,range):
        self.type = type
        self.autorange = autorange
        self.range = range
     
    #################################################
    # Go from numbers from serial command to string #
    #################################################

    def nums2typestr(self):
        typelist =  ["Disabled","Diode 2.5 V (Silicon)", "Diode 10 V (GaAlAs)", "PTC RTD Autorange", "PTC RTD 10 Ohm", "PTC RTD 30 Ohm", "PTC RTD 100 Ohm",
                          "PTC RTD 300 Ohm", "PTC RTD 1 kOhm", "PTC RTD 3 kOhm", "PTC RTD 10 kOhm", "NTC RTD Autorange", "NTC RTD 10 Ohm", "NTC RTD 30 Ohm", 
                          "NTC RTD 100 Ohm", "NTC RTD 300 Ohm", "NTC RTD 1 kOhm", "NTC RTD 3 kOhm", "NTC RTD 10 kOhm", "NTC RTD 30 kOhm", "NTC RTD 100 kOhm", "Thermocouple"]
    
        if self.type == 0: #Disabled
            self.type_str = typelist[0]
        elif self.type == 1: #Diode
            if self.range == 0: #Si
                self.type_str = typelist[1]
            elif self.range == 1: #GaAlAs
                self.type_str = typelist[2]
        elif self.type == 2: #PTC
            if self.autorange == 1: #Autorange
                self.type_str = typelist[3]
            elif self.autorange == 0: 
                if self.range == 0: #10 Ohm
                    self.type_str = typelist[4]
                if self.range == 1: #30 Ohm
                    self.type_str = typelist[5]
                if self.range == 2: #100 Ohm
                    self.type_str = typelist[6]
                if self.range == 3: #300 Ohm
                    self.type_str = typelist[7]
                if self.range == 4: #1 kOhm
                    self.type_str = typelist[8]
                if self.range == 5: #3 kOhm
                    self.type_str = typelist[9]
                if self.range == 6: #10 kOhm
                    self.type_str = typelist[10]
        elif self.type == 3: #NTC
            if self.autorange == 1: #Autorange
                self.typestr = typelist[11]
            elif self.autorange == 0:
                if self.range == 0: #10 Ohm
                    self.type_str = typelist[12]
                if self.range == 1: #30 Ohm
                    self.type_str = typelist[13]
                if self.range == 2: #100 Ohm
                    self.type_str = typelist[14]
                if self.range == 3: #300 Ohm
                    self.type_str = typelist[15]
                if self.range == 4: #1 kOhm
                    self.type_str = typelist[16]
                if self.range == 5: #3 kOhm
                    self.type_str = typelist[17]
                if self.range == 6: #10 kOhm
                    self.type_str = typelist[18]
                if self.range == 7: #30 kOhm
                    self.type_str = typelist[19]
                if self.range == 8: #100 kOhm
                    self.type_str = typelist[20]
        elif self.type == 4: #Thermocouple
            self.type_str = typelist[21]