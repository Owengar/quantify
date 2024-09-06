import datetime, time
import os
import psutil
import ctypes
from quantify_core.measurement.control import MeasurementControl


from quantify_grapher import _find_proc_exhanger, _proc_exchange_folder_name, _proc_exchange_txt_name, _done_reading_signal

def _read_exchanger():
    proc_exchanger_path = _find_proc_exhanger(_proc_exchange_folder_name, _proc_exchange_txt_name)[1]
    with open(proc_exchanger_path) as proc_exchanger:
        main_pid = int(proc_exchanger.readline())
        proc_exchange_dir = proc_exchanger.readline().removesuffix("\n")
        meas_ctrl_id = int(proc_exchanger.readline().removesuffix("\n"))
    

    with open(proc_exchange_dir + f"\\{_done_reading_signal}", "w"):
        pass
    return main_pid, meas_ctrl_id


main_pid, meas_ctrl_id = _read_exchanger()

with open("C:\\Users\\WorkshopAFM2\\quantify-data\\thready.txt", "w") as txt:
    """ for i in range(100):
        time.sleep(0.1)
        i += 1
        txt.write(f"{psutil.pid_exists(main_pid)}   ---   {datetime.datetime.now()}\n") """
    while psutil.pid_exists(main_pid):
        time.sleep(0.1)