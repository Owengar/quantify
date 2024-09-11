import pathlib
import git
import pygame
import subprocess
import sys


def render():
    #localcopy = git.Repo(open_dir)
    #updates = localcopy.git.diff("main", "latest", "--", "source")
    for line in sys.stdin:
        open_dir = line
    localcopy = git.Repo(open_dir)
    updates = localcopy.git.diff("main", "latest", "--", "source")
    pygame.font.init()
    pat_font = pygame.font.SysFont("Arial", int(500 * 0.02))
    subupdates_surf = pat_font.render("hi", antialias=True, color=(0, 0, 0), wraplength=490)

if __name__ == "__main__":
    render()

def txt_process(open_dir):
    process = subprocess.Popen(f"python {__file__}", text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(open_dir)
    process.stdin.close()
    
    return process



import errno
import select
from threading import Thread

def non_blocking_communicate(proc, inputs):
    """non blocking version of subprocess.Popen.communicate.
    `inputs` should be a sequence of bytes (e.g. file-like object, generator,
    io.BytesIO, etc.).
    """

    def write_proc(proc, inputs):
        for line in inputs:
            try:
                proc.stdin.write(line)
            except IOError as e:
                # break at "Broken pipe" error, or "Invalid argument" error.
                if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                    break
                else:
                    raise
        proc.stdin.close()

    t = Thread(target=write_proc, args=(proc, inputs))
    t.start()

    while proc.poll() is None:
        if select.select([proc.stdout], [], [])[0]:
            line = proc.stdout.readline()
            if not line:
                break
            yield line

    proc.wait()
    t.join()