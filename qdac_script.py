from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A




from source.imports import *
import source.instrument_identifier as instrument_identifier
import source.quantify_grapher as quantify_grapher
import source.safety_sweep as safety_sweep





qdac = QDac2("qdac", instrument_identifier.QDAC2_address)
#dmm = Keysight34461A("dmm", "USB0::0x2A8D::0x1401::MY60097947::INSTR")
#dmm.write("VOLT:DC:APER MIN")
safety_sweep.set_debug_printing(False)
safety_sweep.make_parameter_safe(qdac.ch01.dc_constant_V, 0.1, 0.01)



meas_ctrl = MeasurementControl("meas_ctrl")
plotmon = PlotMonitor_pyqt("SourcevoltagefromQDACandmeasurevoltageonDMM")
meas_ctrl.instr_plotmon(plotmon.name)



sweep = ManualParameter(name="sweep_number", label="Sweep Number", vals=validators.Ints())
voltage_parameter = qdac.ch01.dc_constant_V
voltage_parameter.label = "QDAC Output Voltage"
def get_voltage_dmm():
    return voltage_parameter() + sweep()*0.2




measured_voltage = Parameter("measured_voltage", label="DMM Measured Voltage", unit="V", get_cmd=get_voltage_dmm)
#measured_voltage = dmm.volt
measured_voltage.label = "DMM Measured Voltage"
voltage_parameter.inter_delay = 0.0



#The update interval controls how often in seconds the plot is visually updated to render new datapoints.
meas_ctrl.update_interval(0.1)
meas_ctrl.settables([voltage_parameter, sweep])
meas_ctrl.gettables(measured_voltage)
meas_ctrl.setpoints_grid([numpy.linspace(0, 9, 100), numpy.linspace(1, 50, 50, dtype=int)])



setup_config = quantify_grapher.plot_setup_configuration("after_sweep", "after_measurement", True)
quantify_grapher.plot(meas_ctrl, plotmon, "qgraph_mock", [voltage_parameter, sweep, measured_voltage], "C:\\Users\\WorkshopAFM2\\Box\\Quantum Device Lab\\Owen G\\Measurement Data", setup_config)