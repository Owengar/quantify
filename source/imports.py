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
    import time
    import numpy
    import xarray
    from qcodes import Instrument, ManualParameter, Parameter, validators
    import quantify_core
    import quantify_core.visualization.pyqt_plotmon_remote as rpm
    import quantify_core.visualization.pyqt_plotmon as pqm
    from quantify_core.visualization.pyqt_plotmon import PlotMonitor_pyqt
    import quantify_core.data.handling as dh
    from quantify_core.measurement import Gettable, MeasurementControl
    from typing import Literal
    import os
    import subprocess
    import shutil
    import sys
    from pywinauto import Desktop
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import ctypes
    import plotly.express as px
    import plotly
    import pandas
    import json
    import math
    import psutil
    import traceback
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
__all__ = ["traceback", "psutil", "math", "plotly", "json", "pandas", "px", "ctypes", "plt", "animation", "Desktop", "sys", "shutil", "subprocess", "time", "numpy", "Literal","MeasurementControl", "Gettable", "pqm", "rpm", "quantify_core", "Instrument", "PlotMonitor_pyqt", "Parameter", "xarray", "dh", "ManualParameter", "validators", "os"]
