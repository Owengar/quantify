import ctypes
import sys
import os 
import numpy
import subprocess
import time
import psutil
import json
import qfy_tools



c_float_p = ctypes.POINTER(ctypes.c_float)
c_float_array = numpy.ctypeslib.ndpointer(dtype=ctypes.c_float, ndim=1, flags="C_CONTIGUOUS")
handle = None
def setup_dll_handle():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.add_dll_directory(dir_path)
    handle = ctypes.CDLL(dir_path + "\\multi.dll", winmode=0)     
    handle.set_array.argtypes = [c_float_array, ctypes.c_int]
    handle.get_array.argtypes = [c_float_array, ctypes.c_int]
    handle.get_array_pointer.argtypes = [ctypes.c_int]
    handle.get_array_pointer.restype = ctypes.c_int64
    handle.setup_parent_pid.argtypes = [ctypes.c_int]
    handle.get_array_child.argtypes = [c_float_array, ctypes.c_int64]
    handle.set_setp_index.argtypes = [ctypes.c_int64]
    handle.get_setp_index.argtypes = [ctypes.c_int64]
    handle.get_setp_index.restype = ctypes.c_int64
    handle.get_setp_pointer.restype = ctypes.c_int64
    handle.get_transfer_semaphore_pointer.restype = ctypes.c_int64
    handle.set_transfer_semaphore.argtypes = [ctypes.c_bool]
    handle.get_transfer_semaphore.argtypes = [ctypes.c_int64]
    handle.get_transfer_semaphore.restype = ctypes.c_bool
    



    return handle







array_length = 1000*4000
arrays = [numpy.full(array_length, numpy.nan, dtype=ctypes.c_float)] * 10
array_pointers = None


def child_main():
    global handle, array_pointers

    array_pointers = json.loads(sys.argv[1])
    my_float_array = numpy.full(array_length, numpy.nan, dtype=ctypes.c_float)
    handle = setup_dll_handle()
    handle.setup_parent_pid(int(sys.argv[2]))

    qfy_tools.debug_print("transfer child main2D done!")

def child_get_array(index):
    handle.get_array_child(arrays[index], array_pointers[index])
    return arrays[index]

def main(recompile=True):
    global handle
    #TODO: PLEASE find a way to statically link everything in this compile command. It breaks if I don't have g++ installed! Thank you!
    if recompile:
        os.system("g++ -fPIC -static -shared -o multi.dll cpp_interface\\multi.cpp") #compile c++
        os.system("del cpp_interface\\multi.dll")
        os.system("move multi.dll cpp_interface")
    handle = setup_dll_handle()
    handle.dll_main()


def write_array(index, source_list : list):
    arrays[index].put(numpy.indices([len(source_list)]), source_list)
    handle.set_array(arrays[index], index)

def get_child_args():
    array_pointers = [handle.get_array_pointer(p) for p in range(10)]
    return f"{json.dumps(array_pointers).replace(" ", "")} {os.getpid()}"

time.sleep(1)

