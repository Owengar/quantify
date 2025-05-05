#Below, we are importing the instruments that we'll be working with.
from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A



#Below. we import all necessary utilities of Quantify and Qcodes.
from source.imports import *
#Below, we the main module used to setup and graph measurements.
import source.quantify_grapher as quantify_grapher
#Below, we optionally import the safety module, which contains functions to limit parameter step sizes, step times, and define parameter limits such that when they are exceeded, the measurement stops.
import source.safety as safety





meas_ctrl = MeasurementControl("meas_ctrl")
example_instrument = Instrument("example_instrument")







_example_voltage = 0.0
def example_voltage_get():
    return _example_voltage
def example_voltage_set(set_to):
    global _example_voltage
    _example_voltage = set_to
example_voltage_source = Parameter("example_voltage", example_instrument, "Source Voltage", unit="V", get_cmd=example_voltage_get, set_cmd=example_voltage_set, bind_to_instrument=True)




def measured_voltage_get():
    return example_voltage_source()

measured_voltage = Parameter("measured_voltage", example_instrument, "Measured Voltage", unit="V", get_cmd=measured_voltage_get, bind_to_instrument=True)








example_voltage_source.inter_delay = 0.1

meas_ctrl.settables(example_voltage_source)
meas_ctrl.gettables(measured_voltage)
#meas_ctrl.setpoints_grid([numpy.linspace(0, 9, 10)])

measurement = quantify_grapher.measurement_configuration(quantify_grapher.plotly_graphing())
measurement.plot("OneDExample", meas_ctrl, comments="1d measurement example")