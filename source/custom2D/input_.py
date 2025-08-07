import pygame, moderngl, sys, json, numpy, math

class input():
    def nothing():
        pass
    def __init__(self, care_keys_path : str):

        self.care_keys = self.care_keys_from_json(care_keys_path)
        self.init_key_dicts(self.care_keys)
        self.mwheel_scroll = 0.0




    def care_keys_from_json(self, care_keys_path : str):
        care_keys_dict = json.load(open(care_keys_path, "r"))
        return care_keys_dict["keys"]
    

    def init_key_dicts(self, care_keys : list[int]):
        self.keys : dict = dict.fromkeys(care_keys, False)
        self.keys_down : dict = self.keys.copy()
        self.keys_up : dict = self.keys.copy()

        self.init_clear_dicts(self.keys)

    def init_clear_dicts(self, keys : dict):
        self.keys_clear = keys.copy()

        def clear_ups_downs():
            self.keys_down.update(self.keys_clear)
            self.keys_up.update(self.keys_clear)
        self.clear_ups_downs = clear_ups_downs


    def clear_ups_downs():
        pass



    def input_loop(self, running):


        self.mwheel_scroll *= 0.7
        self.mwheel_scroll = math.trunc(self.mwheel_scroll*100)
        self.mwheel_scroll *= 0.01



        self.clear_ups_downs()
        self.mouse_vel = pygame.mouse.get_rel()
        self.mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running[0] = False


            elif event.type == pygame.KEYDOWN:
                if event.key in self.keys:
                    self.keys[event.key] = True
                    self.keys_down[event.key] = True

            elif event.type == pygame.KEYUP:
                if event.key in self.keys:
                    self.keys[event.key] = False
                    self.keys_up[event.key] = True
            
            elif event.type == pygame.MOUSEWHEEL:
                self.mwheel_scroll += -event.precise_y
        
        return __class__.nothing
                
