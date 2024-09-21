try:
    from source.imports import *
    import source._process_exchange as _process_exchange
except:
    raise RuntimeError("\n\nThe \"runner\" file and its function: \"run\" must only be called from the \"measurement_runner\" script ouside of the \"source\" folder.\n\n")




def run(measurement_script_name : str):
    if not measurement_script_name.endswith(".py"):
        measurement_script_name += ".py"


    _process_exchange._make_signal_file("ran_from_meas_runner")
    measurement_daemon_process = subprocess.Popen("pythonw " + os.path.abspath(measurement_script_name), creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, shell=True, stdout=subprocess.PIPE)