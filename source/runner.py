import sys
sys.dont_write_bytecode = True

try:
    from source.imports import *
    import source._process_exchange as _process_exchange
except:
    raise RuntimeError("\n\nThe \"runner\" file and its function: \"run\" must only be called from the \"measurement_runner\" script ouside of the \"source\" folder. This is to prevent accidentally stopping a measurement.\n\n")




def nested_to_list(ndlist):
    if isinstance(ndlist, numpy.ndarray) or isinstance(ndlist, list):
        ndlist = list(ndlist)
        for i,item in enumerate(ndlist):
            ndlist[i] = nested_to_list(item)
        return ndlist
    else:
        return ndlist


def run(measurement_script_name : str, setpoints_grid : list[list[int | float]]):
    """
        Command to run a measurement script with given setpoints.

        Parameters
        -

        - .. measurement_script_name:: The name of the measurement script python file. ***(Suffixing with ".py" does not matter.)***
        - .. setpoints_grid:: A list of lists of setpoints for each settable parameter. ****\\*IMPORTANT\\***** : ***The order in which the lists of setpoints are placed determines which parameter they are assigned to. It should correspond with the same order as the settable parameters in your measurement script file.***
    """
    if not measurement_script_name.endswith(".py"):
        measurement_script_name += ".py"


    setpoints_grid = nested_to_list(setpoints_grid)

    _process_exchange._make_signal_file("ran_from_meas_runner")
    with open(_process_exchange._find_signal_path("ran_from_meas_runner"), "w") as ran_from_meas_runner:
        ran_from_meas_runner.write(str(os.getpid()) + "\n")
        ran_from_meas_runner.write(json.dumps(list(setpoints_grid)) + "\n")
    print("\nInitiating measurement process...")
    measurement_daemon_process = subprocess.Popen("python " + os.path.abspath(measurement_script_name), creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)
    print("To cancel measurement, close the terminal or type CTRL + C.\n")


    _process_exchange._make_signal_file("stdout.txt")
    stdout = open(_process_exchange._find_signal_path("stdout.txt"), "r")
    readline = stdout.readline()
    measurement_daemon_process.poll()
    while not measurement_daemon_process.poll():
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
        time.sleep(1)
    try:
        for line in stdout.readlines():
            print(line)
    except:
        pass

    print(f"\nEnd of script: {measurement_script_name}\n")