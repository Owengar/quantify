import pygame, moderngl, json
import viewport_


class program_manager():
    def __init__(self, programs_json_path : str, display_manager):
        self.programs_json_path = programs_json_path
        self.programs_dir = programs_json_path.rsplit("\\", 1)[0]
        self.display_manager = display_manager
        self.programs = {}
        self.parse_programs_json(self.programs_json_path)



    def parse_programs_json(self, json_path):
        programs_json = json.load(open(json_path, "r"))
        for program in programs_json["programs"]:
            if program["type"] == "program":
                self.programs[program["name"]] = self.load_program(program)
            elif program["type"] == "compute":
                self.programs[program["name"]] = self.load_compute(program)


    def load_program(self, json_program):
        program = self.display_manager.ctx.program(vertex_shader=open(self.programs_dir + "\\" + json_program["vertex"], "r").read(), fragment_shader=open(self.programs_dir + "\\" + json_program["fragment"], "r").read())
        program.needed_uniforms = json_program["uniforms"]
        program.vao = self.display_manager.setup_render_program(program)
        return program


    def load_compute(self, json_compute):
        compute = self.display_manager.ctx.compute_shader(open(self.programs_dir + "\\" + json_compute["compute"], "r").read())
        compute.needed_uniforms = json_compute["uniforms"]
        return compute

