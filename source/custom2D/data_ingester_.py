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
		self.new_data_delay = new_data_delay
		self.measurement_finished = False
		self.data_trace_splits = []
		self.ingest_thread = None
		self.gettables_lock = threading.Lock()
		self.latest_formatted_dset = numpy.array([numpy.nan]*4000000, dtype=numpy.float32)
		self.setp_index = 0
		self.minx = 0
		self.maxx = 0
		self.miny = 0
		self.maxy = 0
		self.max = 0
		self.min = 0


		self.setpoints_lengths = []


	
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
			# support both compressed form ([length]) and full-data form ([v0, v1, ...])
			data_field = var_container.get("data", [])
			if len(data_field) == 1 and (isinstance(data_field[0], int) or (hasattr(data_field[0], "dtype") and numpy.issubdtype(data_field[0].dtype, numpy.integer))):
				data_list_len = int(data_field[0])
			else:
				# already full data list
				data_list_len = len(data_field)
			var_container["data"] = [numpy.nan] * data_list_len

		setpoints_grid_list = []
		if "_settables_ranges" in dset_json:
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
		else:
			for coord in dset_json["coords"]:
				self.data_trace_splits.append(len(dset_json["coords"][coord]["data"]))
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
		pygame.display.set_caption(name + f"  -  {self.my_gettable_label} vs. {self.my_label} and {self.twod_plot_other_label}")


	

	def prep_initial_data(self):
		all_coords = self.settables_labels.copy()
		other_coords = self.settables_labels.copy()
		other_coords.remove(self.settables_labels[self.my_oned_id])

		self.setpoints = {}
		for settable in self.settables_labels.copy():
			self.setpoints[settable] = numpy.unique(self.dataset.get(settable).data)
		setpoints_shape = [len(self.setpoints[i]) for i in self.settables_labels]

		x_setpoints = []
		y_setpoints = []
		for i,name in enumerate(self.setpoints):
			if i==0:
				x_setpoints.extend(list(self.setpoints[name].astype(float)))
			elif i==1:
				y_setpoints.extend(list(self.setpoints[name].astype(float)))
			self.setpoints_lengths.append(len(self.setpoints[name]))


		pov_setpoints = {}

		self.my_label = self.settables_labels[self.my_oned_id]
		if self.my_oned_id == 0:
			self.twod_plot_other_label = self.settables_labels[1]
		elif self.my_oned_id == 1:
			self.twod_plot_other_label = self.settables_labels[0]

		self.my_gettable_label = self.gettables_labels[self.gettable_id]

		shifted_labels = self.settables_labels.copy()
		while shifted_labels[0] != self.my_label:
			shifted_labels = shifted_labels[1:] + shifted_labels[:1]
		for settable in shifted_labels:
			pov_setpoints[settable] = numpy.unique(self.dataset.get(settable).data)
		self.pov_setpoints_shape = [len(pov_setpoints[i]) for i in shifted_labels]



		sorted_getpoints = self.dataset.sortby(self.settables_labels[self.my_oned_id]).get(self.gettables_labels[0])
		#self.start_index = [numpy.where(numpy.isnan(sorted_getpoints.data), False, True)]
		#self.latest_index = [len(self.dataset.get(self.color_label).dropna("dim_0"))]



	def debug_wait(self):
		sys.stdout.write(f"hola\n")
		sys.stdout.flush()
		thing = sys.stdin.readline().removesuffix("\n")
		sys.stdout.write(f"{thing} +  bye\n")
		sys.stdout.flush()

	def check_for_screenshot_request(self, screenshot_func):
		check_path = os.path.abspath("data_ingester_.py").removesuffix("custom2D\\data_ingester_.py")
		if os.path.exists(f"{check_path}\\screenshot_{self.proc_id}.txt"):
			with open(f"{check_path}\\screenshot_{self.proc_id}.txt", "r") as screenshot_request:
				screenshot_save_path=screenshot_request.readline().removesuffix("\n")
			screenshot_func(screenshot_save_path)
			os.remove(f"{check_path}\\screenshot_{self.proc_id}.txt")



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
		result = numpy.max(self.setpoints[self.twod_plot_other_label])
		return result #only doing firsty gettable
	def _find_min_y(self):
		result = numpy.min(self.setpoints[self.twod_plot_other_label])
		return result #only doing firsty gettable
	###
	def pre_calc_minmax(self):
		self.minx = self._find_min_x()
		self.maxx = self._find_max_x()
		self.miny = self._find_min_y()
		self.maxy = self._find_max_y()


	def better_minmax(self):
		self.max = numpy.nanmax(self.latest_formatted_dset)
		self.min = numpy.nanmin(self.latest_formatted_dset)

	def ingest(self):
		exchanger.ask() #our ask
		exchanger.wait("01") #wait for a response to our ask (when there is a 1 somewhere)

		with self.gettables_lock:
			for gettable_label in self.gettables_labels:
				index = self.gettables_labels.index(gettable_label)
				self.gettables_dset[gettable_label] = transfer.child_get_array(index).copy() #might want to do this in the 1D
			self.latest_formatted_dset = self.format_data(0, 0).copy()
			self.setp_index = transfer.handle.get_setp_index(self.mem_addresses["setp_index_address"])
			self.better_minmax()
			self.pre_calc_minmax()

			self.draw2D()
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
			return gettable_array
		else:
			return thing.sort(axis=1)
	
	def format_data_sep(self, settables_index, gettables_index):
		settable_label = self.settables_labels[settables_index]
		gettable_label = self.gettables_labels[gettables_index]
		x_array = numpy.array(self.dataset[settable_label].data).astype(numpy.float32)
		y_array = numpy.array(self.gettables_dset[gettable_label][0:len(self.dataset[settable_label])]).astype(numpy.float32)
		x_array.sort()
		thing = numpy.column_stack((self.dataset[settable_label], self.gettables_dset[gettable_label][0:len(self.dataset[settable_label])])).astype(numpy.float32)

	def draw2D(self):
		#carry in functions :)
		def colormap(normalized_val : float):
			color = self.cmap(normalized_val)
			return (int(color[0]*255), int(color[1]*255), int(color[2]*255), 255)
		def did_range_change(new_max, new_min):
			if self.old_max != new_max:
				self.old_min = new_min
				self.old_max = new_max
				return True
			if self.old_min != new_min:
				self.old_min = new_min
				self.old_max = new_max
				return True
			return False
		def normalize_get(value):
			if 0 == (self.max-self.min):
				return 0
			return (value-self.min) / (self.max-self.min)
		def full_recolor(dset, surf):
			for x in range(self.setpoints_lengths[0]):
				#time.sleep(0.001)
				for y in range(self.setpoints_lengths[1]):
					dpoint = dset[(y*self.setpoints_lengths[0]) + x]
					if numpy.isnan(dpoint):
						continue
					else:
						color_mapped = colormap(normalize_get(dset[(y*self.setpoints_lengths[0]) + x]))
						try:
							surf.pyg_surf.set_at((x, y), color_mapped)
						except:
							pass

		formatted_dset = self.latest_formatted_dset #data_ingester.format_data(0, 0)
		total = len(formatted_dset)
		if did_range_change(self.max, self.min):
			full_recolor(formatted_dset, self.draw_surface)

		self.end_index = self.setp_index
		if self.start_index != self.end_index:
			self.data_wrote_accumulation += len(formatted_dset[self.start_index:self.end_index])
			for index,data_point in enumerate(formatted_dset[self.start_index:self.end_index]):
				index += self.start_index
				x = index%self.setpoints_lengths[0]
				y = index//self.setpoints_lengths[0]
				color_mapped = colormap(normalize_get(data_point))
				ycol = normalize_get(data_point) * 255
				if numpy.isnan(data_point):
					print("BROKEEE")
					time.sleep(5)
					continue
				self.draw_surface.pyg_surf.set_at((x, y), color_mapped)
			qfy_tools.debug_print(f"wrote {len(formatted_dset[self.start_index:self.end_index])} points to IMAGE, {self.data_wrote_accumulation}/{len(formatted_dset)}")
			self.start_index = self.end_index
	



	def start_ingest_thread(self, draw_surf, colormap):
		self.draw_surface = draw_surf
		self.cmap = colormap
		self.old_max= 0
		self.old_min = 0
		self.data_wrote_accumulation = 0
		self.start_index = 0
		self.end_index = 0
		def ingester_thread():
			while not self.measurement_finished:
				self.ingest()
				time.sleep(self.new_data_delay)
		self.ingest_thread = threading.Thread(target=ingester_thread)
		self.ingest_thread.start()
