import pyvisa

#rm = pyvisa.ResourceManager()
##print rm.list_resources()
#lkshr = rm.open_resource("ASRL3::INSTR")
#lkshr.baud_rate = 57600
#lkshr.parity = lkshr.parity.odd
#lkshr.data_bits = 7
#print lkshr.query("*IDN?")
#lkshr.close()

from instruments import lakeshore335

lkshr = lakeshore335('ASRL3::INSTR')

print lkshr.identity
print lkshr.get_tempA()
print lkshr.get_tempB()
lkshr.close()