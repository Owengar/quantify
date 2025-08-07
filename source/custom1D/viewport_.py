import pygame, moderngl, numpy, typing, types, vectormath
import input_, display_manager_

class viewport():

	viewport_unforms = ["data_viewport", "data_viewport_start", "camera_viewport", "camera_viewport_start", "margin_percentages"]

	V2_ONE_nONE = vectormath.Vector2(1.0, -1.0)
	V2_ZERO_ONE = vectormath.Vector2(0.0, 1.0)


	def __init__(self, display_manager : display_manager_.display_manager, wrap_programs : dict, data_ingester):
		self.display_manager = display_manager
		self.data_ingester = data_ingester



		self.find_max_x = data_ingester.find_max_x
		self.find_max_y = data_ingester.find_max_y
		self.find_min_x = data_ingester.find_min_x
		self.find_min_y = data_ingester.find_min_y


		self._camera_viewport = numpy.array([1.0, 1.0], dtype=numpy.float32)
		self._camera_viewport_start = numpy.array([0.0, 0.0], dtype=numpy.float32)

		self.uniform_get_map = {"data_viewport" : self.get_data_viewport, "data_viewport_start" : self.get_data_viewport_start, "camera_viewport" : self.get_camera_viewport, "camera_viewport_start" : self.get_camera_viewport_start}

		for prog in wrap_programs:
			prog = wrap_programs[prog]
			prog.assign_uniforms = self.assign_viewport_uniforms

		self.biggest_x = 0
		self.biggest_y = 0


	def wrap_display_manager_render(self, prog):
		f = self.display_manager.render
		name = None
		fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__)
		# in case f was given attrs (note this dict is a shallow copy):
		fn.__dict__.update(f.__dict__)
		def new_render(*args):
			self.assign_viewport_uniforms(prog)
			print(args)
			fn(self.display_manager, *args)
		self.display_manager.render = new_render


	def wrap_display_manager_run_compute(self, prog):
		f = self.display_manager.run_compute
		name = None
		fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__)
		# in case f was given attrs (note this dict is a shallow copy):
		fn.__dict__.update(f.__dict__)
		def new_run(*args):
			self.assign_viewport_uniforms(prog)
			fn(self.display_manager, *args)
		self.display_manager.run_compute = new_run



	def assign_viewport_uniforms(self, prog):
		for needed_uniform in prog.needed_uniforms:
			if needed_uniform in __class__.viewport_unforms:
				prog[needed_uniform] = self.uniform_get_map[needed_uniform]()
		return
		prog["camera_viewport"] = self.get_camera_viewport()
		prog["camera_viewport_start"] = self.get_camera_viewport_start()
		return #BLANK SHADER
		self.program["data_viewport"] = self.get_data_viewport()
		self.program["data_viewport_start"] = self.get_data_viewport_start()

	def _get_data_viewport(self): #for pre calc
		ydif = self.find_max_y()-self.find_min_y()
		if ydif == 0:
			return numpy.array([self.find_max_x()-self.find_min_x(), ydif+1], dtype=numpy.float32)
		else:
			return numpy.array([self.find_max_x()-self.find_min_x(), ydif], dtype=numpy.float32)
	def get_data_viewport(self):
		return self._data_viewport
	def get_data_viewport_start(self):
		return numpy.array([self.find_min_x(), self.find_min_y()], dtype=numpy.float32)
	

	def get_camera_viewport(self):
		return self._camera_viewport
	def set_camera_viewport(self, new_viewport : tuple):
		self._camera_viewport[0] = new_viewport[0]
		self._camera_viewport[1] = new_viewport[1]
	
	def get_camera_viewport_start(self):
		return self._camera_viewport_start
	def set_camera_viewport_start(self, new_start : tuple):
		self._camera_viewport_start[0] = new_start[0]
		self._camera_viewport_start[1] = new_start[1]

	def mouse_drag(self, input : input_.input):
		if pygame.mouse.get_pressed()[0]:
			pygame.mouse.set_relative_mode(True)
			change = [input.mouse_vel[0] / self.display_manager.get_window_size()[0], input.mouse_vel[1] / self.display_manager.get_window_size()[1]]
			change[0] *= self.get_camera_viewport()[0]
			change[1] *= self.get_camera_viewport()[1]
			self.set_camera_viewport_start((self.get_camera_viewport_start()[0] - change[0], self.get_camera_viewport_start()[1] - change[1]))
		else:
			pygame.mouse.set_relative_mode(False)
	
	def zoom(self, input : input_.input):
		self.set_camera_viewport((self.get_camera_viewport()[0]*(50/(input.mwheel_scroll+50)), self.get_camera_viewport()[1]*(50/(input.mwheel_scroll+50))))
		window_size = self.display_manager.get_window_size()
		if input.mwheel_scroll:
			pass
			#self.set_camera_viewport_start((input.mouse_pos[0] / window_size[0], input.mouse_pos[1] / window_size[1]))

	def pre_calc_viewports(self):
		self._data_viewport = self._get_data_viewport()

		


	def find_min_x():
		pass
	def find_min_y():
		pass
	def find_max_x():
		pass
	def find_max_y():
		pass

	
