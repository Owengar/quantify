import sys
sys.dont_write_bytecode = True

from source.safety_sweep import make_parameter_safe

#from source.parameter_limiter import limit_parameter, expression


def set_debug_printing(set_to : bool):
    from source.safety_sweep import set_debug_printing as sweep_debug
    sweep_debug(set_to)

