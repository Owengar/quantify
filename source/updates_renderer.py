import pathlib
import git
import pygame
import os
import win32com




if __name__ == "__main__":

    source_dir = ""
    for file in os.listdir():
        if file.endswith(".lnk"):
            try:
                link_path = os.path.abspath(file)
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(link_path)
                sc_target = shortcut.Targetpath
                if sc_target.endswith("open_quantify.exe"):
                    source_dir = sc_target.removesuffix("\\open_quantify.exe")
                    break
            except:
                pass

    if not source_dir:
        source_dir = str(pathlib.Path().resolve())
    open_dir = source_dir.removesuffix("\\source")

    localcopy = git.Repo(open_dir)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    pygame.font.init()
    pat_font = pygame.font.SysFont("Arial", int(500 * 0.02))

    updates_surf = pat_font.render(updates, antialias=True, color=(0, 0, 0), wraplength=490)