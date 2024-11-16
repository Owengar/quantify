from source.imports import *








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


