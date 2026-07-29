from qcodes.parameters import Parameter
from qcodes.instrument import Instrument
from gatekeeper import GateKeeper
import time


class gatekeeper(Instrument):
	def __init__(self, name : str, address : str, label : str = "GateKeeper", initialize : bool = False):
		"""IMPORTANT: initialize = True loads calibration data and sets all DAC outputs to 0V. Documentation instructs to use after the Gatekeeper is powercycled."""
		super().__init__(name, label=label)
		self.address = address
		self.gk = GateKeeper(address)
		if initialize:
			print(self.gk.initialize())
		
		


		def get_get_dac(channel : int):
			def get():
				return self.gk.get_dac(channel)
			return get
		def get_set_dac(channel : int):
			def set(voltage : float):
				print(self.gk.set_voltage(channel, voltage))
			return set
		self.ch0 = Parameter("gk_ch0", label="Gatekeeper Channel 0", unit="V", get_cmd=get_get_dac(0), set_cmd=get_set_dac(0))
		self.ch1 = Parameter("gk_ch1", label="Gatekeeper Channel 1", unit="V", get_cmd=get_get_dac(1), set_cmd=get_set_dac(1))
		self.ch2 = Parameter("gk_ch2", label="Gatekeeper Channel 2", unit="V", get_cmd=get_get_dac(2), set_cmd=get_set_dac(2))
		self.ch3 = Parameter("gk_ch3", label="Gatekeeper Channel 3", unit="V", get_cmd=get_get_dac(3), set_cmd=get_set_dac(3))
		self.ch4 = Parameter("gk_ch4", label="Gatekeeper Channel 4", unit="V", get_cmd=get_get_dac(4), set_cmd=get_set_dac(4))
		self.ch5 = Parameter("gk_ch5", label="Gatekeeper Channel 5", unit="V", get_cmd=get_get_dac(5), set_cmd=get_set_dac(5))
		self.ch6 = Parameter("gk_ch6", label="Gatekeeper Channel 6", unit="V", get_cmd=get_get_dac(6), set_cmd=get_set_dac(6))
		self.ch7 = Parameter("gk_ch7", label="Gatekeeper Channel 7", unit="V", get_cmd=get_get_dac(7), set_cmd=get_set_dac(7))


if __name__ == "__main__":

	gk = gatekeeper("gatekeeper", "COM3", initialize=True)

	print(gk.ch0.get())
