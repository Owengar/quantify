from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A




from source.imports import *
import source.instrument_identifier as instrument_identifier
import source.quantify_grapher as quantify_grapher
import source.safety_sweep as safety_sweep






meas_ctrl = MeasurementControl("meas_ctrl")
plotmon = PlotMonitor_pyqt("ExampleMeasurement")
meas_ctrl.instr_plotmon(plotmon.name)









dummy_instrument = Instrument("dummy")
dummy_voltage = 0.0
def dummy_voltage_get():
    return dummy_voltage
def dummy_voltage_set(set_to):
    global dummy_voltage
    dummy_voltage = set_to
dummy_parameter = Parameter("dummy_voltage", dummy_instrument, "Dummy Voltage", "V", get_cmd=dummy_voltage_get, set_cmd=dummy_voltage_set, bind_to_instrument=True)






measured_voltage = Parameter("measured_voltage", dummy_instrument, label="Dummy Measured Voltage", unit="V", get_cmd=dummy_voltage_get)


#The update interval controls how often in seconds the plot is visually updated to render new datapoints.
meas_ctrl.update_interval(0.1)
meas_ctrl.settables(dummy_parameter)
meas_ctrl.gettables(measured_voltage)
meas_ctrl.setpoints_grid([numpy.linspace(0, 9, 100)])



setup_config = quantify_grapher.plot_setup_configuration("after_step", "after_measurement", True)
quantify_grapher.plot(meas_ctrl, plotmon, "qgraph_mock", [dummy_parameter, measured_voltage], "C:\\Users\\WorkshopAFM2\\Box\\Quantum Device Lab\\Owen G\\Measurement Data", setup_config)
