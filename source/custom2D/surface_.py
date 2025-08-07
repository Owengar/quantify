import PIL.Image
import PIL.ImageMode
import pygame, moderngl, PIL


class surface():
    def __init__(self, size : tuple, display_manager, texture_dtype = "f1", flags=0):
        self.flags = flags
        self.pyg_surf = pygame.Surface(size, flags).convert_alpha()
        self.display_manager = display_manager
        self.init_texture(size, texture_dtype=texture_dtype)
        self.set_size(size)
    def __getattr__(self, name):
        return self.pyg_surf.__getattribute__(name)


    def get_size(self) -> tuple:
        return self._size
    
    def set_size(self, set_to : tuple):
        self._size : tuple = set_to
        self.pyg_surf = pygame.Surface(set_to, self.flags).convert_alpha()

    def init_texture(self, size : tuple, texture_dtype = "f1"):
        self.texture : moderngl.Texture = self.display_manager.ctx.texture(size, 4, self.get_buffer(), dtype=texture_dtype)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    
    def bind_to_image(self, unit):
        self.texture.bind_to_image(unit, True, True)
    
    def read_from_texture(self):
        #surf = pygame.image.frombytes(self.texture, self.texture.size, "RGBA")
        #self.texture.read_into(self.get_buffer())
        #with open("help.txt", "a") as help:
        #    help.write(f"{self.get_buffer()}\n")
        self.get_buffer().write(self.texture.read())
        
    def file_save(self, name):
        PIL.Image.frombytes("RGBA", (self.texture.width, self.texture.height), self.texture.read()).save(name)
    def write_to_texture(self):
        self.texture.write(self.get_buffer())

    def write_and_return(self):
        self.write_to_texture()
        return self.texture
    
    def clear_surface_and_texture(self, color : tuple[int, int, int, int]):
        self.fill(color)
        self.write_to_texture()


