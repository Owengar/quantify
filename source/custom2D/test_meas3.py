from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A


import json
import numpy
import qcodes
from qcodes import Parameter, Instrument
import quantify_core
import quantify_core.data
import quantify_core.data.handling
from quantify_core.measurement import Gettable, MeasurementControl
import sys, os, time
import subprocess
import multiprocessing
import threading
import ctypes
from ctypes import *
from ctypes.wintypes import *
import xarray
import pickle
import exchanger
import cpp_interface.transfer as transfer







def make_setpoint_list(ranges : list[tuple[float, float, int]], parameter : Parameter, meas_ctrl : MeasurementControl):
	
	"""This is a helper function to assemble a setpoint list that is assembled in parts.
	
	The "ranges" parameter is a list of (start, stop, step_count) tuples, identical to what is inputted into the numpy.linspace function.
	
	All ranges in the list will be concatenated together into one numpy array and then returned."""

	if not hasattr(meas_ctrl, "_settables_setpoints"):
		meas_ctrl._settables_setpoints = {}
	if not hasattr(meas_ctrl, "_settables_ranges"):
		meas_ctrl._settables_ranges = {}

	base_list = []
	for setpoint_range in ranges:
		base_list.extend(list(numpy.linspace(setpoint_range[0], setpoint_range[1], setpoint_range[2])))

	meas_ctrl._settables_ranges[parameter.label + f" ({parameter.unit})"] = ranges
	meas_ctrl._settables_setpoints[parameter.name] = base_list





if __name__ == "__main__":
	quantify_core.data.handling.set_datadir(".\\datadir")


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
		return sweep_number() + numpy.sin(dummy_voltage_source()) * numpy.sin(i) * 10
	def measured_voltage_get_second(): #this is to differentiate it from the first gettable
		return sweep_number() * numpy.sin(dummy_voltage_source()) * 20
	measured_voltage = Parameter("measured_voltage", dummy_instrument, "Dummy Measured Voltage", unit="V", get_cmd=measured_voltage_get, bind_to_instrument=True)
	second_gettable = Parameter("second_gettable", dummy_instrument, "Extra Gettable", unit="V", get_cmd=measured_voltage_get_second, bind_to_instrument=True)





	dummy_voltage_source.inter_delay = 0

	meas_ctrl.settables([dummy_voltage_source, sweep_number])
	meas_ctrl.gettables([measured_voltage, second_gettable])

	make_setpoint_list([(-2, 2, 100)], dummy_voltage_source, meas_ctrl)
	make_setpoint_list([(1, 100, 100)], sweep_number, meas_ctrl)


	

	#this will be done automatically with init function
	setpoints_grid_list = []
	for settable_par in meas_ctrl._settable_pars:
		setpoint_list = meas_ctrl._settables_setpoints.get(settable_par.name)
		setpoints_grid_list.append(setpoint_list)
	meas_ctrl.setpoints_grid(setpoints_grid_list)
	meas_ctrl._init("hi")



	meas_ctrl._gettables_names = []
	def rename_coord_sorter(name):
		return name[1]
	rename_dict = {}
	sorted_coords = list(meas_ctrl._dataset.coords._names)
	sorted_coords.sort(key=rename_coord_sorter)
	for i,settable_coord in enumerate(sorted_coords):
		rename_dict[settable_coord] = meas_ctrl._settable_pars[i].label + f" ({meas_ctrl._settable_pars[i].unit})"
	for i,gettable_coord in enumerate(meas_ctrl._dataset.data_vars.keys()):
		rename_dict[gettable_coord] = meas_ctrl._gettable_pars[i].label + f" ({meas_ctrl._gettable_pars[i].unit})"
		meas_ctrl._gettables_names.append(meas_ctrl._gettable_pars[i].label + f" ({meas_ctrl._gettable_pars[i].unit})")

	

	#i have no idea why i made this
	update_dict = {}
	for var_to_rename in rename_dict:
		update_dict[rename_dict[var_to_rename]] = []

	meas_ctrl._settables_names = [settable.label+ f" ({settable.unit})" for settable in meas_ctrl._settable_pars]
	def prep_traces_dset(initial=False):
		if initial:
			return meas_ctrl._dataset.rename_vars(rename_dict)
		else:
			dictionary = {}
			dset = meas_ctrl._dataset.rename_vars(rename_dict)
			for var_to_rename in rename_dict:
				dictionary[rename_dict[var_to_rename]] = list(dset.get(rename_dict[var_to_rename]).data)
			#print(dictionary)
			return dictionary
	

	def clamp(value, min_value, max_value):
		return max(min_value, min(value, max_value))
	
	def correct_from_estimation(formatted_dset_1, estimation, radius=20):
		for k in range(clamp(estimation-radius, 0, len(formatted_dset_1)), clamp(estimation+radius+1, 0, len(formatted_dset_1))):
			this_one_is_nan = numpy.isnan(formatted_dset_1[k])
			if k == estimation-radius and this_one_is_nan:
				return "broke"
			if this_one_is_nan:
				#print(f"saved by diff of: {k-estimation}")
				return k
		else:
			return len(formatted_dset_1)
	def transfer_all_gettable_arrays():
		global i

		prepped_dset = prep_traces_dset(initial=False)
		formatted_dset = prepped_dset[meas_ctrl._gettables_names[0]]

		result = correct_from_estimation(formatted_dset, i)

		if result == "broke":
			print("FAILED transfer")
			return
		else:
			for gettable_label in meas_ctrl._gettables_names:
				index = meas_ctrl._gettables_names.index(gettable_label)
				transfer.write_array(index, prepped_dset[gettable_label])
			transfer.handle.set_setp_index(result)


		"""
		if i==len(formatted_dset):
			print("sucessful transfer!")
			for gettable_label in meas_ctrl._gettables_names:
				index = meas_ctrl._gettable9s_names.index(gettable_label)
				transfer.write_array(index, prepped_dset[gettable_label])
			transfer.handle.set_setp_index(i)
		elif (not numpy.isnan(formatted_dset[i-1])) and numpy.isnan(formatted_dset[i]):
			print("sucessful transfer!")
			for gettable_label in meas_ctrl._gettables_names:
				index = meas_ctrl._gettables_names.index(gettable_label)
				transfer.write_array(index, prepped_dset[gettable_label])
			transfer.handle.set_setp_index(i)
		else:
			print("FAILED transfer")
			return
		"""




	def compress_dset_json_for_initial_transfer(dset_json : json) -> json:
		data_vars = dset_json["data_vars"]
		for data_var_key in data_vars:
			var_container = data_vars[data_var_key]
			data_list_len = len(var_container["data"])
			var_container["data"].clear()
			var_container["data"].append(data_list_len)
		
		for coord in dset_json["coords"]:
			dset_json["coords"][coord]["data"].clear()
		dset_json["_settables_ranges"] = meas_ctrl._settables_ranges
		return dset_json
			

	def make_initial_writes(my_oned_id : int, settables_labels : list, gettables_labels : list, dataset : xarray.Dataset, name : str, data_store_path : str, parent_pid : int, mem_addresses : dict = {}) -> str:
		initial_writes = {}
		initial_writes["my_oned_id"] = str(my_oned_id)
		initial_writes["settables_labels"] = json.dumps(settables_labels)
		initial_writes["gettables_labels"] = json.dumps(gettables_labels)
		initial_writes["dataset"] = json.dumps(compress_dset_json_for_initial_transfer(dataset.to_dict()))
		initial_writes["name"] = name
		initial_writes["data_store_path"] = data_store_path
		initial_writes["parent_pid"] = str(parent_pid)
		initial_writes["mem_addresses"] = json.dumps(mem_addresses)

		return json.dumps(initial_writes) + "\n"

	

	#dset_as_dict = prep_traces_dset(initial=True).to_dict()
	#dset_as_dict["initial_writes"] =  str(0) + "\n" + json.dumps(meas_ctrl._settables_names) + "\n" + json.dumps(meas_ctrl._gettables_names) + "\n" + json.dumps(prep_traces_dset(initial=True).to_dict()) + "\n" + "hi" + "\n" + "storepatj" + "\n" + str(os.getpid()) + "\n" + "END\n"
 





	transfer.main(recompile=False)
	transfer.handle.set_setp_index(0)
	initial_writes = make_initial_writes(0, meas_ctrl._settables_names, meas_ctrl._gettables_names, prep_traces_dset(initial=True), "name of something!", "data store path!", os.getpid(), {"setp_index_address" : transfer.handle.get_setp_pointer(), "transfer_semaphore_address" : transfer.handle.get_transfer_semaphore_pointer()})
	ingester = subprocess.Popen(f"{sys.executable} mainv2D.py {transfer.get_child_args()}", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
	#ingester = subprocess.Popen("python dummy.py", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
	ingester.stdin.writelines(initial_writes)
	ingester.stdin.flush()


	i = 0
	def transfer_thread_func(transfer_frequency):
		"""transfer_frequency should be less than the data_ingester's "new_data_delay" """
		while ingester.poll() == None:
			exchanger.wait("0")
			transfer_all_gettable_arrays()
			exchanger.done("1")
			exchanger.wait_to_clear("012")
			time.sleep(transfer_frequency) 
			#print(i/(4000*1000) *100)
		print("Transfer thread stopped!")

	transfer_thread = threading.Thread(target=transfer_thread_func, args=(4,)) #A low transfer delay (high frequency), will cause more error on the plotting end, due to mismatch between setp_index and actual data,
	transfer_thread.start()
	#time.sleep(45)
	def talk():
		global i
		time.sleep(0.001) 
		i+=1


	meas_ctrl.run("hi", step_function=talk)

	while ingester.poll() == None:
		time.sleep(2)
		print("measurement finished, stalling...")