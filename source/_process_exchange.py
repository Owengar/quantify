import os, shutil, subprocess

_proc_exchange_folder_name = "temporary_proc_exchange_folder"
_exchange_txt_name = "temporary_proc_exchange.txt"
_done_reading_signal = "done_reading"

_source_path = ""
_proc_exchange_dir = ""


def _get_source_path():
    global _source_path
    if not _source_path:
        _source_path = os.path.dirname(os.path.abspath(__file__))
    return _source_path
def _get_proc_exchange_dir():
    global _proc_exchange_dir
    source_path = _get_source_path()
    if not _proc_exchange_dir:
        _proc_exchange_dir = f"{source_path}\\{_proc_exchange_folder_name}"
        _make_proc_exchange_dir()
    return _proc_exchange_dir

def _make_signal_file(signal_name : str):
    if not signal_name.endswith(".txt"):
        signal_name += ".txt"
    proc_exchange_dir = _get_proc_exchange_dir()
    with open(proc_exchange_dir + "\\" + signal_name, "w") as singal_file:
        pass
    
def _wait_for_signal(signal_name : str, break_condition = None):
    if not signal_name.endswith(".txt"):
        signal_name += ".txt"
    proc_exchange_dir = _get_proc_exchange_dir()
    if callable(break_condition):
        while not signal_name in os.listdir(proc_exchange_dir):
            if break_condition():
                return False
    else:
        while not signal_name in os.listdir(proc_exchange_dir):
            pass
    os.remove(proc_exchange_dir + "\\" + signal_name)
    return True


def _make_proc_exchange_dir():
    proc_exchange_dir = _get_proc_exchange_dir()

    if os.path.exists(proc_exchange_dir):
        return
    else:
        os.mkdir(proc_exchange_dir)

def _del_exchange_dir():
    proc_excahnge_dir = _get_proc_exchange_dir()
    shutil.rmtree(proc_excahnge_dir)
























def _find_exchange_file(proc_exchange_folder_name, proc_exchange_txt_name, source_path : str):
    proc_exchange_dir = f"{source_path}\\{_proc_exchange_folder_name}"
    exchange_txt_path = proc_exchange_dir + f"\\{_exchange_txt_name}"
    return (proc_exchange_dir, exchange_txt_path)





def _make_proc_exchange_holder(source_path : str = "", signal_files : list[str] = []):
    if not source_path:
        source_path = os.path.dirname(os.path.abspath(__file__))


    proc_exchange_dir, proc_exchanger_path = _find_exchange_file(_proc_exchange_folder_name, _exchange_txt_name, source_path)

    if os.path.exists(proc_exchange_dir):
        shutil.rmtree(proc_exchange_dir)
    os.mkdir(proc_exchange_dir)
    with open(proc_exchanger_path, "w") as proc_exchanger:
        proc_exchanger.write(str(os.getpid()) + "\n")
        proc_exchanger.write(proc_exchange_dir + "\n")
    for signal_name in signal_files:
        with open(proc_exchange_dir + "\\" + signal_name):
            pass

    return proc_exchange_dir

def _wait_for_dir_close_signal(proc_exchange_dir):
    while not _done_reading_signal in os.listdir(proc_exchange_dir):
        pass
    shutil.rmtree(proc_exchange_dir)

""" def _spawn_daemon():
    source_path = os.path.dirname(os.path.abspath(__file__))
    stop_detector_daemon_path = source_path + "\\stop_detector_daemon.py"
    proc_exhange_dir = _make_proc_exchange_holder(source_path=source_path)



    stop_detector_daemon_process = subprocess.Popen("python " + stop_detector_daemon_path, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)

    _wait_for_dir_close_signal(proc_exhange_dir)
    
    print("past")
 """