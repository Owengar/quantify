from source.runner import run
import numpy

run("example_2d_script", [numpy.linspace(-2, 2, 1000), numpy.linspace(1, 1000, 1000)])


run("example_2d_script", [numpy.linspace(-2, 2, 100), numpy.linspace(1, 100, 100)])
