import sys, math, numpy, time, itertools





#10^what to get to my unit?
prefix_scales = {"y":3, "z":3, "a":3, "f":3, "p":3, "n":3, "µ":3, "m":1, "c":2, "":0, "k":3, "M":3, "G":3, "T":3, "P":3, "E":3, "Z":3, "Y":3}
prefix_scales_values = list(prefix_scales.values())
prefix_scales_keys = list(prefix_scales.keys())
zero_index = prefix_scales_values.index(0)


def scale_unit(value, current_scale_index=prefix_scales_keys.index("")):

    if abs(value) > 999.99 :
        threshhold_to_go_up = 10**-prefix_scales_values[current_scale_index+1]
        value_upped = value * threshhold_to_go_up
        return scale_unit(value_upped, current_scale_index+1)
    elif value == 0:
        return (value, "zero")
    elif abs(value) < 0.1:
        threshhold_to_go_down = 10**prefix_scales_values[current_scale_index-1]
        value_downed = value * threshhold_to_go_down
        return scale_unit(value_downed, current_scale_index-1)
    else:
        return (value, prefix_scales_keys[current_scale_index])




def _n_range(start, stop):
    if start > stop:
        return range(start, stop, -1)
    else:
        return range(start, stop, 1)

def _get_scale_direction(scale : str):
    scale_index = prefix_scales_keys.index(scale)
    if scale_index < zero_index:
        return 1
    else:
        return -1

def _accumulate_scale_from_zero(scale : str):
    index = prefix_scales_keys.index(scale)
    accumulation = 0
    for i in _n_range(index, zero_index):
        accumulation += prefix_scales_values[i]
    return accumulation


def compare_scales(scale1, scale2):

    if scale1 == "zero" and scale2 == "zero":
        return ("", 0, 1)
    elif scale2 == "zero":
        return (scale1, _accumulate_scale_from_zero(scale1), 0)
    elif scale1 == "zero":
        return (scale2, _accumulate_scale_from_zero(scale2), 1)
    
    if prefix_scales_keys.index(scale1) > prefix_scales_keys.index(scale2):
        return (scale1, _accumulate_scale_from_zero(scale1), 0)
    else:
        return (scale2, _accumulate_scale_from_zero(scale2), 1)
    

def convert_unit_scale(data_first, data_second, debug=False):
    x1_val, x1_scale = scale_unit(data_first)
    x2_val, x2_scale = scale_unit(data_second)
   
    scale, scale_factor, index = compare_scales(x1_scale, x2_scale)
    #The scaled value we have chosen to be our base
    scaled_chosen_val = (x1_val, x2_val)[index]

    scale_direction = _get_scale_direction(scale)
    #scale the other value to the chosen value's scale
    scaled_unchosen_val = (data_first, data_second)[abs(index-1)] * (10**(scale_direction*scale_factor)) #[abs(index-1)] switchs 1 to 0 and 0 to 1
    
    if debug:
        print(scale_factor)
        #print(((data_first, data_second), (scaled_chosen_val, scaled_unchosen_val)))
    #figuring out what order to return our vals so that it is the same is the input
    if index == 0:
        return (scaled_chosen_val, scaled_unchosen_val, scale, (10**(scale_direction*scale_factor)))
    elif index == 1:
        return (scaled_unchosen_val, scaled_chosen_val, scale, (10**(scale_direction*scale_factor)))
    else:
        print("something went really wrong")

   
if __name__ == "__main__":
    print(scale_unit(0.01))         # "1.00 cm"
    print(scale_unit(1500))         # "1.50 km"
    print(scale_unit(0.000000001))   # "10.00 nm"
    print(scale_unit(1000))         # "1.00 kg"
    print(scale_unit(0.000001))     # "1.00 µs"
    print()

    res = convert_unit_scale(0.000000001, 0.000001000)
    print(res)
    print()