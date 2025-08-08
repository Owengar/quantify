import sys
sys.dont_write_bytecode = True

import sys, os
import psutil
import subprocess
import shutil



parent_pid = int(sys.argv[1])
source_path = sys.argv[2]

while psutil.pid_exists(parent_pid):
    1+1


source_dir_list = subprocess.run(f"cd {source_path} & dir", creationflags=subprocess.CREATE_NO_WINDOW, shell=True, stdout=subprocess.PIPE, text=True)
for file in source_dir_list.stdout.splitlines():
    if "open_quantify.exe" in file:
        os.remove(source_path + "\\open_quantify.exe")
shutil.copyfile(source_path + "\\new_opener\\new_open_quantify.exe", source_path + "\\open_quantify.exe")
subprocess.run(source_path + "\\open_quantify.exe", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)