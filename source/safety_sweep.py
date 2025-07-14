from functools import wraps
from typing import Callable, Any
from source.imports import *
import sys
sys.dont_write_bytecode = True



def make_parameter_safe(target_parameter : Parameter, maximum_safe_step_size : float, inter_delay_s : float, post_delay_s : float = 0):
    """
    A function used on a parameter object to add inter delay or post delay to its set function, as well as to define a maximum safe step size.

    Parameters
    -

    - .. target_parameter:: The parameter which will be the target of the delays and maximum safe step size.
    - .. maximum_safe_step_size:: A value that defines the maximum change that a settable parameter can undergo in one step, in the unit of the parameter. If this change is attempted to be exceeded, then it will automatically gradually step towards the target value using this step size.
    - .. inter_delay_s:: A delay in seconds that will occur between setting the target_parameter and any other work.
    - .. post_delay_s:: A delay in seconds that will after setting the target_parameter and any other work."""
    target_parameter.set = _wrap_set(target_parameter, target_parameter.set_raw, maximum_safe_step_size, inter_delay_s, post_delay_s)


_debug_printing = [False]
def set_debug_printing(set_to : bool):
    _debug_printing[0] = set_to


def _wrap_set(param, set_function: Callable[..., None], maximum_safe_step_size, inter_delay, post_delay, instrument=None) -> Callable[..., None]:
    @wraps(set_function)
    def set_wrapper(value: Any, **kwargs: Any) -> None:
        try:
            if not param.settable:
                raise TypeError("Trying to set a parameter that is not settable.")
            if param.abstract:
                raise NotImplementedError(
                    f"Trying to set an abstract parameter: {param.full_name}"
                )
            param.validate(value)

            # In some cases intermediate sweep values must be used.
            # Unless `maximum_safe_step_size` is defined, get_sweep_values will return
            # a list containing only `value`.
            steps = param.get_ramp_values(value, step=maximum_safe_step_size)

            for step_index, val_step in enumerate(steps):
                # even if the final value is valid we may be generating
                # steps that are not so validate them too
                param.validate(val_step)

                raw_val_step = param._from_value_to_raw_value(val_step)


                if _debug_printing[0]:
                    print(f"Safe ramping parameter: \"{param.name}\" to value of:  {raw_val_step}")

                

                # Check if delay between set operations is required
                t_elapsed = time.perf_counter() - param._t_last_set
                if t_elapsed < inter_delay:
                    # Sleep until time since last set is larger than
                    # inter_delay
                    time.sleep(inter_delay - t_elapsed)

                # Start timer to measure execution time of set_function
                t0 = time.perf_counter()

                set_function(raw_val_step, **kwargs)

                # Update last set time (used for calculating delays)
                param._t_last_set = time.perf_counter()

                # Check if any delay after setting is required
                t_elapsed = param._t_last_set - t0
                if t_elapsed < post_delay:
                    # Sleep until total time is larger than post_delay
                    time.sleep(post_delay - t_elapsed)

                param.cache._update_with(value=val_step, raw_value=raw_val_step)

        except Exception as e:
            e.args = e.args + (f"setting {param} to {value}",)
            raise e

    return set_wrapper
