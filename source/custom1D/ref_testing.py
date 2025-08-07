from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import QDac2
from qcodes.instrument_drivers.Keysight.Keysight_34461A_submodules import Keysight34461A


import json
import numpy
import qcodes
from qcodes import Parameter, Instrument, Measurement
import quantify_core
import quantify_core.data
import quantify_core.data.handling
from quantify_core.measurement import Gettable, MeasurementControl
import sys, os, time
import subprocess
import multiprocessing
import threading
import ctypes
from ctypes import *
from ctypes.wintypes import *
import xarray
import pickle




def deref(pid, address, length):
    PROCESS_ID = 9476 # From TaskManager for Notepad.exe
    PROCESS_HEADER_ADDR = 0x7ff7b81e0000 # From SysInternals VMMap utility

    # read from addresses
    STRLEN = length

    PROCESS_VM_READ = 0x0010

    k32 = WinDLL('kernel32')
    k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
    k32.OpenProcess.restype = HANDLE
    k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
    k32.ReadProcessMemory.restype = BOOL

    process = k32.OpenProcess(PROCESS_VM_READ, 0, pid)
    buf = create_string_buffer(STRLEN)
    s = c_size_t()
    if k32.ReadProcessMemory(process, address, buf, STRLEN, byref(s)):
        obj = ctypes.cast(buf, py_object).value
        print(obj)
        return obj





lis = {"here" : []}

lis_address_and_size = f"{id(lis)} {lis.__sizeof__()}"

derefed_id_and_len = deref(os.getpid(), id(lis_address_and_size), lis_address_and_size.__sizeof__())

derefed_id_and_len = derefed_id_and_len.split(" ")
deref(os.getpid(), int(derefed_id_and_len[0]), int(derefed_id_and_len[1]))