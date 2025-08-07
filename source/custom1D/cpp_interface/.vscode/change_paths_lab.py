import io, json
from collections.abc import Iterable



#TODO PUT THIS AS AN ENDING PARAMETER IN TASKS: "-static-libstdc++"

tasks = ".vscode\\tasks.json"
properties = ".vscode\\c_cpp_properties.json"
build_args = ".vscode\\build_args.json"


my_gpp_path = "C:\\msys64\\ucrt64\\bin\\g++.exe"
gpp_identifiers = ["bin\\g++.exe", "bin/g++.exe"]

my_glfw_include_path = "C:\\Users\\WorkshopAFM2\\glfw-3.4.bin.WIN64\\include"
glfw_include_identifiers = ["glfw-3.4.bin.WIN64/include", "glfw-3.4.bin.WIN64\\include"]

my_glfw_lib_path = "C:\\Users\\WorkshopAFM2\\glfw-3.4.bin.WIN64\\lib-mingw-w64"
glfw_lib_identifiers = ["glfw-3.4.bin.WIN64/lib-mingw-w64", "glfw-3.4.bin.WIN64\\lib-mingw-w64"]

my_glm_include_path = "C:\\Users\\WorkshopAFM2\\glm-1.0.1-light"
glm_include_identifiers = ["/glm-1.0.1-light", "\\glm-1.0.1-light"]

my_json_include_path = "C:\\Users\\WorkshopAFM2\\json-develop\\single_include\\nlohmann"
json_include_identifiers = ["single_include\\nlohmann", "single_include/nlohmann"]


"""
def find_identifier_path_start_end(read_file : str, identifiers : list[str]):
    for identifier in identifiers:
        latest_index = 0
        while True:
            id_index = read_file.find(identifier, latest_index)
            if id_index == -1:
                break
            latest_index = id_index+1
            while read_file[id_index] != "\"":
                id_index -= 1
            start = id_index
            id_index +=1
            while read_file[id_index] != "\"":
                id_index += 1
            yield (start, id_index)



def delete_range(opened_file : io.TextIOWrapper):
    opened_file.truncate()

def rename_specific_path(opened_file : io.TextIOWrapper, identifiers : list[str], my_replacement):
    read_file = opened_file.read()
    for start, end in find_identifier_path_start_end(read_file, identifiers):
        
        print((start, end))
        delete_range(opened_file)
"""





class parent_obj():
    def __init__(self, parent, child, child_dict_index = None):
        if isinstance(parent, list):
            self.parent_list = parent
            self.child_index = parent.index(child)
            self.set_to = self._set_child_list
        elif isinstance(parent, dict):
            self.parent_dict = parent
            self.child_dict_index = child_dict_index
            self.set_to = self._set_child_dict
            

    def _set_child_list(self, set_to):
        self.parent_list[self.child_index] = set_to
    def _set_child_dict(self, set_to):
        self.parent_dict[self.child_dict_index] = set_to

        
        

def rename_specific_path(obj, identifiers : list[str], my_path : str, parent_ob : parent_obj = None):
    if isinstance(obj, dict):
        for dict_item in obj:
            rename_specific_path(obj[dict_item], identifiers, my_path, parent_obj(obj, obj[dict_item], dict_item))
    elif isinstance(obj, list):
        for item in obj:
            rename_specific_path(item, identifiers, my_path, parent_obj(obj, item))
    elif isinstance(obj, str):
        for identifier in identifiers:
            if identifier in obj:
                parent_ob.set_to(my_path)



def rename_all_paths(loaded_dict, file_name):
    rename_specific_path(loaded_dict, gpp_identifiers, my_gpp_path)
    rename_specific_path(loaded_dict, glfw_include_identifiers, my_glfw_include_path)
    rename_specific_path(loaded_dict, glfw_lib_identifiers, my_glfw_lib_path)
    rename_specific_path(loaded_dict, glm_include_identifiers, my_glm_include_path)
    rename_specific_path(loaded_dict, json_include_identifiers, my_json_include_path)
    

    with open(file_name, "w") as opened_file:
        json.dump(loaded_dict, opened_file, indent=1)

if __name__ == "__main__":
    loaded_properties = json.load(open(properties, "r+"))
    loaded_tasks = json.load(open(tasks, "r+"))
    loaded_args = json.load(open(build_args, "r+"))
    rename_all_paths(loaded_properties, properties)
    rename_all_paths(loaded_tasks, tasks)
    rename_all_paths(loaded_args, build_args)