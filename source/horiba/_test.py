import qcodes
import pyvisa
import time
from pyvisa.constants import *







if __name__ == "__main__":
    print("hi from horiba.py")
    rm = pyvisa.ResourceManager()
    horiba = rm.open_resource("ASRL5::INSTR", baud_rate=0x2580)
    horiba.read_termination = '\r'
    horiba.write_termination = '\r'


    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_flow_control, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.timeout_value, 0x7D0)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.termchar_enabled, VI_TRUE)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.termchar, 0xD)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.send_end_enabled, VI_TRUE)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_data_bits, 8)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_end_in, VI_ASRL_END_TERMCHAR)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_end_out, VI_ASRL_END_TERMCHAR)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.suppress_end_enabled, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.file_append_enabled, VI_FALSE)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_stop_bits, 10)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_parity, 0x0)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.asrl_replace_char, 0x0)
    print(status_code)
    time.sleep(0.1)
    status_code = horiba.set_visa_attribute(ResourceAttribute.io_prot, 0x1)
    print(status_code)
    time.sleep(0.1)



    while True:
        print(horiba.write(f"Intensity,{float(input("Intensity,"))}"))


    horiba.close()
    rm.close()