from pathlib import Path
import sys, os

current_file_path = Path(__file__).resolve()
cfg_path = current_file_path.parent.joinpath("pyvenv.cfg")



def find_home_from_full_split(full_split : str) -> tuple[int, Path]:
    for i,word in enumerate(full_split):
        if word.startswith("home = "):
            return (i, Path(full_split[i+2].__str__()))
    print("Failed to find home in pyvenv config")
    raise Exception("Failed to find home in pyvenv config")

def find_user(path : Path):
    prev_path = path
    while path.name != "Users":
        prev_path = path
        path = path.parent
    return prev_path.name

def combine_full(split_full : list[bytes]):
    combine = ""
    for word in split_full:
        combine+=word + "\n"
    return combine

with open(cfg_path, "r+b") as cfg:
    #cfg.seek(16)
    #print(cfg.read(16))
    split_full = cfg.read().decode("utf-8").splitlines()
    index, current_home = find_home_from_full_split(split_full)
    split_full[index] = "home = " + sys.argv[1]
    combined = combine_full(split_full)
    #split_full.join()
    cfg_path.write_text(combined)

    #user = find_user(Path(current_home))
    #replaced_home = current_home.__str__().replace(f"\\{user}\\", "\\hi\\")
    #print(replaced_home)
    