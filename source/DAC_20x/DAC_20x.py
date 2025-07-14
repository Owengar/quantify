
#THIS DAC USES CARRIAGE RETURN: "\r" INSTEAD OF "\n"
#Edited for DACington the 1nd

import sys
sys.dont_write_bytecode = True

import pyvisa, sys
import qcodes
from qcodes.instrument.parameter import Parameter


class DAC_20x(qcodes.Instrument):
    def __init__(self, name, address, channel_count = 8, **kwargs):
        super().__init__(name, **kwargs)

        self.address = address
        self.channel_count = channel_count
        self.rm = pyvisa.ResourceManager()
        self.dac = self.rm.open_resource(address)
        self.dac.clear()

        ####for syntax highlighting
        self.ch0_voltage : Parameter
        self.ch1_voltage : Parameter
        self.ch2_voltage : Parameter
        self.ch3_voltage : Parameter
        self.ch4_voltage : Parameter
        self.ch5_voltage : Parameter
        self.ch6_voltage : Parameter
        self.ch7_voltage : Parameter
        ####

        for i in range(channel_count):
            Parameter(f"ch{i}_voltage", self, label=f"CH{i} Voltage", unit="V", get_cmd=self._get_channel_get_voltage(i), set_cmd=self._get_channel_set_voltage(i))

    def _get_channel_get_voltage(self, channel : int):
        def get_voltage():
            return float(self.dac.query(f"GET_DAC,{channel}\r"))
        return get_voltage
    def _get_channel_set_voltage(self, channel):
        def set_voltage(value):
            self.dac.query(f"SET,{channel},{value}\r")
            self.dac.clear()
        return set_voltage
    def __del__(self):
        try:
            self.dac.close()
            self.rm.close()
        except:
            pass
