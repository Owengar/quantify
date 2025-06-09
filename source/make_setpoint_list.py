from source.runner import run
import numpy
from source.make_setpoint_list import make_setpoint_list


import sys
print(numpy.linspace(-2, 2, 10))
print(make_setpoint_list([(-2, 2, 10)]))

run("example_1d_script", [make_setpoint_list([(-2, 2, 10), (2, -2, 10)])])


