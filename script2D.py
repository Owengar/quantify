from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A
import qcodes
from qcodes import Parameter, Instrument
import quantify_core
import quantify_core.data
import quantify_core.data.handling
from quantify_core.measurement import Gettable, MeasurementControl
import numpy, sys, os, time

from source import quantify_measurement






dummy_instrument = Instrument("dummy_instrument")
_dummy_voltage = 0.0
def dummy_voltage_get():
    return _dummy_voltage
def dummy_voltage_set(set_to):
    global _dummy_voltage
    _dummy_voltage = set_to
dummy_voltage_source = Parameter("dummy_voltage", dummy_instrument, "Dummy Voltage", "V", get_cmd=dummy_voltage_get, set_cmd=dummy_voltage_set, bind_to_instrument=True)




_sweep_number = 0
def sweep_number_get():
    return _sweep_number
def sweep_number_set(set_to):
    global _sweep_number
    _sweep_number = set_to
sweep_number = Parameter("sweep_number", dummy_instrument, "Sweep Number", get_cmd=sweep_number_get, set_cmd=sweep_number_set, bind_to_instrument=True)





def measured_voltage_get():
    return sweep_number() + numpy.sin(dummy_voltage_source())
def measured_voltage_get_second(): #this is to differentiate it from the first gettable
    return sweep_number() * numpy.sin(dummy_voltage_source()) * 5
measured_voltage = Parameter("measured_voltage", dummy_instrument, "Dummy Measured Voltage", unit="V", get_cmd=measured_voltage_get, bind_to_instrument=True)
second_gettable = Parameter("second_gettable", dummy_instrument, "Extra Gettable", unit="V", get_cmd=measured_voltage_get_second, bind_to_instrument=True)



sweep_number.set(1)
dummy_voltage_source.inter_delay = 0.0

quantify_measurement.set_settables([dummy_voltage_source, sweep_number])
quantify_measurement.set_gettables([measured_voltage, second_gettable])

quantify_measurement.make_setpoint_list([(-50, 50, 100)], dummy_voltage_source)
quantify_measurement.make_setpoint_list([(0, 50, 51)], sweep_number)
quantify_measurement.set_measurement_name("example")
quantify_measurement.run()
print("all out")
