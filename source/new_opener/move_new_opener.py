import sys, os
import psutil
import subprocess
import shutil



readlines = [sys.stdin.readline()]
while len(readlines) < 2:
    readlines.append(sys.stdin.readline())


parent_pid = int(readlines[0].removesuffix("\n"))
source_path = readlines[1].removesuffix("\n")

while psutil.pid_exists(parent_pid):
    1+1


source_dir_list = subprocess.run(f"cd {source_path} & dir", creationflags=subprocess.CREATE_NO_WINDOW, shell=True, stdout=subprocess.PIPE, text=True)
for file in source_dir_list.stdout.splitlines():
    if "open_quantify.exe" in file:
        os.remove(source_path + "\\open_quantify.exe")
shutil.copyfile(source_path + "\\new_opener\\new_open_quantify.exe", source_path + "\\open_quantify.exe")
subprocess.run(source_path + "\\open_quantify.exe", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)