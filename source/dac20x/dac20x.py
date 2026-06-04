import pyvisa
from pyvisa.constants import *
import qcodes
import time


class dac20x(qcodes.Instrument):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, **kwargs)
        self._address = address

        #for attribute set return codes
        self._debug = False

        #pyvisa ResourceManager
        self._rm = pyvisa.ResourceManager()
        #baud rate is 9600
        self._dac = self._rm.open_resource(self._address, baud_rate=0x2580)
        self._dac.read_termination = '\r'
        self._dac.write_termination = '\r'


        #attribute setting:
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_flow_control, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.timeout_value, 0x7D0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.termchar_enabled, VI_TRUE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.termchar, 0xD)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.send_end_enabled, VI_TRUE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_end_in, VI_ASRL_END_TERMCHAR)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_end_out, VI_ASRL_END_TERMCHAR)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.suppress_end_enabled, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.file_append_enabled, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_stop_bits, 10)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_parity, 0x0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.asrl_replace_char, 0x0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._dac.set_visa_attribute(ResourceAttribute.io_prot, 0x1)
        self._debug_print(status_code)
        time.sleep(0.1)


        #making parameters:
        self.ch1 : qcodes.Parameter
        self.ch2 : qcodes.Parameter
        self.ch3 : qcodes.Parameter
        self.ch4 : qcodes.Parameter
        qcodes.Parameter("ch1", self, "Channel 1 Voltage", "V", get_cmd=self._get_channel("3"), set_cmd=self._set_channel("3"))
        qcodes.Parameter("ch2", self, "Channel 2 Voltage", "V", get_cmd=self._get_channel("2"), set_cmd=self._set_channel("2"))
        qcodes.Parameter("ch3", self, "Channel 3 Voltage", "V", get_cmd=self._get_channel("7"), set_cmd=self._set_channel("7"))
        qcodes.Parameter("ch4", self, "Channel 4 Voltage", "V", get_cmd=self._get_channel("6"), set_cmd=self._set_channel("6"))

    def _debug_print(self, obj):
        if self._debug:
            print(obj)
    
    def __del__(self):
        self._dac.close()
        self._rm.close()

    def _set_channel(self, channel_num:str):
        def set_channel(voltage):
            self._dac.write(f"SET,{channel_num},{voltage}")
            time.sleep(0.1)
        return set_channel
    
    def _get_channel(self, channel_num:str):
        def get_channel():
            res = self._dac.query(f"GET_DAC,{channel_num}")
            time.sleep(0.1)
            return res
        return get_channel


if __name__ == "__main__":
    dac = dac20x("dac", "ASRL4::INSTR")

    dac.ch1.set(0)
    print(dac.ch4.get())


"""
if __name__ == "__main__":
    
    print("hi from dac20x.py")
    rm = pyvisa.ResourceManager()
    my_dac20x = rm.open_resource("ASRL4::INSTR", baud_rate=0x2580)
    my_dac20x.read_termination = '\r'
    my_dac20x.write_termination = '\r'

    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_flow_control, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.timeout_value, 0x7D0)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.termchar_enabled, VI_TRUE)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.termchar, 0xD)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.send_end_enabled, VI_TRUE)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_end_in, VI_ASRL_END_TERMCHAR)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_end_out, VI_ASRL_END_TERMCHAR)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.suppress_end_enabled, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.file_append_enabled, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_stop_bits, 10)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_parity, 0x0)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.asrl_replace_char, 0x0)
    print(status_code)
    time.sleep(0.1)
    status_code = my_dac20x.set_visa_attribute(ResourceAttribute.io_prot, 0x1)
    print(status_code)
    time.sleep(0.1)







    my_dac20x.write("SET,3,1")
    time.sleep(1)
    res = my_dac20x.query("GET_DAC,3")
    print(res)

    time.sleep(1)
    my_dac20x.close()
    rm.close()"""