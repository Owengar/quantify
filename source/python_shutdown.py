import subprocess, sys, os, time


my_pid = str(os.getpid())
tasklist = subprocess.run("tasklist", stdout=subprocess.PIPE)

procs = tasklist.stdout.splitlines()

for proc in procs:
    proc = proc.decode()
    if "python.exe" in proc and (not "pythonw" in proc):
        proc = proc.split(" ")
        pid = ""
        for word in proc:
            if word.isdigit():
                pid = word
                break
        if pid != my_pid:
            print(proc)
            print(pid)
            os.system(f"taskkill /PID {pid} /F")