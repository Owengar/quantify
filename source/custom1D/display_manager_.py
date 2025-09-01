import pygame, moderngl, struct, ctypes, time


class display_manager():

    def __init__(self, window_size : tuple | str, caption : str, clear_color : tuple[int, int, int, int], scaled_up=True):
        if not scaled_up:
            print("real scale")
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


    
    def render(self, program, texture_location_pairs : list[tuple[moderngl.Texture, int]]):
        for texture_location_pair in texture_location_pairs:
            texture_location_pair[0].use(texture_location_pair[1])
        program.assign_uniforms(program)
        self.ctx.clear(self.clear_color[0]/255, self.clear_color[1]/255, self.clear_color[2]/255, self.clear_color[3]/255)
        program.vao.render()


    def run_compute(self, compute : moderngl.ComputeShader, work_groups : tuple[int, int, int]):
        compute.assign_uniforms(compute)
        #self.ctx.clear(14/255,40/255,66/255)
        compute.run(work_groups[0], work_groups[1], work_groups[2])