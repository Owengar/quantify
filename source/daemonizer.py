import subprocess
import time

independent_process = subprocess.Popen(
    'python C:\\Users\\WorkshopAFM2\\Documents\\vscode_python\\quantify_setup\\daemonize_me.py',
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
)
time.sleep(5)
independent_process.kill()