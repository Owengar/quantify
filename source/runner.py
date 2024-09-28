try:
    from source.imports import *
    import source._process_exchange as _process_exchange
except:
    raise RuntimeError("\n\nThe \"runner\" file and its function: \"run\" must only be called from the \"measurement_runner\" script ouside of the \"source\" folder.\n\n")




def run(measurement_script_name : str):
    if not measurement_script_name.endswith(".py"):
        measurement_script_name += ".py"


    _process_exchange._make_signal_file("ran_from_meas_runner")
    measurement_daemon_process = subprocess.Popen("pythonw " + os.path.abspath(measurement_script_name), creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _process_exchange._make_signal_file("stdout.txt")
    stdout = open(_process_exchange._find_signal_path("stdout.txt"), "r")
    readline = stdout.readline()
    while True:
        if len(readline):
            print(readline)
            if "closing..." in readline:
                stdout.close()
                _process_exchange._del_exchange_dir()
                break
            if "Traceback" in readline:
                for line in stdout.readlines():
                    print(line)
                stdout.close()
                measurement_daemon_process.kill()
                for i in range(10):
                    try:
                        _process_exchange._del_exchange_dir()
                        break
                    except:
                        time.sleep(0.5)
                break
        readline = stdout.readline()