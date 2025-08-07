import sys, math





#10^what to get to my unit?
prefix_scales = {"y":3, "z":3, "a":3, "f":3, "p":3, "n":3, "µ":3, "m":1, "c":2, "":0, "k":3, "M":3, "G":3, "T":3, "P":3, "E":3, "Z":3, "Y":3}
prefix_scales_values = list(prefix_scales.values())
prefix_scales_keys = list(prefix_scales.keys())


def scale_unit(value, current_scale_index=prefix_scales_keys.index("")):

    if abs(value) > 999.99 :
        threshhold_to_go_up = 10**-prefix_scales_values[current_scale_index+1]
        value_upped = value * threshhold_to_go_up
        return scale_unit(value_upped, current_scale_index+1)
    elif value == 0:
        return (value, prefix_scales_keys[current_scale_index])
    elif abs(value) < 0.1:
        threshhold_to_go_down = 10**prefix_scales_values[current_scale_index-1]
        value_downed = value * threshhold_to_go_down
        return scale_unit(value_downed, current_scale_index-1)
    else:
        return (value, prefix_scales_keys[current_scale_index])








def compare_scales(scale1, scale2):
    if prefix_scales_keys.index(scale1) > prefix_scales_keys.index(scale2):
        return scale1
    else:
        return scale2

def convert_unit_scale(point1, point2):
    x1_val, x1_scale = scale_unit(point1[0])
    x2_val, x2_scale = scale_unit(point2[0])
    print(compare_scales(x1_scale, x2_scale))
    print(x2_val)

    
if __name__ == "__main__":
    print(scale_unit(0.01))         # "1.00 cm"
    print(scale_unit(1500))         # "1.50 km"
    print(scale_unit(0.000000001))   # "10.00 nm"
    print(scale_unit(1000))         # "1.00 kg"
    print(scale_unit(0.000001))     # "1.00 µs"

