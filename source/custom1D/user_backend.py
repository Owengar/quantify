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
import traceback
import threading
import ctypes
from ctypes import *
from ctypes.wintypes import *
import xarray
import shutil
import quantify_core.data.handling as dh

import cpp_interface.transfer as transfer



def _prep_hdf5_dset(dataset : xarray.Dataset, measurement_control):
    rename_dict = {}
    for var in dataset.variables:
        rename_dict[var] = dataset[var].attrs.get("name", var)
    if len(measurement_control._setpoints_shape) > 1:
        dataset = dataset.assign_coords({"nD" : (xarray.DataArray(dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})

    if measurement_control.comments:
        dataset.attrs["comments"] = measurement_control.comments
        dataset.assign({"Comments" : measurement_control.comments})
    return dataset.rename_vars(rename_dict)


_name = "unnamed"
meas_ctrl = MeasurementControl("meas_ctrl")
def set_gettables(list_of_gettables : list[Parameter]):
	meas_ctrl.gettables(list_of_gettables)
def set_settables(list_of_settables : list[Parameter]):
	meas_ctrl.settables(list_of_settables)
def set_measurement_name(name : str):
	global _name
	_name = name

def make_setpoint_list(ranges : list[tuple[float, float, int]], parameter : Parameter): #meas_ctrl : MeasurementControl used to be a param before it went global :(
	global meas_ctrl
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





def run():
	global meas_ctrl, i
	quantify_core.data.handling.set_datadir(".\\datadir")
	



	


	



	

	#this will be done automatically with init function
	setpoints_grid_list = []
	for settable_par in meas_ctrl._settable_pars:
		setpoint_list = meas_ctrl._settables_setpoints.get(settable_par.name)
		setpoints_grid_list.append(setpoint_list)
	meas_ctrl.setpoints_grid(setpoints_grid_list)
	meas_ctrl._init(_name)



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
		transfer.handle.set_transfer_semaphore(True)


		prepped_dset = prep_traces_dset(initial=False)
		formatted_dset = prepped_dset[meas_ctrl._gettables_names[0]]

		result = correct_from_estimation(formatted_dset, i)

		if result == "broke":
			print("FAILED transfer")
			return
		else:
			#print("sucessful transfer!")
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
 





	transfer.main()
	transfer.handle.set_setp_index(0)
	transfer.handle.set_transfer_semaphore(False)
	initial_writes = make_initial_writes(0, meas_ctrl._settables_names, meas_ctrl._gettables_names, prep_traces_dset(initial=True), "name of something!", "data store path!", os.getpid(), {"setp_index_address" : transfer.handle.get_setp_pointer(), "transfer_semaphore_address" : transfer.handle.get_transfer_semaphore_pointer()})
	ingester = subprocess.Popen(f"{sys.executable} mainv2.py {transfer.get_child_args()}", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
	#ingester = subprocess.Popen("python dummy.py", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
	ingester.stdin.writelines(initial_writes)
	ingester.stdin.flush()


	i = 0
	def transfer_thread_func(transfer_frequency):
		"""transfer_frequency should be less than the data_ingester's "new_data_delay" """
		while ingester.poll() == None:
			transfer_all_gettable_arrays()
			transfer.handle.set_transfer_semaphore(False)
			time.sleep(transfer_frequency) 
		print("Transfer thread stopped!")

	transfer_thread = threading.Thread(target=transfer_thread_func, args=(0.1,))
	transfer_thread.start()
	#time.sleep(45)
	def talk():
		global i
		i+=1


	meas_ctrl.run("hi", step_function=talk)

	while ingester.poll() == None:
		time.sleep(2)
		print("measurement finished, stalling...")

	#taken!!!!
	

	try:
		meas_ctrl.comments
	except:
		meas_ctrl.comments = ""
	meas_ctrl._setpoints_shape = [len(i) for i in meas_ctrl._setpoints_input]
	def _make_data_store_path():
		measurements_dir = f"{os.environ['USERPROFILE']}\\Box\\Quantum Device Lab\\Quantify\\Measurements"
		import datetime
		now = datetime.datetime.now()
		measurements_dir += f"\\{now.year}"
		if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt"):
			with open(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt", "r") as install_info:
				measurements_dir += f"\\{install_info.readline().removesuffix('\n')}"
		else:
			measurements_dir += f"\\{os.path.basename(os.environ['USERPROFILE'])}"
		measurements_dir += f"\\{now.month}"
		measurements_dir += f"\\{now.day}"
		if not os.path.exists(measurements_dir):
			os.makedirs(measurements_dir)
		return measurements_dir
	data_store_path = _make_data_store_path()

	data_store_path += f"\\{meas_ctrl._dataset.attrs['name']}_dataset_{meas_ctrl._dataset.attrs['tuid']}"
	if not os.path.exists(data_store_path):
		os.makedirs(data_store_path)
	dataset_path_name = data_store_path+f"\\{meas_ctrl._dataset.attrs['name']}_dataset_{meas_ctrl._dataset.attrs['tuid']}.hdf5"
	def save_measurement_script():
		script_path = traceback.extract_stack()[0].filename
		shutil.copy(script_path, data_store_path+f"\\Script - {script_path.split("\\")[-1]}")
	save_measurement_script()

	dh.write_dataset(dataset_path_name, _prep_hdf5_dset(meas_ctrl._dataset, meas_ctrl))