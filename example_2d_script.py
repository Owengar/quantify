from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A




from source.imports import *
import source.quantify_grapher as quantify_grapher
import source.safety_sweep as safety_sweep






meas_ctrl = MeasurementControl("meas_ctrl")
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
    return sweep_number() * dummy_voltage_source()

measured_voltage = Parameter("measured_voltage", dummy_instrument, "Dummy Measured Voltage", unit="V", get_cmd=measured_voltage_get, bind_to_instrument=True)
second_gettable = Parameter("second_gettable", dummy_instrument, "Extra Gettable", unit="V", get_cmd=measured_voltage_get, bind_to_instrument=True)










dummy_voltage_source.inter_delay = 0.1

meas_ctrl.settables([dummy_voltage_source, sweep_number])
meas_ctrl.gettables([measured_voltage, second_gettable])
meas_ctrl.setpoints_grid([numpy.linspace(-2, 2, 100), numpy.linspace(1, 100, 100)])

measurement = quantify_grapher.measurement_configuration(quantify_grapher.plotly("total_live"))
measurement.plot("TwoDExample", meas_ctrl, "C:\\Users\\samga\\Documents\\Visual_Studio_Code\\Tank_Game_Project\\quantify", comments="2d measurement example")
