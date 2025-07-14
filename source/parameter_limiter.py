from source.imports import *
import source._process_exchange as _process_exchange
import sys
sys.dont_write_bytecode = True





class expression():

    def _evaluate(compare_to : int | float) -> bool:
        pass

    def __init__(self, comparer : Literal[">", "≥", "<", "≤"], value : int|float):
        self.comparer = comparer
        self.value = value

        def greater_than(compare_to : int|float):
            return compare_to > value
        def greater_than_eq(compare_to : int|float):
            return compare_to >= value
        def less_than(compare_to : int|float):
            return compare_to < value
        def less_than_eq(compare_to : int|float):
            return compare_to <= value
    
        comparison_map = {">" : greater_than, "≥" : greater_than_eq, "<" : less_than, "≤" : less_than_eq}
        

        self._evaluate = comparison_map[comparer]
    
    def __repr__(self):
        return f"{self.comparer} {self.value}"
    
    def __str__(self):
        return self.__repr__()



def limit_parameter(target_parameter : Parameter, limit_expressions : list[expression]):
    """
        Set a value limit on a parameter, such that when any of the limit expressions become true, the measurement stops.

        Parameters
        -

        - .. target_parameter:: The parameter which should be evaluated against the limit expressions every new data point.
        - .. limit_expressions:: A list of expression objects, that will each be checked with the current value of the target_parameter. If any expression becomes true, the measurement stops.
    """

    unwrapped_get = target_parameter.get
    def wrap_get():
        new_val = unwrapped_get()
        for expression in limit_expressions:
            if expression._evaluate(new_val):
                print(f"\nParameter \"{target_parameter.label}\" has exceeded its limit of {expression}\n Stopping measurement...\n", flush=True)
                _process_exchange._make_signal_file("limiter_stop.txt")
        return new_val
                
    target_parameter.get = target_parameter._wrap_get(wrap_get)

