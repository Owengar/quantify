import numpy


getpoints_total = numpy.array(numpy.arange(400))

print(getpoints_total[-100:])
graph_points : numpy.ndarray = numpy.array([numpy.nan] * 100)
for i,getpoint in enumerate(getpoints_total[::-1]):
    if numpy.isnan(getpoint):
        continue
    else:
        graph_points[99-i] = getpoint

print(graph_points)