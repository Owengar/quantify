import pygame, time, numpy, moderngl, threading, sys
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

class labeling():
	
	def __init__(self, display_manager : display_manager_.display_manager, label_surface : surface_.surface, viewport : viewport_.viewport, data_ingester : data_ingester_.data_ingester, default_color : tuple[int, int, int] = (0, 0, 0, 255)):
		self.display_manager = display_manager
		self.label_surface = label_surface
		self.viewport = viewport
		self.data_ingester = data_ingester
		self.x_label = data_ingester.my_label
		self.y_label = data_ingester.my_gettable_label
		self.viewport.uniform_get_map["margin_percentages"] = self.get_margin_percentages
		self.default_color = default_color
		self.margin_size = self.display_manager.get_shortest()*0.1
		self.extra_margin_size = self.display_manager.get_shortest()*0.15
		self.window_size = self.display_manager.get_window_size()
		self.grid_color = (10, 10, 10)
		self.hover_bg_color = (220, 220, 220, 255)
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
		win_size_x, win_size_y = self.display_manager.get_window_size()
		self._margin_percentages = (self.extra_margin_size / win_size_x, self.extra_margin_size / win_size_y)

	def get_margin_percentages(self) -> tuple[float, float]:
		return self._margin_percentages 

	def draw_transfer_symbol(self):
		self.label_surface.blit(self.transfer_symbol, ((0.5*self.margin_size)-(0.5*self.transfer_symbol.size[0]), self.display_manager.get_window_size()[1]-(self.margin_size)+(0.5*self.margin_size)-(0.5*self.transfer_symbol.size[1])))

	def pixel_pos_to_data_pos(self, pixel_pos : tuple[int, int]):
		data_viewport = self.viewport.get_data_viewport()
		data_viewport_start = self.viewport.get_data_viewport_start() 
		camera_viewport = self.viewport.get_camera_viewport()
		camera_viewport_start = self.viewport.get_camera_viewport_start()

		#bottom left pixel_pos = (self.labeling.margin_size, (self.window_size[1]-self.labeling.margin_size))
		#top right pixel_pos = (window_size[0]-labeling.margin_size, labeling.margin_size) orrrrrrrr.......... (window_size[0], 0)

		margin = self.get_margin_percentages()[0] * data_viewport[0]
		twox_margin = self.get_margin_percentages()[0] * data_viewport[0] * 2
		data_pos_x = ((((pixel_pos[0]/self.window_size[0])/(1/camera_viewport[0]) + camera_viewport_start[0] - 0) / 1) * (data_viewport[0] + twox_margin)) - margin + data_viewport_start[0]
		
		margin = self.get_margin_percentages()[1] * data_viewport[1]
		twox_margin = self.get_margin_percentages()[1] * data_viewport[1] * 2
		data_pos_y = ((((pixel_pos[1]/self.window_size[1])/(1/camera_viewport[1]) + camera_viewport_start[1] - 1) / -1) * (data_viewport[1] + twox_margin)) - margin + data_viewport_start[1]
		
		return (data_pos_x, data_pos_y)

	def draw_hovering(self, ssbo : moderngl.Buffer, mouse_pos):
		self.display_manager.ctx.copy_buffer(self.new, ssbo, 4*2*2, (4000000-2)*4*2)
		ret_bytes = self.new.read()
		ret_dpoint = numpy.frombuffer(ret_bytes, dtype=numpy.float32)

		if numpy.isnan(ret_dpoint[3]):
			return
		ssbo.write(numpy.array([numpy.nan, numpy.nan]).astype(numpy.float32).tobytes(), (4000000-1)*4*2)
		hover_point_text = self.grid_label_font.render(f"[X: {ret_dpoint.tolist()[2:][0]}, Y: {ret_dpoint.tolist()[2:][1]}]", True, (0, 0, 0, 255), bgcolor=self.hover_bg_color)
		mouse_pos = (mouse_pos[0], mouse_pos[1]-hover_point_text.size[1])
		pygame.draw.circle(self.label_surface.pyg_surf, (255, 255, 0, 100), (int(ret_dpoint[0]), int(ret_dpoint[1])), 10)
		self.label_surface.pyg_surf.blit(hover_point_text, mouse_pos)


	def make_grid_list(self):
		data_bottom_left = self.pixel_pos_to_data_pos((self.margin_size, (self.window_size[1]-self.margin_size)))
		data_top_right = self.pixel_pos_to_data_pos((self.window_size[0], 0))

		x_unit_scaled = new_unit_scale.convert_unit_scale(data_bottom_left[0], data_top_right[0])
		x_scale_factor = x_unit_scaled[3]
		y_unit_scaled = new_unit_scale.convert_unit_scale(data_bottom_left[1], data_top_right[1], debug=False)
		y_scale_factor = y_unit_scaled[3]


		x_data_points = get_axis_nums(x_unit_scaled[0], x_unit_scaled[1])
		x_pixel_points = [float((dp-data_bottom_left[0]*x_scale_factor)/(data_top_right[0]*x_scale_factor-data_bottom_left[0]*x_scale_factor)*(self.window_size[0]-self.margin_size)+self.margin_size) for dp in x_data_points]

		y_data_points = get_axis_nums(y_unit_scaled[0], y_unit_scaled[1])
		y_pixel_points = [float((dp-data_top_right[1]*y_scale_factor)/(data_bottom_left[1]*y_scale_factor-data_top_right[1]*y_scale_factor)*(self.window_size[1]-self.margin_size)) for dp in y_data_points]

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
		y_label_surf = self._y_label_surfs[y_unit_scaled[2]]
		x_label_surf = self._x_label_surfs[x_unit_scaled[2]]


		self.label_surface.pyg_surf.blit(y_label_surf, (0, (self.window_size[1]-self.margin_size)*0.5-y_label_surf.size[1]*0.5))
		self.label_surface.pyg_surf.blit(x_label_surf, (self.window_size[0]*0.5+self.margin_size-x_label_surf.size[0], self.window_size[1]-self.margin_size*0.5))
		

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
		win_size_x, win_size_y = self.display_manager.get_window_size()


		#x_axis margin crop
		pygame.draw.rect(surface, bg_color, (0, win_size_y-self.margin_size, win_size_x, self.margin_size))
		#y_axis margin crop
		pygame.draw.rect(surface, bg_color, (0, 0, self.margin_size, win_size_y))



		#x_axis line
		pygame.draw.rect(surface, color, (0, win_size_y-self.margin_size, win_size_x, 2))
		#y_axis line
		pygame.draw.rect(surface, color, (self.margin_size, 0, 2, win_size_y))


