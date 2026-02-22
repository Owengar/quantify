import pygame, moderngl, struct, ctypes, numpy



def swap_channels_numpy(surface, channel_map):
    """
    Swaps color channels using numpy.
    channel_map should be a list of indices, e.g., [1, 0, 2, 3] swaps R and G in RGBA.
    """
    # Convert Pygame surface to a NumPy array (RGBA format)
    # The 'RGBA' format is often the default/easiest to work with
    img_array = pygame.surfarray.array3d(surface)
    
    # If the surface has alpha, you might need array4d or convert it first
    # For a general RGBA surface:
    if surface.get_flags() & pygame.SRCALPHA:
        img_array = pygame.surfarray.array3d(surface.convert_alpha()) # get RGB part
        alpha_array = pygame.surfarray.pixels_alpha(surface) # get A part
        # Combine into an RGBA array if needed
        full_array = numpy.concatenate((img_array, alpha_array[:, :, numpy.newaxis]), axis=2)
    else:
        full_array = img_array

    # Perform the channel swap using NumPy indexing
    # Example for swapping R and G: channel_map = [1, 0, 2, 3] for RGBA
    swapped_array = full_array[:, :, channel_map]
    
    # Convert the NumPy array back to a Pygame Surface
    # This requires specific handling depending on your Pygame version and array format
    # A simple way for RGB/RGBA array:
    new_surface = pygame.surfarray.make_surface(swapped_array[:, :, :3])
    if len(channel_map) == 4: # If alpha was handled, set it
         new_surface.set_alpha(255) # Or use the alpha data appropriately

    return new_surface


class display_manager():

	def __init__(self, window_size : tuple, caption : str, clear_color : tuple[int, int, int, int], scaled_up=True):
		if not scaled_up:
			#print("real scale")
			ctypes.windll.user32.SetProcessDPIAware()
		
		self.set_caption(caption)
		if window_size != "auto":
			self.set_window_size(window_size)
		else:
			display_size = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
			size = (int(display_size[0]*0.7), int(display_size[1]*0.7))
			self.set_window_size(size)
		pygame.init()
		self.display_surface = pygame.display.set_mode(self.get_window_size(), pygame.OPENGL | pygame.GL_DOUBLEBUFFER |pygame.DOUBLEBUF)

		self.ctx = moderngl.create_context()
		self.frame_buffer = self.ctx.detect_framebuffer()
		self.clear_color = clear_color
	


	def set_caption(self, caption : str):
		pygame.display.set_caption(caption)

	def get_window_size(self) -> tuple:
		return self._window_size
	
	def set_window_size(self, set_to : tuple):
		self._window_size : tuple = set_to
	
	def get_shortest(self):
		size = self.get_window_size()
		if size[0] > size[1]:
			return size[1]
		else:
			return size[0]

	def setup_render_program(self, prog):
		texture_coordinates = [0, 1,  1, 1,                0, 0,  1, 0]  
		world_coordinates = [-1, -1,  1, -1,              -1,  1,  1,  1]  
		render_indices = [0, 1, 2,           1, 2, 3] 


		vbo = self.ctx.buffer(struct.pack('8f', *world_coordinates))
		uvmap = self.ctx.buffer(struct.pack('8f', *texture_coordinates))
		ibo = self.ctx.buffer(struct.pack('6I', *render_indices))
		vao_content = [     (vbo, '2f', 'vert'),     (uvmap, '2f', 'in_text') ]
		vao = self.ctx.vertex_array(prog, vao_content, ibo)
		return vao


	
	def render(self, program, texture_location_pairs : list[tuple[moderngl.Texture, int]], clear_ctx = False):
		for texture_location_pair in texture_location_pairs:
			texture_location_pair[0].use(texture_location_pair[1])
		program.assign_uniforms(program)
		if clear_ctx:
			self.ctx.clear(self.clear_color[0]/255, self.clear_color[1]/255, self.clear_color[2]/255, self.clear_color[3]/255)
		program.vao.render()


	def run_compute(self, compute : moderngl.ComputeShader, work_groups : tuple[int, int, int]):
		compute.assign_uniforms(compute)
		self.ctx.clear(14/255,40/255,66/255)
		compute.run(work_groups[0], work_groups[1], work_groups[2])

	def ctx_clear(self):
		self.ctx.clear(self.clear_color[0]/255, self.clear_color[1]/255, self.clear_color[2]/255, self.clear_color[3]/255)

	def screenshot(self, save_path, format=".jpg"):
		screenshot_surf = pygame.Surface(self._window_size).convert_alpha()
		screenshot_surf.get_buffer().write(self.frame_buffer.read(components=4))
		screenshot_surf = pygame.transform.flip(screenshot_surf, False, True)
		screenshot_surf = swap_channels_numpy(screenshot_surf, [2, 1, 0, 3])
		pygame.image.save(screenshot_surf, save_path+format)