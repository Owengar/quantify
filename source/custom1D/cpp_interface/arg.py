


import numpy
import ctypes



my_float_array = numpy.full(10, numpy.nan, dtype=ctypes.c_float)


inserter = [5, 4 , 3]
print(numpy.indices([len(inserter)]))
my_float_array.put(numpy.indices([len(inserter)]), inserter)


print(my_float_array)