import sys
sys.dont_write_bytecode = True

import subprocess, os


"""
uninstallation = subprocess.Popen("pip uninstall numpy", stdin=subprocess.PIPE, stdout=sys.stdout, text=True)
uninstallation.stdin.write("Y\n")
uninstallation.stdin.flush()
uninstallation.wait()
print("done with uninstall")
os.system("pip install numpy")
"""

try:
    import math
    import json
    import numpy
    import qcodes
    from qcodes import Parameter, Instrument
    import quantify_core
    import quantify_core.data
    import quantify_core.data.handling
    from quantify_core.measurement import Gettable, MeasurementControl
    import sys, os, time
    import subprocess
    import traceback
    import threading
    import ctypes
    from ctypes import *
    from ctypes.wintypes import *
    import xarray
    import shutil
    import quantify_core.data.handling as dh
    from source.custom2D.cpp_interface import transfer
    from source import exchanger
    import source.save_functions as saver
    import qfy_tools

    try:
        from source.make_setpoint_list import make_setpoint_list
    except:
        try:
            from make_setpoint_list import make_setpoint_list
        except:
            raise ImportError("Was unable to import the make_setpoint_list function")
except ImportError as error:
    print("Something went wrong while importing base utilities form imports.py. Most likely something needs to be installed with pip.")
    raise error
__all__ = ["traceback", "saver", "math", "json", "ctypes", "sys", "shutil", "subprocess", "time", "numpy", "MeasurementControl", "quantify_core", "Instrument", "Parameter", "xarray", "dh", "os", "transfer", "exchanger", "threading", "qfy_tools"]
