import pyvisa

rm = pyvisa.ResourceManager()

#try:
#    lkshr = rm.open_resource("ASRL3::INSTR")
#except pyvisa.VisaIOError:
#    pass
#    exit()


class lakeshore335():
    def __init__(self, name):
        self.ctrl = rm.open_resource(name)
        self.ctrl.baud_rate = 57600
        self.ctrl.parity = pyvisa.constants.Parity.odd
        self.ctrl.data_bits = 7

        self.identity = self.lakestr2str(self.ctrl.query("*IDN?"))
        self.status = self.ctrl.query("*TST?")
    
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


