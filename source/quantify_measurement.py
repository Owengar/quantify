
from source.imports import *

#remove old datadir
try:
	shutil.rmtree(".\\datadir", True)
except:
	pass

### globals
_measurement_name = "Unnamed Measurement"
_profile_name = "Unnamed Profile"
_meas_ctrl = MeasurementControl("meas_ctrl")
_start_time = saver.get_formatted_time()
###


def set_gettables(list_of_gettables : list[Parameter]):
	_meas_ctrl.gettables(list_of_gettables)
def set_settables(list_of_settables : list[Parameter]):
	_meas_ctrl.settables(list_of_settables)
def set_measurement_name(name : str):
	global _measurement_name
	_measurement_name = name
def set_profile_name(name : str):
	global _profile_name
	_profile_name = name
def set_comments(comments: str):
    _meas_ctrl.comments = comments
def make_setpoint_list(ranges : list[tuple[float, float, int]], parameter : Parameter): #meas_ctrl : MeasurementControl used to be a param before it went global :(
	"""Function to assign setpoints to a settable parameter.
	
	The "ranges" parameter is a list of (start, stop, step_count) tuples, each of these tuples are identical to what is inputted into the numpy.linspace function.
	
	The "parameter" parameter is the target settble parameter that will be assigned the setpoints."""
	global _meas_ctrl

	if not hasattr(_meas_ctrl, "_settables_setpoints"):
		_meas_ctrl._settables_setpoints = {}
	if not hasattr(_meas_ctrl, "_settables_ranges"):
		_meas_ctrl._settables_ranges = {}

	base_list = []
	for setpoint_range in ranges:
		base_list.extend(list(numpy.linspace(setpoint_range[0], setpoint_range[1], setpoint_range[2])))

	_meas_ctrl._settables_ranges[parameter.label + f" ({parameter.unit})"] = ranges
	_meas_ctrl._settables_setpoints[parameter.name] = base_list




















def save_procedure(prepped_traces_dset):
	global _meas_ctrl

	#first make sure that _meas_ctrl.comments is a real variable
	try:
		_meas_ctrl.comments
	except:
		_meas_ctrl.comments = ""
	_meas_ctrl._setpoints_shape = [len(i) for i in _meas_ctrl._setpoints_input] #this needs to be done before prep_hdf5_dset

	try:
		data_store_path = saver.make_data_store_path(_meas_ctrl) #get data_store_path
		saver.save_measurement_script(data_store_path)
		saver.save_hdf5(data_store_path, _meas_ctrl)


		parameters = [{"settables" : [{name : _meas_ctrl._setpoints_shape[i]} for i,name in enumerate(_meas_ctrl._settables_names)]}, {"recorded" : [name for name in _meas_ctrl._gettables_names]}]
		other_data = {"profile_name" : _profile_name, "measurement_name" : _measurement_name, "comments" : _meas_ctrl.comments, "dimension" : len(_meas_ctrl._setpoints_shape), "start_time" : _start_time, "stop_time" : saver.get_formatted_time(), "finished_measurement" : True, "parameters": parameters, "computer_name" : saver.get_computer_name()}
		json.dump(other_data, open(data_store_path+"\\other_data.json", "w"))
		json.dump(prepped_traces_dset, open(data_store_path+"\\json_dataset.json", "w"))

		#send out screenshot request to proc_id 0
		qfy_tools.debug_print(saver.request_screenshot(data_store_path))
	except:
		pass
	try:
		data_store_path = saver.make_local_data_store_path(_meas_ctrl) #get data_store_path
		saver.save_measurement_script(data_store_path)
		saver.save_hdf5(data_store_path, _meas_ctrl)


		parameters = [{"settables" : [{name : _meas_ctrl._setpoints_shape[i]} for i,name in enumerate(_meas_ctrl._settables_names)]}, {"recorded" : [name for name in _meas_ctrl._gettables_names]}]
		other_data = {"profile_name" : _profile_name, "measurement_name" : _measurement_name, "comments" : _meas_ctrl.comments, "dimension" : len(_meas_ctrl._setpoints_shape), "start_time" : _start_time, "stop_time" : saver.get_formatted_time(), "finished_measurement" : True, "parameters": parameters, "computer_name" : saver.get_computer_name()}
		json.dump(other_data, open(data_store_path+"\\other_data.json", "w"))
		json.dump(prepped_traces_dset, open(data_store_path+"\\json_dataset.json", "w"))

		#send out screenshot request to proc_id 0
		qfy_tools.debug_print(saver.request_screenshot(data_store_path))
	except:
		pass









def run():
	global _meas_ctrl, i
	quantify_core.data.handling.set_datadir(".\\datadir")

	#this will be done automatically with init function
	setpoints_grid_list = []
	for settable_par in _meas_ctrl._settable_pars:
		setpoint_list = _meas_ctrl._settables_setpoints.get(settable_par.name)
		setpoints_grid_list.append(setpoint_list)
	_meas_ctrl.setpoints_grid(setpoints_grid_list)
	_meas_ctrl._init(_measurement_name)

	_meas_ctrl._gettables_names = []
	def rename_coord_sorter(name):
		return name[1]
	rename_dict = {}
	sorted_coords = list(_meas_ctrl._dataset.coords._names)
	sorted_coords.sort(key=rename_coord_sorter)
	for i,settable_coord in enumerate(sorted_coords):
		rename_dict[settable_coord] = _meas_ctrl._settable_pars[i].label + f" ({_meas_ctrl._settable_pars[i].unit})"
	for i,gettable_coord in enumerate(_meas_ctrl._dataset.data_vars.keys()):
		rename_dict[gettable_coord] = _meas_ctrl._gettable_pars[i].label + f" ({_meas_ctrl._gettable_pars[i].unit})"
		_meas_ctrl._gettables_names.append(_meas_ctrl._gettable_pars[i].label + f" ({_meas_ctrl._gettable_pars[i].unit})")

	#i have no idea why i made this
	update_dict = {}
	for var_to_rename in rename_dict:
		update_dict[rename_dict[var_to_rename]] = []

	_meas_ctrl._settables_names = [settable.label+ f" ({settable.unit})" for settable in _meas_ctrl._settable_pars]
	def prep_traces_dset(initial=False):
		if initial:
			return _meas_ctrl._dataset.rename_vars(rename_dict)
		else:
			dictionary = {}
			dset = _meas_ctrl._dataset.rename_vars(rename_dict)
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
		formatted_dset = prepped_dset[_meas_ctrl._gettables_names[0]]

		result = correct_from_estimation(formatted_dset, i)

		if result == "broke":
			qfy_tools.debug_print("FAILED transfer")
			return
		else:
			#print("sucessful transfer!")
			for gettable_label in _meas_ctrl._gettables_names:
				index = _meas_ctrl._gettables_names.index(gettable_label)
				transfer.write_array(index, prepped_dset[gettable_label])
			transfer.handle.set_setp_index(result)
	
	def compress_dset_json_for_initial_transfer(dset_json : json) -> json:
		data_vars = dset_json["data_vars"]
		for data_var_key in data_vars:
			var_container = data_vars[data_var_key]
			data_list_len = len(var_container["data"])
			var_container["data"].clear()
			var_container["data"].append(data_list_len)
		
		for coord in dset_json["coords"]:
			dset_json["coords"][coord]["data"].clear()
		dset_json["_settables_ranges"] = _meas_ctrl._settables_ranges
		return dset_json	

	def make_initial_writes(proc_id : int, my_oned_id : int, gettable_id : int, settables_labels : list, gettables_labels : list, dataset : xarray.Dataset, name : str, data_store_path : str, parent_pid : int, mem_addresses : dict = {}) -> str:
		initial_writes = {}
		initial_writes["proc_id"] = str(proc_id)
		initial_writes["my_oned_id"] = str(my_oned_id)
		initial_writes["gettable_id"] = str(gettable_id)
		initial_writes["settables_labels"] = json.dumps(settables_labels)
		initial_writes["gettables_labels"] = json.dumps(gettables_labels)
		initial_writes["dataset"] = json.dumps(compress_dset_json_for_initial_transfer(dataset.to_dict()))
		initial_writes["name"] = name
		initial_writes["data_store_path"] = data_store_path
		initial_writes["parent_pid"] = str(parent_pid)
		initial_writes["mem_addresses"] = json.dumps(mem_addresses)

		return json.dumps(initial_writes) + "\n"
	
	


	



	#General prep for any D measurement
	plot_procs = []
	transfer.main(recompile=False)
	transfer.handle.set_setp_index(0)
	transfer.handle.set_transfer_semaphore(False)
	initial_dset = prep_traces_dset(initial=True)



	proc_ids = {}
	proc_id = [0]
	def get_next_proc_id():
		id = proc_id[0]
		proc_id[0]+=1
		return id

	def start_2d_plotter(gettable_id):
		new_id = get_next_proc_id()
		ingester = subprocess.Popen(f"cd source/custom2D && {sys.executable} mainv2D.py {transfer.get_child_args()}", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
		initial_writes = make_initial_writes(new_id, 0, gettable_id, _meas_ctrl._settables_names, _meas_ctrl._gettables_names, initial_dset, _measurement_name, "data store path!", os.getpid(), {"setp_index_address" : transfer.handle.get_setp_pointer(), "transfer_semaphore_address" : transfer.handle.get_transfer_semaphore_pointer()})
		ingester.stdin.writelines(initial_writes)
		ingester.stdin.flush()
		proc_ids[ingester] = new_id
		plot_procs.append(ingester)
	def start_1d_plotter(oned_id, gettable_id):
		new_id = get_next_proc_id()
		ingester = subprocess.Popen(f"cd source/custom1D && {sys.executable} mainv2.py {transfer.get_child_args()}", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)
		initial_writes = make_initial_writes(new_id, oned_id, gettable_id, _meas_ctrl._settables_names, _meas_ctrl._gettables_names, initial_dset, _measurement_name, "data store path!", os.getpid(), {"setp_index_address" : transfer.handle.get_setp_pointer(), "transfer_semaphore_address" : transfer.handle.get_transfer_semaphore_pointer()})
		ingester.stdin.writelines(initial_writes)
		ingester.stdin.flush()
		proc_ids[ingester] = new_id
		plot_procs.append(ingester)



	#IF this is a 2D measurement
	if len(setpoints_grid_list) == 2:
		for i in range(len(_meas_ctrl._gettable_pars)): #for every gettable parameter, open up a 2d plot with gettable as color axis
			start_2d_plotter(i)
		for i in range(len(_meas_ctrl._settable_pars)): #for every settable parameter, open up a 1d plot with the settable as x-axis
			start_1d_plotter(i, 0) #no extra gettables
	if len(setpoints_grid_list) == 1: #if its a 1D measurement
		for i in range(len(_meas_ctrl._gettable_pars)):
			start_1d_plotter(0, i)

	def plotters_running():
		return_value = False
		for proc in plot_procs:
			if proc.poll() == None:
				return_value = True
			else:
				proc_id = proc_ids[proc]
				plot_procs.remove(proc)
				exchanger.remove_exchanger(proc_id)
		if return_value:
			return True
		else:
			return False
	exchanger.find_exchangers(len(plot_procs)) #setup our meas-side exchanger

	#Start meas
	i = 0
	def transfer_thread_func_exchanger(transfer_frequency):
		"""transfer_frequency should be less than the data_ingester's "new_data_delay" """
		while plotters_running():
			#wait for all plotters to be in the asking state
			exchanger.wait_for_all_asking(plotters_running)
			transfer_all_gettable_arrays()
			exchanger.give_all_one()
			exchanger.wait_to_clear(plotters_running)
			time.sleep(transfer_frequency) 
		print("No longer tranfering data to plotters. Tranfer thread stopped...")


	transfer_thread = threading.Thread(target=transfer_thread_func_exchanger, args=(0.1,))
	transfer_thread.start()

	#find total number of setpoints for use in percentage printing
	number_of_setpoints = 1
	for setpoint_set in _meas_ctrl._setpoints_input:
		number_of_setpoints *= len(setpoint_set)
	#
	def talk():
		global i
		i+=1
		print(f"Setpoint {i}/{number_of_setpoints} | {i/number_of_setpoints*100:.2f}%")


	_meas_ctrl.run("hi", step_function=talk, lazy_set=True)

	print("Wait... Saving measurement data...")
	save_procedure(prep_traces_dset())
	print("Measurement data saved!")
	while plotters_running():
		time.sleep(2)
		print("Measurement finished, stalling...")
	print("Measurement finished, done stalling!")

	#now, control will go back to script to execute any post measurement operations


