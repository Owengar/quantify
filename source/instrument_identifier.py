from source.imports import *





def _check_runner_signal():
    start_time = time.time()
    time_with_no_signal = [0]
    def _no_signal():
        time_with_no_signal[0] = time.time() - start_time
        if time_with_no_signal[0] > 2:
            return True
        else:
            return False
    
    import source._process_exchange as _process_exchange
    if _process_exchange._wait_for_signal("ran_from_meas_runner", break_condition=_no_signal):
        return

    direct_run = input("You are running a measurement script directly, please run measurement scripts from the \"measurement_runner\" file. Running from the measurement script directly can cause the measurement shutdown procedure to not execute if an interruption occurs. Do you want to continue? y/n : ").lower()
    while True:
        if direct_run == "y":
            break
        elif direct_run == "n":
            sys.exit()
        else:
            direct_run = input("Please enter only \"y\" or \"n\" : ")

_check_runner_signal()




_idn_to_name = {
    "QDevil, QDAC-II, 242, 13-1.57" : "QDAC2"
}

QDAC2_address = ""


def _identify_resources():
    import pyvisa
    import pyvisa.constants
    _rm = pyvisa.ResourceManager()
    _resources = _rm.list_resources()
    for resource_address in _resources:
        with _rm.open_resource(resource_address) as opened_resource:
            opened_resource.set_visa_attribute(pyvisa.constants.ResourceAttribute.asrl_baud_rate, 921600)
            try:
                resource_idn = opened_resource.query("*IDN?")
            except:
                raise ConnectionError(f"Instrument of address  {resource_address}  caused error on \"*IDN?\" query.")
            try:
                instrument_name = _idn_to_name[resource_idn.removesuffix("\n")]
            except:
                raise NotImplementedError(f"Instrument of address  {resource_address}  had an IDN that was not in the _idn_to_name dictionary:  {_idn_to_name}  . This most likely means this instrument has not been documented yet and needs to be added to the dictionary.")
            
            globals().update({instrument_name+"_address" : resource_address})
    _rm.close()

_identify_resources()