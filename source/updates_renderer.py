import pathlib
import git
import pygame



if __name__ == "__main__":
    source_dir = str(pathlib.Path().resolve())
    open_dir = source_dir.removesuffix("\\source")
    localcopy = git.Repo(open_dir)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    pygame.font.init()
    pat_font = pygame.font.SysFont("Arial", int(500 * 0.02))

    updates_surf = pat_font.render(updates, antialias=True, color=(0, 0, 0), wraplength=490)