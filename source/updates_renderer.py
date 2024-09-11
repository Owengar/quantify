import pathlib
import git
import pygame
import subprocess
import sys, os



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def render():
    for line in sys.stdin:
        open_dir = line
        break
    localcopy = git.Repo(open_dir)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    pygame.font.init()
    pat_font = pygame.font.SysFont("Arial", int(500 * 0.02))
    subupdates_surf = pat_font.render("hi", antialias=True, color=(0, 0, 0), wraplength=490)

if __name__ == "__main__":
    render()

def txt_process(open_dir):
    process = subprocess.Popen(f"python {resource_path("updates_renderer.py")}", text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(open_dir)
    process.stdin.close()
    
    return process

