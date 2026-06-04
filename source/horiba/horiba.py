import qcodes
import pyvisa
import time
from pyvisa.constants import *


def _no_getters():
    print("This parameter does not have a getter.")
    return 0


class horiba(qcodes.Instrument):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, **kwargs)
        self._address = address

        #for attribute set return codes
        self._debug = False

        #pyvisa ResourceManager
        self._rm = pyvisa.ResourceManager()
        #baud rate is 9600
        self._horiba = self._rm.open_resource(self._address, baud_rate=0x2580)
        self._horiba.read_termination = '\r'
        self._horiba.write_termination = '\r'


        #attribute setting:
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_flow_control, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.timeout_value, 0x7D0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.termchar_enabled, VI_TRUE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.termchar, 0xD)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.send_end_enabled, VI_TRUE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_end_in, VI_ASRL_END_TERMCHAR)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_end_out, VI_ASRL_END_TERMCHAR)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.suppress_end_enabled, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.file_append_enabled, VI_FALSE)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_stop_bits, 10)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_parity, 0x0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.asrl_replace_char, 0x0)
        self._debug_print(status_code)
        time.sleep(0.1)
        status_code = self._horiba.set_visa_attribute(ResourceAttribute.io_prot, 0x1)
        self._debug_print(status_code)
        time.sleep(0.1)


        #making parameters:
        self.intensity : qcodes.Parameter
        self.width : qcodes.Parameter
        self.middle_wavelength : qcodes.Parameter
        qcodes.Parameter("intensity", self, "Intensity", "Cd", get_cmd=_no_getters, set_cmd=self._set_intensity())
        qcodes.Parameter("width", self, "Spectrum Width", "nm", get_cmd=_no_getters, set_cmd=self._set_width())
        qcodes.Parameter("middle_wavelength", self, "Middle Wave Length", "Steps", get_cmd=_no_getters, set_cmd=self._set_middle_wavelength())


    def _debug_print(self, obj):
        if self._debug:
            print(obj)

    def __del__(self):
        self._horiba.close()
        self._rm.close()
    
    def _set_intensity(self):
        def set(intensity):
            self._horiba.write(f"Intensity,{intensity}")
        return set
    def _set_width(self):
        def set(width):
            self._horiba.write(f"Width,{width}")
        return set
    def _set_middle_wavelength(self):
        def set(wavelength):
            self._horiba.write(f"Wavelength,{wavelength}")
        return set
    
    