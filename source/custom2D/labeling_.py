import pygame, time, numpy, moderngl, threading, mpl_colorbar, json, sys, subprocess, os
import display_manager_, surface_, viewport_, data_ingester_

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import new_unit_scale



def how_many_in_between(low, high, round_decimal):

	round_to = 1/(10**round_decimal)


	low_bound = round(low, round_decimal)
	if round(low, round_decimal) < low:
		low_bound += round_to
		if low_bound > high:
			return "bad"


	high_bound = round(high, round_decimal)
	if round(high, round_decimal) > high:
		high_bound -= round_to
		if high_bound < low:
			return "bad"



	return ((low_bound, high_bound), int(abs(high_bound-low_bound) / round_to)+1)

_decimal_checks = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
def get_axis_nums(low, high, ideal_num = 10):
	check_results = []
	for round_decimal in _decimal_checks:
		result = how_many_in_between(low, high, round_decimal)
		if result == "bad":
			continue
		else:
			check_results.append(how_many_in_between(low, high, round_decimal))

	def sort_key(check_result):
		return abs(check_result[1] - ideal_num)
	check_results.sort(key=sort_key)
	return numpy.linspace(check_results[0][0][0], check_results[0][0][1], check_results[0][1])



def map_ranges(val, in_min, in_max, out_min, out_max):
	out_val = out_min + ((val - in_min) / (in_max - in_min)) * (out_max - out_min)
	return out_val

class labeling():
	
	def __init__(self, display_manager : display_manager_.display_manager, label_surface : surface_.surface, viewport : viewport_.viewport, data_ingester : data_ingester_.data_ingester, draw_surface : surface_.surface, default_color : tuple[int, int, int] = (0, 0, 0, 255)):
		self.display_manager = display_manager
		self.label_surface = label_surface
		self.viewport = viewport
		self.data_ingester = data_ingester
		self.draw_surface = draw_surface

		self.x_label = data_ingester.my_label
		self.y_label = data_ingester.settables_labels[1]
		self.color_label = data_ingester.my_gettable_label
		self.viewport.uniform_get_map["margin_percentages"] = self.get_margin_percentages
		self.default_color = default_color
		self.margin_size = self.display_manager.get_shortest()*0.1
		self.extra_margin_size = self.display_manager.get_shortest()*0.15
		self.window_size = self.display_manager.get_window_size()
		self.grid_color = (10, 10, 10, 255)
		self.hover_bg_color = (220, 220, 220, 255)
		self.cb_drawer = None
		self.old_cb_surf = 0
		self._cache_margin_percentages()
		
		self.new = self.display_manager.ctx.buffer(reserve=4*2*2)
		pygame.font.init()

		#fonts
		self.fps_font = pygame.font.SysFont("arial", int(self.display_manager.get_shortest()*0.05))
		self.transferring_font = pygame.font.SysFont("arial", int(self.display_manager.get_shortest()*0.025))
		self.grid_num_font = pygame.font.SysFont("arial", int(self.display_manager.get_shortest()*0.015))
		self.grid_label_font = pygame.font.SysFont("times", int(self.display_manager.get_shortest()*0.035))
		self._x_label_surfs = {}
		self._y_label_surfs = {}
		self._pre_render_label_fonts(self.grid_label_font)

		#images
		transfer_symbol = pygame.image.load("images/downloadwhite.svg", "svg").convert_alpha()
		self.transfer_symbol = pygame.transform.scale(transfer_symbol, (display_manager.get_shortest()*0.08, display_manager.get_shortest()*0.08))

		#start up cb drawing
		self.start_colorbar_draw_proc()
	
	def _pre_render_label_fonts(self, font):
		for scale in new_unit_scale.prefix_scales_keys:
			#split the string (cuts off the "(")
			split_label_x = self.x_label.rsplit("(", maxsplit=1)
			split_label_x[1] = f"({scale}{split_label_x[1]}"
			new_x_label = split_label_x[0] + split_label_x[1]

			split_label_y = self.y_label.rsplit("(", maxsplit=1)
			split_label_y[1] = f"({scale}{split_label_y[1]}"
			new_y_label = split_label_y[0] + split_label_y[1]


			_x_label_surf = font.render(new_x_label, True, self.grid_color)
			_y_label_surf = font.render(new_y_label, True, self.grid_color)
			_y_label_surf = pygame.transform.rotate(_y_label_surf, 90)

			self._x_label_surfs[scale] = _x_label_surf
			self._y_label_surfs[scale] = _y_label_surf


	def _cache_margin_percentages(self):
		win_size_x, win_size_y = self.window_size
		self._margin_percentages = (self.margin_size / win_size_x, self.margin_size / win_size_y)

	def get_margin_percentages(self) -> tuple[float, float]:
		return self._margin_percentages 

	def draw_transfer_symbol(self):
		self.label_surface.blit(self.transfer_symbol, ((0.5*self.margin_size)-(0.5*self.transfer_symbol.size[0]), self.window_size[1]-(self.margin_size)+(0.5*self.margin_size)-(0.5*self.transfer_symbol.size[1])))


	def norm_pixel_to_data(self, data_pos: tuple[float, float]) -> tuple[float, float]:
		x, y = data_pos

		#step 7
		x, y = (x-1, y-1)
		# Step 6 Inverse: undo final remapping of y
		y = ((y + 1) / -1) + 1

		# Step 5 Inverse: subtract offset based on camera viewport start
		x -= ((1 / self.viewport.get_camera_viewport()[0]) * self.viewport.get_camera_viewport_start()[0] * -1)
		y -= ((1 / self.viewport.get_camera_viewport()[1]) * self.viewport.get_camera_viewport_start()[1] * 1)

		# Step 4 Inverse: subtract margin percentages
		x -= self.get_margin_percentages()[0]
		y -= self.get_margin_percentages()[1]

		# Step 3 Inverse: divide by camera viewport size
		x /= self.viewport.get_camera_viewport()[0]
		y /= self.viewport.get_camera_viewport()[1]

		# Step 2 Inverse: divide by (1 - margin percentages)
		x /= (1 - self.get_margin_percentages()[0])
		y /= (1 - self.get_margin_percentages()[1])

		# Step 1 Inverse: y inversion
		x, y = (x / 1, y * -1)

		return x, y

	def pixel_pos_to_data(self, pixel_pos : tuple[float, float]):
		x, y = pixel_pos #not normalized pixel coords
		#x, y = (x/self.window_size[0], y/self.window_size[1]) # vert

		"""
		vert = pygame.Vector2(x, y).elementwise()
		NONE_ONE = pygame.Vector2(-1.0, 1.0).elementwise()
		ONE_NONE = pygame.Vector2(1.0, -1.0).elementwise()
		ONE_ONE = pygame.Vector2(1.0, 1.0).elementwise()
		margin_percentages = pygame.Vector2(self.get_margin_percentages()).elementwise()
		camera_viewport_start = pygame.Vector2(self.viewport.get_camera_viewport_start()).elementwise()
		camera_viewport = pygame.Vector2(self.viewport.get_camera_viewport()).elementwise()
		camera_viewport_inverse = (ONE_ONE / camera_viewport).elementwise()
		res = ((((vert*ONE_NONE).elementwise()*(ONE_ONE-margin_percentages).elementwise()).elementwise()*camera_viewport).elementwise()+margin_percentages).elementwise()+((camera_viewport_inverse*camera_viewport_start).elementwise()*NONE_ONE).elementwise()
		"""
		#return (res.x, res.y)
		x, y = (x*1, y*-1) # vert*ONE_NONE
		x, y = (x * (1-self.get_margin_percentages()[0]),         y * (1-self.get_margin_percentages()[1])) # *(ONE_ONE-margin_percentages)
		x, y = (x * self.viewport.get_camera_viewport()[0],          y * self.viewport.get_camera_viewport()[1]) # *camera_viewport
		x, y = (x + self.get_margin_percentages()[0],    y + self.get_margin_percentages()[1]) # +margin_percentages
		x, y = (x + ((1/self.viewport.get_camera_viewport()[0])*self.viewport.get_camera_viewport_start()[0]*-1),           y + ((1/self.viewport.get_camera_viewport()[1])*self.viewport.get_camera_viewport_start()[1]*1)) # +(camera_viewport_inverse*camera_viewport_start*NONE_ONE)

		#gl_Position = vert*ONE_NONE*(ONE_ONE-margin_percentages)*camera_viewport+margin_percentages+(camera_viewport_inverse*camera_viewport_start*NONE_ONE)
		x, y = (x, ((y-1)*-1)-1)

		return x+1, y+1
		coord_x, coord_y = (x-(self.viewport.get_camera_viewport_start()[0]*-self.window_size[0]),     y-(self.viewport.get_camera_viewport_start()[1]*-self.window_size[1]))
		scalex, scaley = (self.draw_surface.target_scale[0] / self.draw_surface._size[0] * self.viewport.get_camera_viewport()[0],           self.draw_surface.target_scale[1] / self.draw_surface._size[1] * self.viewport.get_camera_viewport()[1])



		draw_surf_coord_x = (coord_x-self.margin_size)/scalex
		draw_surf_coord_y = (coord_y-self.margin_size)/scaley


		goalx = ((draw_surf_coord_x/self.data_ingester.setpoints_lengths[0])*abs(self.data_ingester.find_max_x()-self.data_ingester.find_min_x())) + self.data_ingester.find_min_x()
		goaly = (((draw_surf_coord_y/self.data_ingester.setpoints_lengths[1])*abs(self.data_ingester.find_max_y()-self.data_ingester.find_min_y())) + self.data_ingester.find_min_y()) * -1 + abs(self.data_ingester.find_max_y()-self.data_ingester.find_min_y())
		return (goalx, goaly)
	
	def full_pixel_to_data(self, pixel_pos : tuple[int, int]):
		
		x, y = pixel_pos
		x = x/self.window_size[0] * 2
		y = y/self.window_size[1] * 2

		new_dp = self.norm_pixel_to_data((x, y))

		data_x = map_ranges(new_dp[0], -1, -3, self.data_ingester.find_min_x(), self.data_ingester.find_max_x())
		data_y = map_ranges(new_dp[1], 1, 3, self.data_ingester.find_min_y(), self.data_ingester.find_max_y())

		data = (self.data_ingester.find_min_x()-data_x+self.data_ingester.find_min_x(), self.data_ingester.find_min_y()-data_y+self.data_ingester.find_min_y())

		return data

	def draw_hovering(self, mouse_pos):
		#pygame.draw.circle(self.label_surface.pyg_surf, (0, 255, 0, 255), mouse_pos, 8)
		data_point = self.full_pixel_to_data(mouse_pos)

		mapped_y = map_ranges(data_point[1], self.data_ingester.find_min_y(), self.data_ingester.find_max_y(), 0, 1)
		mapped_x = map_ranges(data_point[0], self.data_ingester.find_min_x(), self.data_ingester.find_max_x(), 0, 1)
		if numpy.isnan(mapped_x) or numpy.isnan(mapped_y):
			return
		if mapped_x > 1 or mapped_x < 0:
			return
		if mapped_y > 1 or mapped_y < 0:
			return
		x_pixel = int(mapped_x * self.draw_surface._size[0])
		y_pixel = int(mapped_y * self.draw_surface._size[1])


		try:
			data_point = self.data_ingester.setpoints[self.data_ingester.my_label][x_pixel], self.data_ingester.setpoints[self.data_ingester.twod_plot_other_label][y_pixel]
			color_data = self.data_ingester.latest_formatted_dset[(y_pixel*self.data_ingester.setpoints_lengths[0]) + x_pixel]
			hover_point_text = self.grid_label_font.render(f"[X: {str(float(data_point[0]))}, Y: {str(float(data_point[1]))}, Z: {str(color_data)}]", True, (0, 0, 0, 255), bgcolor=self.hover_bg_color)
			self.label_surface.pyg_surf.blit(hover_point_text, mouse_pos)
		except:
			pass


		return 
		mapped_y = map_ranges(data_point[1], self.data_ingester.find_min_y(), self.data_ingester.find_max_y(), 0, 1)
		mapped_x = map_ranges(data_point[0], self.data_ingester.find_min_x(), self.data_ingester.find_max_x(), 0, 1)
		
		if numpy.isnan(mapped_x) or numpy.isnan(mapped_y):
			return
		x_pixel = int(mapped_x * self.draw_surface._size[0])
		y_pixel = int(mapped_y * self.draw_surface._size[1])

		#pre_color = self.draw_surface.pyg_surf.get_at((x_pixel, y_pixel))
		self.draw_surface.pyg_surf.set_at((x_pixel, y_pixel), (0, 0, 0, 255))
		#pygame.draw.rect(self.label_surface.pyg_surf, (0, 0, 0, 255), (mouse_pos[0], mouse_pos[1], 20, 20), 3)

		return
		if numpy.isnan(ret_dpoint[3]):
			return
		
		hover_point_text = self.grid_label_font.render(str(ret_dpoint.tolist()[2:]), True, (0, 0, 0, 255))
		mouse_pos = (mouse_pos[0], mouse_pos[1]-hover_point_text.size[1])
		pygame.draw.circle(self.label_surface.pyg_surf, (255, 255, 0, 100), (int(ret_dpoint[0]), int(ret_dpoint[1])), 10)
		self.label_surface.pyg_surf.blit(hover_point_text, mouse_pos)


	def make_grid_list(self):
		
		#attempting the full function here
		data_top_right = self.full_pixel_to_data((self.window_size[0], 0))
		data_bottom_left = self.full_pixel_to_data((self.margin_size, self.window_size[1]-self.margin_size))



		x_data_points = get_axis_nums(data_bottom_left[0], data_top_right[0])
		x_pixel_points = [float((dp-data_bottom_left[0])/(data_top_right[0]-data_bottom_left[0])*(self.window_size[0]-self.margin_size)+self.margin_size) for dp in x_data_points]

		y_data_points = get_axis_nums(data_bottom_left[1], data_top_right[1])
		y_pixel_points = [float((dp-data_top_right[1])/(data_bottom_left[1]-data_top_right[1])*(self.window_size[1]-self.margin_size)) for dp in y_data_points]

		x_text_offset = 0.02777777777*self.window_size[0]
		for i,x_pix in enumerate(x_pixel_points):
			pygame.draw.rect(self.label_surface.pyg_surf, self.grid_color, pygame.Rect(x_pix, 0, 1, self.window_size[1]-self.margin_size*0.5))
			surf = self.grid_num_font.render(f"{x_data_points[i]:.2f}", antialias=True, color=self.grid_color)
			self.label_surface.pyg_surf.blit(surf, (x_pix-x_text_offset, self.window_size[1]-self.margin_size*0.9))

		for i,y_pix in enumerate(y_pixel_points):
			pygame.draw.rect(self.label_surface.pyg_surf, self.grid_color, pygame.Rect(0+self.margin_size*0.5, y_pix, self.window_size[0], 1))
			surf = self.grid_num_font.render(f"{y_data_points[i]:.2f}", antialias=True, color=self.grid_color)
			self.label_surface.pyg_surf.blit(surf, (0+self.margin_size*0.5, y_pix))
		
		#axis labels
		y_label_surf = self._y_label_surfs[""]
		x_label_surf = self._x_label_surfs[""]

		self.label_surface.pyg_surf.blit(y_label_surf, (0, (self.window_size[1]-self.margin_size)*0.5-y_label_surf.size[1]*0.5))
		self.label_surface.pyg_surf.blit(x_label_surf, (self.window_size[0]*0.5+self.margin_size-x_label_surf.size[0], self.window_size[1]-self.margin_size*0.5))


		return
		x_grid_points = numpy.linspace(data_bottom_left[0], data_top_right[0], 11)
		y_grid_points = numpy.linspace(data_bottom_left[1], data_top_right[1], 11)

		x_text_offset = 0.02777777777*self.window_size[0]
		for i,x in enumerate(numpy.linspace(self.margin_size, self.window_size[0], 11)):
			if i==0:
				continue
			pygame.draw.rect(self.label_surface.pyg_surf, self.grid_color, pygame.Rect(x, 0, 1, self.window_size[1]-self.margin_size*0.5))
			surf = self.grid_num_font.render(f"{x_grid_points[i]:.2f}", antialias=True, color=self.grid_color)
			self.label_surface.pyg_surf.blit(surf, (x-x_text_offset, self.window_size[1]-self.margin_size*0.9))

		for i,y in enumerate(numpy.linspace((self.window_size[1]-self.margin_size), 0, 11)):
			if i==0:
				continue
			pygame.draw.rect(self.label_surface.pyg_surf, self.grid_color, pygame.Rect(0+self.margin_size*0.5, y, self.window_size[0], 1))
			surf = self.grid_num_font.render(f"{y_grid_points[i]:.2f}", antialias=True, color=self.grid_color)
			self.label_surface.pyg_surf.blit(surf, (0+self.margin_size*0.5, y))

		#axis labels
		self.label_surface.pyg_surf.blit(self._y_label_surf, (0, (self.window_size[1]-self.margin_size)*0.5-self._y_label_surf.size[1]*0.5))
		self.label_surface.pyg_surf.blit(self._x_label_surf, (self.window_size[0]*0.5+self.margin_size-self._x_label_surf.size[0], self.window_size[1]-self.margin_size*0.5))

	def draw_colorbar(self):
		surf = mpl_colorbar.make_colorbar_surf(self.data_ingester.min, self.data_ingester.max, self.data_ingester.my_gettable_label)
		self.label_surface.pyg_surf.blit(surf, (self.window_size[0]-self.margin_size, (self.window_size[1]-self.margin_size)*0.5))
	
	def start_colorbar_draw_proc(self, delay=0):
		self.update_colorbar()
		with open(f"_{self.data_ingester.proc_id}_colorbar_settings.txt", "w") as cb_settings:
			pass
		self.cb_drawer = subprocess.Popen(f"{sys.executable} mpl_colorbar.py loop {delay} {self.data_ingester.proc_id}", shell=True, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=0)

	def update_colorbar(self):
		with open(f"_{self.data_ingester.proc_id}_colorbar_settings.txt", "w") as cb_settings:
			settings_dump = json.dumps({"min":float(self.data_ingester.min), "max":float(self.data_ingester.max), "label":self.data_ingester.my_gettable_label})
			cb_settings.write(f"{settings_dump}\n")
			cb_settings.flush()
		try:
			cb_surf = pygame.image.load(f"_{self.color_label}_colorbar.jpg")
			self.old_cb_surf = cb_surf

			side_scaler = self.extra_margin_size / cb_surf.size[0]
			cb_surf = pygame.transform.smoothscale(cb_surf, (int(cb_surf.size[0]*side_scaler), int(cb_surf.size[1]*side_scaler)))
			self.label_surface.pyg_surf.blit(cb_surf, (self.window_size[0]-self.extra_margin_size,           (self.window_size[1]-self.extra_margin_size)*0.5 - cb_surf.size[1]*0.5))
		except:
			if self.old_cb_surf != 0:
				side_scaler = self.extra_margin_size / self.old_cb_surf.size[0]
				self.old_cb_surf = pygame.transform.smoothscale(self.old_cb_surf, (int(self.old_cb_surf.size[0]*side_scaler), int(self.old_cb_surf.size[1]*side_scaler)))
				self.label_surface.pyg_surf.blit(self.old_cb_surf, (self.window_size[0]-self.extra_margin_size,           (self.window_size[1]-self.extra_margin_size)*0.5 - self.old_cb_surf.size[1]*0.5))





	def default_to_color(color_param_name):
		def inner1(*args):
			func = args[0]
			params = list(func.__code__.co_varnames)
			index = params.index(color_param_name)
			def inner2(*args, **kwargs):
				args = list(args)


				target = None
				in_kwargs = kwargs.get(color_param_name)
				if in_kwargs:
					target = in_kwargs
				elif len(args) > index:
					if args[index] == "default_color":
						del args[index]
					else:
						target = args[index]


				obj = args[0]

				if not target:
					kwargs[color_param_name] = obj.default_color
				elif target == "default_color":
					kwargs[color_param_name] = obj.default_color
				

				func(*args, **kwargs)
			return inner2
		return inner1        
	


	@default_to_color("color")
	def draw_axis_lines(self, surface : pygame.Surface,  bg_color : tuple[int, int, int, int], color : tuple[int, int, int] = "default_color"):
		"""it needs the bg color for the margin crop"""
		win_size_x, win_size_y = self.window_size


		#x_axis margin crop
		pygame.draw.rect(surface, bg_color, (0, win_size_y-self.margin_size, win_size_x, self.margin_size))
		#y_axis margin crop
		pygame.draw.rect(surface, bg_color, (0, 0, self.margin_size, win_size_y))



		#x_axis line
		pygame.draw.rect(surface, color, (0, win_size_y-self.margin_size, win_size_x, 2))
		#y_axis line
		pygame.draw.rect(surface, color, (self.margin_size, 0, 2, win_size_y))


