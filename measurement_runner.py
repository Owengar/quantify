from source.runner import run
import numpy
from source.make_setpoint_list import make_setpoint_list

run("example_1d_script", [numpy.linspace(-2, 2, 100)])


