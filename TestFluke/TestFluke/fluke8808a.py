import pyvisa

rm = pyvisa.ResourceManager()

class fluke8808a():
    def __init__(self, serial_address):
        self.ctrl = rm.open_resource(serial_address)




