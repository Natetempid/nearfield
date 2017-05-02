import pyvisa
import threading
import Queue as q
import datetime

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
        self.listA = []
        self.thread = threading.Thread()
        self.stop_event = threading.Event()
        
    #methods for threading and measuring    
    def __measureA(self, timestep):
        while (not self.stop_event.is_set()):
            #self.queueA.put({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.listA.append({'datetime': datetime.datetime.now(), 'data': self.get_tempA()})
            self.stop_event.wait(timestep)
    
    def configThread(self):
        self.stop_event.clear()

    def measureA(self, timestep):
        self.thread = threading.Thread(target = self.__measureA, args=(timestep,))
        self.thread.start()

    def stopThread(self):
        self.stop_event.set()

    #methods for writing serial commmands to lakeshore
    def close(self):
        self.ctrl.close()
    
    def get_tempA(self):
        temp = self.ctrl.query("KRDG? A")
        return self.lakestr2float(temp)
    
    def get_tempB(self):
        temp = self.ctrl.query("KRDG? B")
        return self.lakestr2float(temp)

    def lakestr2str(self, str):
        return str.strip("\r\n")

    def lakestr2float(self, str):
        return float(str.strip("\r\n"))


