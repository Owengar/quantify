from pywinauto import Desktop
import sys, os, pathlib, win32com
import time



"""This file is used by the quantify_opener.exe program.
It starts when the program is run and will close """


for line in sys.stdin:
    open_dir = line
    break


def is_quantify_open():
    windows = Desktop(backend="uia").windows()
    for window in windows:
        window = str(window)
        if open_dir.rsplit("\\", maxsplit=1)[1].lower() in window.lower():
            return True
    return False




def is_old_txt():
    global old_txt
    with open(f"{open_dir}\\instrument_list.txt", "r") as instrument_list:
        new_txt = instrument_list.readlines()
    if old_txt == new_txt:
        return True
    old_txt = new_txt
    return False


import pyvisa
import pyvisa.constants
_rm = pyvisa.ResourceManager()







instruments_string = ""
for address in _rm.list_resources():
    try:
        with _rm.open_resource(address) as opened_resource:
            opened_resource.set_visa_attribute(pyvisa.constants.ResourceAttribute.asrl_baud_rate, 921600)
            try:
                resource_idn = opened_resource.query("*IDN?")
                instruments_string += f" > Instrument Address: {address}    Instrument IDN: {resource_idn}\n\n"
            except:
                instruments_string += f" > Instrument Address: {address}    Instrument IDN: **Instrument did not respond to *IDN? query**\n\n"
    except:
        instruments_string += f" > Instrument Address: {address}    **Instrument's communication is currently occupied with another program.**\n\n"

with open(f"{open_dir}\\instrument_list.txt", "w+") as instrument_list:
    if instruments_string:
        instrument_list.write(instruments_string)
    else:
        instrument_list.write("No detected instruments...")












old_resources = _rm.list_resources()


with open(f"{open_dir}\\instrument_list.txt", "r") as instrument_list:
    old_txt = instrument_list.readlines()

change_recency = 0
while is_quantify_open():
    _resources = _rm.list_resources()
    if _resources == old_resources and is_old_txt():
        change_recency += 1
        if change_recency > 600:
            change_recency = 601
            time.sleep(4)
            continue
    else:
        change_recency = 0
    old_resources = _resources
    instruments_string = ""
    for address in _resources:
        try:
            with _rm.open_resource(address) as opened_resource:
                opened_resource.set_visa_attribute(pyvisa.constants.ResourceAttribute.asrl_baud_rate, 921600)
                try:
                    resource_idn = opened_resource.query("*IDN?")
                    instruments_string += f" > Instrument Address: {address}    Instrument IDN: {resource_idn}\n\n"
                except:
                    instruments_string += f" > Instrument Address: {address}    Instrument IDN: **Instrument did not respond to *IDN? query**\n\n"
        except:
            instruments_string += f" > Instrument Address: {address}    **Instrument's communication is currently occupied with another program.**\n\n"

    with open(f"{open_dir}\\instrument_list.txt", "w") as instrument_list:
        if instruments_string:
            instrument_list.write(instruments_string)
        else:
            instrument_list.write("No detected instruments...")
