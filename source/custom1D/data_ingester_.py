import sys, xarray, json, numpy, threading, time, os
import cpp_interface.transfer as transfer
import quantify_core.measurement
import qcodes
import pygame
import qfy_tools

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import exchanger

def blank_set(value):
	pass

class data_ingester():
	def __init__(self, running : list[bool], paused : list[bool], new_data_delay : float = 1.0):
		self.t1_done = True
		self.stdin_full = False
		self.running = running
		self.paused = paused
		self.debug = open("main_debug.txt", "w")
		self.time_of_last_ingest = 0.0
		self.new_data_delay = new_data_delay
		self.measurement_finished = False
		self.data_trace_splits = []
		self.ingest_thread = None
		self.gettables_lock = threading.Lock()
		self.latest_formatted_dset = None
		self.setp_index = 0
	


	
	def make_setpoint_list(ranges : list[tuple[float, float, int]]):
		"""This is a helper function to assemble a setpoint list that is assembled in parts.
		
		The "ranges" parameter is a list of (start, stop, step_count) tuples, identical to what is inputted into the numpy.linspace function.
		
		All ranges in the list will be concatenated together into one numpy array and then returned."""
		base_list = []
		for setpoint_range in ranges:
			base_list.extend(list(numpy.linspace(setpoint_range[0], setpoint_range[1], setpoint_range[2])))
		return numpy.array(base_list)
	
	def _setpoints_grid(self, setpoints_grid_list):
		meas_ctrl = quantify_core.measurement.control.MeasurementControl("throwaway_meas_ctrl")
		quantify_core.data.handling.set_datadir(".\\datadir")
		dummy_gettable = qcodes.Parameter("dummy_gettable")
		
		settables_params = []
		for i in range(len(setpoints_grid_list)): #makes a dummy settable param for every setpoint list in setpoints_grid_list
			settables_params.append(qcodes.Parameter(f"x{i}", set_cmd=blank_set))
		meas_ctrl.settables(settables_params)
		meas_ctrl.gettables([dummy_gettable])
		meas_ctrl.setpoints_grid(setpoints_grid_list)
		meas_ctrl._init("throwaway")
		dset = meas_ctrl._dataset
		return_list = []
		for i in range(len(setpoints_grid_list)):
			return_list.append(list(dset.get(f"x{i}").data))
		return return_list
	
	def decompress_initial_json_dset(self, dset_json : json) -> json:
		data_vars = dset_json["data_vars"]
		for data_var_key in data_vars:
			var_container = data_vars[data_var_key]
			data_list_len = var_container["data"][0]
			var_container["data"] = [numpy.nan] * data_list_len

		setpoints_grid_list = []
		for coord in dset_json["coords"]:
			setpoint_ranges = dset_json["_settables_ranges"][coord]
			for setpoint_range in setpoint_ranges:
				dset_json["coords"][coord]["data"].extend(list(numpy.linspace(setpoint_range[0], setpoint_range[1], setpoint_range[2])))
			self.data_trace_splits.append(len(dset_json["coords"][coord]["data"]))
			setpoints_grid_list.append(dset_json["coords"][coord]["data"])
		returned = self._setpoints_grid(setpoints_grid_list)

		for i,coord in enumerate(dset_json["coords"]):
			dset_json["coords"][coord]["data"].clear()
			dset_json["coords"][coord]["data"].extend(returned[i])
		return dset_json

	def wait_for_initial_data(self):
		transfer.child_main()
		initial_writes : dict = json.loads(sys.stdin.readline())

		proc_id = int(initial_writes.get("proc_id").removesuffix("\n"))
		gettable_id = int(initial_writes.get("gettable_id").removesuffix("\n"))
		my_oned_id = int(initial_writes.get("my_oned_id").removesuffix("\n"))
		settables_labels = json.loads(initial_writes.get("settables_labels"))
		gettables_labels = json.loads(initial_writes.get("gettables_labels").removesuffix("\n"))
		dataset = xarray.Dataset.from_dict(self.decompress_initial_json_dset(json.loads(initial_writes.get("dataset"))))
		name = initial_writes.get("name").removesuffix("\n")
		data_store_path = initial_writes.get("data_store_path").removesuffix("\n")
		parent_pid = int(initial_writes.get("parent_pid").removesuffix("\n"))
		mem_addresses = json.loads(initial_writes.get("mem_addresses"))

		qfy_tools.debug_print("done reading initial writes")
		self.proc_id = proc_id
		self.gettable_id = gettable_id
		self.my_oned_id = my_oned_id
		self.settables_labels = settables_labels
		self.gettables_labels = gettables_labels
		self.dataset = dataset
		self.name = name
		self.data_store_path = data_store_path
		self.parent_pid = parent_pid
		self.mem_addresses = mem_addresses

		self.gettables_dset = {}
		
		exchanger.set_proc_id(self.proc_id)
		self.prep_initial_data()
		pygame.display.set_caption(name + f"  -  {self.my_gettable_label} vs. {self.my_label}")

	def check_for_screenshot_request(self, screenshot_func):
		check_path = os.path.abspath("data_ingester_.py").removesuffix("custom1D\\data_ingester_.py")
		if os.path.exists(f"{check_path}\\screenshot_{self.proc_id}.txt"):
			with open(f"{check_path}\\screenshot_{self.proc_id}.txt", "r") as screenshot_request:
				screenshot_save_path=screenshot_request.readline().removesuffix("\n")
			screenshot_func(screenshot_save_path)
			os.remove(f"{check_path}\\screenshot_{self.proc_id}.txt")
	"""
	def initial_data_wait(self, seperate_lines = False):
		transfer.child_main()
		time.sleep(5)

		if seperate_lines:
			my_oned_id = int(sys.stdin.readline().removesuffix("\n"))
			settables_labels = json.loads(sys.stdin.readline())
			color_label = sys.stdin.readline().removesuffix("\n")
			dataset = xarray.Dataset.from_dict(json.loads(sys.stdin.readline()))
			name = sys.stdin.readline().removesuffix("\n")
			data_store_path = sys.stdin.readline().removesuffix("\n")
			parent_pid = int(sys.stdin.readline().removesuffix("\n"))
		else:
			print("reading")
			lines = []
			for line in sys.stdin:
				if line != "END\n":
					lines.append(line)
				else:
					break


			print("read")


			my_oned_id = int(lines[0].removesuffix("\n"))
			settables_labels = json.loads(lines[1])
			gettables_labels =  json.loads(lines[2].removesuffix("\n"))
			dataset = xarray.Dataset.from_dict(json.loads(lines[3]))
			name = lines[4].removesuffix("\n")
			data_store_path = lines[5].removesuffix("\n")
			parent_pid = int(lines[6].removesuffix("\n"))



		self.my_oned_id = my_oned_id
		self.settables_labels = settables_labels
		self.gettables_labels = gettables_labels
		self.dataset = dataset
		self.name = name
		self.data_store_path = data_store_path
		self.parent_pid = parent_pid

		self.gettables_dset = {}

		self.prep_initial_data()
	"""


	def prep_initial_data(self):
		all_coords = self.settables_labels.copy()
		other_coords = self.settables_labels.copy()
		other_coords.remove(self.settables_labels[self.my_oned_id])

		self.setpoints = {}
		for settable in self.settables_labels.copy():
			self.setpoints[settable] = numpy.unique(self.dataset.get(settable).data)
		setpoints_shape = [len(self.setpoints[i]) for i in self.settables_labels]


		pov_setpoints = {}

		self.my_label = self.settables_labels[self.my_oned_id]
		shifted_labels = self.settables_labels.copy()
		while shifted_labels[0] != self.my_label:
			shifted_labels = shifted_labels[1:] + shifted_labels[:1]
		for settable in shifted_labels:
			pov_setpoints[settable] = numpy.unique(self.dataset.get(settable).data)
		self.pov_setpoints_shape = [len(pov_setpoints[i]) for i in shifted_labels]

		self.my_gettable_label = self.gettables_labels[self.gettable_id]

		sorted_getpoints = self.dataset.sortby(self.settables_labels[self.my_oned_id]).get(self.gettables_labels[0])
		#start_index = [numpy.where(numpy.isnan(sorted_getpoints.data), False, True)]
		#self.latest_index = [len(self.dataset.get(self.color_label).dropna("dim_0"))]



	def debug_wait(self):
		sys.stdout.write(f"hola\n")
		sys.stdout.flush()
		thing = sys.stdin.readline().removesuffix("\n")
		sys.stdout.write(f"{thing} +  bye\n")
		sys.stdout.flush()




	def find_min_x(self):
		return self.minx
	def find_max_x(self):
		return self.maxx
	def find_max_y(self):
		return self.maxy #only doing firsty gettable
	def find_min_y(self):
		return self.miny #only doing firsty gettable
	
	###for pre calc
	def _find_min_x(self):
		result = numpy.min(self.setpoints[self.my_label])
		return result
	def _find_max_x(self):
		result = numpy.max(self.setpoints[self.my_label])
		return result
	def _find_max_y(self):
		result = numpy.nanmax(self.gettables_dset[self.my_gettable_label])
		return result #only doing firsty gettable
	def _find_min_y(self):
		result = numpy.nanmin(self.gettables_dset[self.my_gettable_label])
		return result #only doing firsty gettable
	###
	def pre_calc_minmax(self):
		self.minx = self._find_min_x()
		self.maxx = self._find_max_x()
		self.miny = self._find_min_y()
		self.maxy = self._find_max_y()
		"""def cached_minx():
			return self.minx
		def cached_maxx():
			return self.maxx
		def cached_miny():
			return self.miny
		def cached_maxy():
			return self.maxy
		self.find_min_x = cached_minx
		self.find_max_x = cached_maxx
		self.find_min_y = cached_miny
		self.find_max_y = cached_maxy"""

	def ingest(self):
		exchanger.ask() #our ask
		exchanger.wait("01") #wait for a response to our ask (when there is a 1 at the somewhere)
		#print("\ningested!!\n")

		with self.gettables_lock:
			for gettable_label in self.gettables_labels:
				index = self.gettables_labels.index(gettable_label)
				self.gettables_dset[gettable_label] = transfer.child_get_array(index).copy()
			self.latest_formatted_dset = self.format_data(0, 0).copy()
			self.setp_index = transfer.handle.get_setp_index(self.mem_addresses["setp_index_address"])
			self.pre_calc_minmax()
		exchanger.done("2")

	def format_data(self, settables_index, gettables_index, sort_by = "x"):
		#if not self.measurement_finished:
		#	self.check_ingest_schedule()

		#settable_label = self.settables_labels[settables_index]
		#gettable_label = self.gettables_labels[gettables_index]

		#print(self.gettables_dset[self.gettables_labels[0]][0:len(self.dataset[self.my_label])])
		gettable_array = self.gettables_dset[self.my_gettable_label][0:len(self.dataset[self.my_label])]
		thing = numpy.column_stack((self.dataset[self.my_label], gettable_array)).astype(numpy.float32) #the [0:len(self.dataset[self.my_label])] is just to take the whole array. The buffer is actually like 4 billion or something
		#print(f"{self.my_label} |and| {self.gettables_labels[0]} thing: ")
		if len(gettable_array) == self.setp_index:
			self.measurement_finished = True



		if sort_by == "x":
			return thing
		else:
			return thing.sort(axis=1)
	
	def format_data_sep(self, settables_index, gettables_index):
		settable_label = self.settables_labels[settables_index]
		gettable_label = self.gettables_labels[gettables_index]
		x_array = numpy.array(self.dataset[settable_label].data).astype(numpy.float32)
		y_array = numpy.array(self.gettables_dset[gettable_label][0:len(self.dataset[settable_label])]).astype(numpy.float32)
		x_array.sort()
		thing = numpy.column_stack((self.dataset[settable_label], self.gettables_dset[gettable_label][0:len(self.dataset[settable_label])])).astype(numpy.float32)

	def get_setpoints_diff(self):
		setpoints = self.dataset[self.my_label]
		first_setpoint = setpoints[0]
		all_of_first = setpoints.where(setpoints == first_setpoint)
		i=1
		while True:
			if all_of_first[i] == first_setpoint:
				break
			else:
				i+=1
		return i
	
	def get_setpoints_reps(self):
		setpoints = self.dataset[self.my_label]
		first_setpoint = setpoints[0]
		all_of_first = setpoints.where(setpoints == first_setpoint)
		return all_of_first.dropna(dim="dim_0").size
	
	def check_ingest_schedule(self):
		current_time = time.time()
		if (current_time - self.time_of_last_ingest) > self.new_data_delay:
			print("ingest time")
			self.ingest()
			self.time_of_last_ingest = time.time()

		

	def start_ingest_thread(self):
		def ingester_thread():
			while not self.measurement_finished:
				self.ingest()
				time.sleep(self.new_data_delay)
		self.ingest_thread = threading.Thread(target=ingester_thread)
		self.ingest_thread.start()
