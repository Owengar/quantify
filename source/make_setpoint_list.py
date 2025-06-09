import numpy

def make_setpoint_list(ranges : list[tuple[float, float, int]]):
    """This is a helper function to assemble a setpoint list that is assembled in parts.
    
    The "ranges" parameter is a list of (start, stop, step_count) tuples, identical to what is inputted into the numpy.linspace function.
    
    All ranges in the list will be concatenated together into one numpy array and then returned."""
    base_list = []
    for setpoint_range in ranges:
        base_list.extend(list(numpy.linspace(setpoint_range[0], setpoint_range[1], setpoint_range[2])))

    return numpy.array(base_list)