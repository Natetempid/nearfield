import pyvisa

rm = pyvisa.ResourceManager()
#print rm.list_resources()
lkshr = rm.open_resource("ASRL3::INSTR")
lkshr.baud_rate = 57600
lkshr.parity = lkshr.parity.odd
lkshr.data_bits = 7
print lkshr.query("*IDN?")
lkshr.close()