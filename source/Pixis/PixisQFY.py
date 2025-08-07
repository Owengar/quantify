import ctypes as ctypes
import os


picamLibrary = 'C:\\Program Files\\Common Files\\Princeton Instruments\\Picam\\Runtime\\Picam.dll'
#picam = load(picamLibrary) # Not sure where to put these?
os.add_dll_directory('C:\\Program Files\\Common Files\\Princeton Instruments\\Picam\\Runtime')
picam = ctypes.cdll.LoadLibrary(picamLibrary) # Not sure where to put these?

print("before")
err = picam.Picam_UninitializeLibrary()
print(err)
err = picam.Picam_InitializeLibrary()
print("after")