#!/usr/bin/env python




import InstrumentDriver

import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

#import picam.pypicam as pc

from collections import Counter

"""Test for talking to Picam"""
import ctypes as ctypes

#import matplotlib.pyplot as plt
""" Import standard type definitions from PiTypes.py """
from PiTypes import *

""" Import non-standard type definitions from PiTypesMore.py """
#from PiTypesMore import *
##### Some of the types defined dependent on an enum: PicamStringSize.  From picam.h we have the following:
"""
typedef enum PicamStringSize
{
    PicamStringSize_SensorName     =  64,
    PicamStringSize_SerialNumber   =  64,
    PicamStringSize_FirmwareName   =  64,
    PicamStringSize_FirmwareDetail = 256
} PicamStringSize;
"""
### Which is why I define the following:
PicamStringSize_SensorName = PicamStringSize_SerialNumber = PicamStringSize_FirmwareName = 64
PicamStringSize_FirmwareDetail = 256

"""
typedef struct PicamCameraID
{
    PicamModel          model;
    PicamComputerInterface computer_interface;
    pichar                 sensor_name[PicamStringSize_SensorName];
    pichar                 serial_number[PicamStringSize_SerialNumber];
} PicamCameraID;
"""
class PicamCameraID(ctypes.Structure):
    _fields_ = [("model", PicamModel),
                ("computer_interface", PicamComputerInterface),
                ("sensor_name", pichar * PicamStringSize_SensorName),
                ("serial_number", pichar * PicamStringSize_SerialNumber)]

# PicamHandle
PicamHandle = ctypes.c_void_p


# PicamFirmwareDetail
"""
typedef struct PicamFirmwareDetail
{
    pichar name[PicamStringSize_FirmwareName];
    pichar detail[PicamStringSize_FirmwareDetail];
} PicamFirmwareDetail;
"""

class PicamFirmwareDetail(ctypes.Structure):
    _fields_ = [("name", pichar * PicamStringSize_FirmwareName),
                ("detail", pichar * PicamStringSize_FirmwareDetail)]

##### Types defined on pp57-70 (chapter 4: Camera Parameter Values, Inofrmation, Constraints, and Commitment)
    ### Saving this for later!

##### Types defined on p76 (chapter 5: Camera Data Acquisition)

# PicamAvailableData
"""
typedef struct PicamAvailableData
{
    void* initial_readout;
    pi64s readout_count;
} PicamAvailableData;
"""
class PicamAvailableData(ctypes.Structure):
    _fields_ = [("initial_readout", ctypes.c_void_p), ("readout_count", pi64s)]

class PicamAvailableData2(ctypes.Structure):
    _fields_ = [ ( "initial_readout", ctypes.POINTER(type(ctypes.c_void_p()))), ("readout_count", pi64s)]

# PicamAcquisitionErrorsMask
"""
typedef enum PicamAcquisitionErrorsMask
{
    PicamAcquisitionErrorsMask_None           = 0x0,
    PicamAcquisitionErrorsMask_DataLost       = 0x1,
    PicamAcquisitionErrorsMask_ConnectionLost = 0x2
} PicamAcquisitionErrorsMask; /* (0x4) */
"""
PicamAcquisitionErrorsMask = ctypes.c_int

# PicamAcquisitionStatus
class PicamAcquisitionStatus(ctypes.Structure):
    _fields_ = [("running",pibln),
                ("errors",PicamAcquisitionErrorsMask),
                ("readout_rate",piflt)]

# PicamRoi
class PicamRoi(ctypes.Structure):
    _fields_ = [("x",piint),
                ("width",piint),
                ("x_binning",piint),
                ("y",piint),
                ("height",piint),
                ("y_binning",piint)]

class PicamRois(ctypes.Structure):
    _fields_ = [("roi_array",ctypes.POINTER(PicamRoi)),
                ("roi_count",piint)]

    # the following is based on: 
    # http://stackoverflow.com/questions/17101845/python-ctypes-array-of-structs
    def __init__(self):
        elements = (PicamRoi * 10)() # assume 10 rois at the most
        self.roi_array = ctypes.cast(elements,ctypes.POINTER(PicamRoi))


""" Import function definitions from PiFunctions.py """
""" This should contian all of the functions from picam.h """
#from PiFunctions import *


""" Import parameter lookup from PiParameterLookup.py """
""" This file includes a function PI_V and a lookup table to return the code
    for different Picam Parameters described in chapter 4 """
from PiParameterLookup import *

###================================================================================================###
###================================================================================================###
###================================================================================================###
############################
##### Custom Functions #####
############################

def pointer(x):
    """Returns a ctypes pointer"""
    ptr = ctypes.pointer(x)
    return ptr


def load(x):
    """Loads a library where argument is location of library"""
    x = ctypes.cdll.LoadLibrary(x)
    return x

picamLibrary = 'C:\\Program Files\\Common Files\\Princeton Instruments\\Picam\\Runtime\\Picam.dll'
#picam = load(picamLibrary) # Not sure where to put these?
picam = ctypes.cdll.LoadLibrary(picamLibrary) # Not sure where to put these?

###=====================================================================================================###
### Begin imported Functions

def Picam_GetVersion(major, minor, distribution, released):
    """ PICAM_API Picam_GetVersion( piint* major, piint* minor, piint* distribution, piint* released) """
    err = picam.Picam_GetVersion( major, minor, distribution, released)
    err = ReturnPicamError(err)
    return err

def Picam_IsLibraryInitialized(inited):
    """ PICAM_API Picam_IsLibraryInitialized( pibln* inited ) """
    err = picam.Picam_IsLibraryInitialized(inited)
    err = ReturnPicamError(err)
    return err

def Picam_InitializeLibrary():
    """ PICAM_API Picam_InitializeLibrary( void ) """
    err = picam.Picam_InitializeLibrary()
    err = ReturnPicamError(err)
    return err

def Picam_UninitializeLibrary():
    """ PICAM_API Picam_UninitializeLibrary( void ) """
    err = picam.Picam_UninitializeLibrary()
    err = ReturnPicamError(err)
    return err

def Picam_DestroyString(s):
    """ PICAM_API Picam_DestroyString( const pichar* s ) """
    err = picam.Picam_DestroyString(s)
    err = ReturnPicamError(err)
    return err

def Picam_GetEnumerationString(type, value, s):
    """ PICAM_API Picam_GetEnumerationString( PicamEnumeratedType type, piint value, const pichar** s) """
    err = picam.Picam_GetEnumerationString( type, value, s)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyCameraIDs(id_array):
    """ PICAM_API Picam_DestroyCameraIDs( const PicamCameraID* id_array ) """
    err = picam.Picam_DestroyCameraIDs(id_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetAvailableCameraIDs(id_array, id_count):
    """ PICAM_API Picam_GetAvailableCameraIDs( const PicamCameraID** id_array, piint* id_count) """
    err = picam.Picam_GetAvailableCameraIDs( id_array, id_count)
    err = ReturnPicamError(err)
    return err

def Picam_GetUnavailableCameraIDs(id_array, id_count):
    """ PICAM_API Picam_GetUnavailableCameraIDs( const PicamCameraID** id_array, piint* id_count) """
    err = picam.Picam_GetUnavailableCameraIDs( id_array, id_count)
    err = ReturnPicamError(err)
    return err

def Picam_IsCameraIDConnected(id, connected):
    """ PICAM_API Picam_IsCameraIDConnected( const PicamCameraID* id, pibln* connected) """
    err = picam.Picam_IsCameraIDConnected( id, connected)
    err = ReturnPicamError(err)
    return err

def Picam_IsCameraIDOpenElsewhere(id, open_elsewhere):
    """ PICAM_API Picam_IsCameraIDOpenElsewhere( const PicamCameraID* id, pibln* open_elsewhere) """
    err = picam.Picam_IsCameraIDOpenElsewhere( id, open_elsewhere)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyHandles(handle_array):
    """ PICAM_API Picam_DestroyHandles( const PicamHandle* handle_array ) """
    err = picam.Picam_DestroyHandles(handle_array)
    err = ReturnPicamError(err)
    return err

def Picam_OpenFirstCamera(camera):
    """ PICAM_API Picam_OpenFirstCamera( PicamHandle* camera ) """
    err = picam.Picam_OpenFirstCamera(camera)
    err = ReturnPicamError(err)
    return err

def Picam_OpenCamera(id, camera):
    """ PICAM_API Picam_OpenCamera( const PicamCameraID* id, PicamHandle* camera) """
    err = picam.Picam_OpenCamera( id, camera)
    err = ReturnPicamError(err)
    return err

def Picam_CloseCamera(camera):
    """ PICAM_API Picam_CloseCamera( PicamHandle camera ) """
    err = picam.Picam_CloseCamera(camera)
    err = ReturnPicamError(err)
    return err

def Picam_GetOpenCameras(camera_array, camera_count):
    """ PICAM_API Picam_GetOpenCameras( const PicamHandle** camera_array, piint* camera_count) """
    err = picam.Picam_GetOpenCameras( camera_array, camera_count)
    err = ReturnPicamError(err)
    return err

def Picam_IsCameraConnected(camera, connected):
    """ PICAM_API Picam_IsCameraConnected( PicamHandle camera, pibln* connected) """
    err = picam.Picam_IsCameraConnected( camera, connected)
    err = ReturnPicamError(err)
    return err

def Picam_GetCameraID(camera, id):
    """ PICAM_API Picam_GetCameraID( PicamHandle camera, PicamCameraID* id) """
    err = picam.Picam_GetCameraID( camera, id)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyFirmwareDetails(firmware_array):
    """ PICAM_API Picam_DestroyFirmwareDetails( const PicamFirmwareDetail* firmware_array) """
    err = picam.Picam_DestroyFirmwareDetails( firmware_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetFirmwareDetails(id, firmware_array, firmware_count):
    """ PICAM_API Picam_GetFirmwareDetails( const PicamCameraID* id, const PicamFirmwareDetail** firmware_array, piint* firmware_count) """
    err = picam.Picam_GetFirmwareDetails( id, firmware_array, firmware_count)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyModels(model_array):
    """ PICAM_API Picam_DestroyModels( const PicamModel* model_array ) """
    err = picam.Picam_DestroyModels(model_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetAvailableDemoCameraModels(model_array, model_count):
    """ PICAM_API Picam_GetAvailableDemoCameraModels( const PicamModel** model_array, piint* model_count) """
    err = picam.Picam_GetAvailableDemoCameraModels( model_array, model_count)
    err = ReturnPicamError(err)
    return err

def Picam_ConnectDemoCamera(model, serial_number, id):
    """ PICAM_API Picam_ConnectDemoCamera( PicamModel model, const pichar* serial_number, PicamCameraID* id) """
    err = picam.Picam_ConnectDemoCamera( model, serial_number, id)
    err = ReturnPicamError(err)
    return err

def Picam_DisconnectDemoCamera(id):
    """ PICAM_API Picam_DisconnectDemoCamera( const PicamCameraID* id ) """
    err = picam.Picam_DisconnectDemoCamera(id)
    err = ReturnPicamError(err)
    return err

def Picam_IsDemoCamera(id, demo):
    """ PICAM_API Picam_IsDemoCamera( const PicamCameraID* id, pibln* demo) """
    err = picam.Picam_IsDemoCamera( id, demo)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    err = picam.Picam_GetParameterIntegerValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint value) """
    err = picam.Picam_SetParameterIntegerValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterIntegerValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint value, pibln* settable) """
    err = picam.Picam_CanSetParameterIntegerValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterLargeIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s* value) """
    err = picam.Picam_GetParameterLargeIntegerValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterLargeIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s value) """
    err = picam.Picam_SetParameterLargeIntegerValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterLargeIntegerValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s value, pibln* settable) """
    err = picam.Picam_CanSetParameterLargeIntegerValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterFloatingPointValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    err = picam.Picam_GetParameterFloatingPointValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterFloatingPointValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt value) """
    err = picam.Picam_SetParameterFloatingPointValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterFloatingPointValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt value, pibln* settable) """
    err = picam.Picam_CanSetParameterFloatingPointValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyRois(rois):
    """ PICAM_API Picam_DestroyRois( const PicamRois* rois ) """
    err = picam.Picam_DestroyRois(rois)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterRoisValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois** value) """
    err = picam.Picam_GetParameterRoisValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterRoisValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois* value) """
    err = picam.Picam_SetParameterRoisValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterRoisValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois* value, pibln* settable) """
    err = picam.Picam_CanSetParameterRoisValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyPulses(pulses):
    """ PICAM_API Picam_DestroyPulses( const PicamPulse* pulses ) """
    err = picam.Picam_DestroyPulses(pulses)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterPulseValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse** value) """
    err = picam.Picam_GetParameterPulseValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterPulseValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse* value) """
    err = picam.Picam_SetParameterPulseValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterPulseValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse* value, pibln* settable) """
    err = picam.Picam_CanSetParameterPulseValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyModulations(modulations):
    """ PICAM_API Picam_DestroyModulations( const PicamModulations* modulations ) """
    err = picam.Picam_DestroyModulations(modulations)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterModulationsValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations** value) """
    err = picam.Picam_GetParameterModulationsValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterModulationsValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations* value) """
    err = picam.Picam_SetParameterModulationsValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterModulationsValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations* value, pibln* settable) """
    err = picam.Picam_CanSetParameterModulationsValue( camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterIntegerDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterIntegerDefaultValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    err = picam.Picam_GetParameterIntegerDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterLargeIntegerDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterLargeIntegerDefaultValue( PicamHandle camera, PicamParameter parameter, pi64s* value) """
    err = picam.Picam_GetParameterLargeIntegerDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterFloatingPointDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterFloatingPointDefaultValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    err = picam.Picam_GetParameterFloatingPointDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterRoisDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterRoisDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamRois** value) """
    err = picam.Picam_GetParameterRoisDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterPulseDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterPulseDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamPulse** value) """
    err = picam.Picam_GetParameterPulseDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterModulationsDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterModulationsDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamModulations** value) """
    err = picam.Picam_GetParameterModulationsDefaultValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanSetParameterOnline(camera, parameter, onlineable):
    """ PICAM_API Picam_CanSetParameterOnline( PicamHandle camera, PicamParameter parameter, pibln* onlineable) """
    err = picam.Picam_CanSetParameterOnline( camera, parameter, onlineable)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterIntegerValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterIntegerValueOnline( PicamHandle camera, PicamParameter parameter, piint value) """
    err = picam.Picam_SetParameterIntegerValueOnline( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterFloatingPointValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterFloatingPointValueOnline( PicamHandle camera, PicamParameter parameter, piflt value) """
    err = picam.Picam_SetParameterFloatingPointValueOnline( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_SetParameterPulseValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterPulseValueOnline( PicamHandle camera, PicamParameter parameter, const PicamPulse* value) """
    err = picam.Picam_SetParameterPulseValueOnline( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_CanReadParameter(camera, parameter, readable):
    """ PICAM_API Picam_CanReadParameter( PicamHandle camera, PicamParameter parameter, pibln* readable) """
    err = picam.Picam_CanReadParameter( camera, parameter, readable)
    err = ReturnPicamError(err)
    return err

def Picam_ReadParameterIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_ReadParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    err = picam.Picam_ReadParameterIntegerValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_ReadParameterFloatingPointValue(camera, parameter, value):
    """ PICAM_API Picam_ReadParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    err = picam.Picam_ReadParameterFloatingPointValue( camera, parameter, value)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyParameters(parameter_array):
    """ PICAM_API Picam_DestroyParameters( const PicamParameter* parameter_array ) """
    err = picam.Picam_DestroyParameters(parameter_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameters(camera, parameter_array, parameter_count):
    """ PICAM_API Picam_GetParameters( PicamHandle camera, const PicamParameter** parameter_array, piint* parameter_count) """
    err = picam.Picam_GetParameters( camera, parameter_array, parameter_count)
    err = ReturnPicamError(err)
    return err

def Picam_DoesParameterExist(camera, parameter, exists):
    """ PICAM_API Picam_DoesParameterExist( PicamHandle camera, PicamParameter parameter, pibln* exists) """
    err = picam.Picam_DoesParameterExist( camera, parameter, exists)
    err = ReturnPicamError(err)
    return err

def Picam_IsParameterRelevant(camera, parameter, relevant):
    """ PICAM_API Picam_IsParameterRelevant( PicamHandle camera, PicamParameter parameter, pibln* relevant) """
    err = picam.Picam_IsParameterRelevant( camera, parameter, relevant)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterValueType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterValueType( PicamHandle camera, PicamParameter parameter, PicamValueType* type) """
    err = picam.Picam_GetParameterValueType( camera, parameter, type)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterEnumeratedType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterEnumeratedType( PicamHandle camera, PicamParameter parameter, PicamEnumeratedType* type) """
    err = picam.Picam_GetParameterEnumeratedType( camera, parameter, type)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterValueAccess(camera, parameter, access):
    """ PICAM_API Picam_GetParameterValueAccess( PicamHandle camera, PicamParameter parameter, PicamValueAccess* access) """
    err = picam.Picam_GetParameterValueAccess( camera, parameter, access)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterConstraintType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterConstraintType( PicamHandle camera, PicamParameter parameter, PicamConstraintType* type) """
    err = picam.Picam_GetParameterConstraintType( camera, parameter, type)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyCollectionConstraints(constraint_array):
    """ PICAM_API Picam_DestroyCollectionConstraints( const PicamCollectionConstraint* constraint_array) """
    err = picam.Picam_DestroyCollectionConstraints( constraint_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterCollectionConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterCollectionConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamCollectionConstraint** constraint) """
    err = picam.Picam_GetParameterCollectionConstraint( camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyRangeConstraints(constraint_array):
    """ PICAM_API Picam_DestroyRangeConstraints( const PicamRangeConstraint* constraint_array) """
    err = picam.Picam_DestroyRangeConstraints( constraint_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterRangeConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterRangeConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamRangeConstraint** constraint) """
    err = picam.Picam_GetParameterRangeConstraint( camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyRoisConstraints(constraint_array):
    """ PICAM_API Picam_DestroyRoisConstraints( const PicamRoisConstraint* constraint_array) """
    err = picam.Picam_DestroyRoisConstraints( constraint_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterRoisConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterRoisConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamRoisConstraint** constraint) """
    err = picam.Picam_GetParameterRoisConstraint( camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyPulseConstraints(constraint_array):
    """ PICAM_API Picam_DestroyPulseConstraints( const PicamPulseConstraint* constraint_array) """
    err = picam.Picam_DestroyPulseConstraints( constraint_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterPulseConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterPulseConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamPulseConstraint** constraint) """
    err = picam.Picam_GetParameterPulseConstraint( camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err

def Picam_DestroyModulationsConstraints(constraint_array):
    """ PICAM_API Picam_DestroyModulationsConstraints( const PicamModulationsConstraint* constraint_array) """
    err = picam.Picam_DestroyModulationsConstraints( constraint_array)
    err = ReturnPicamError(err)
    return err

def Picam_GetParameterModulationsConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterModulationsConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamModulationsConstraint** constraint) """
    err = picam.Picam_GetParameterModulationsConstraint( camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err

def Picam_AreParametersCommitted(camera, committed):
    """ PICAM_API Picam_AreParametersCommitted( PicamHandle camera, pibln* committed) """
    err = picam.Picam_AreParametersCommitted( camera, committed)
    err = ReturnPicamError(err)
    return err

def Picam_CommitParameters(camera, failed_parameter_array, failed_parameter_count):
    """ PICAM_API Picam_CommitParameters( PicamHandle camera, const PicamParameter** failed_parameter_array, piint* failed_parameter_count) """
    err = picam.Picam_CommitParameters( camera, failed_parameter_array, failed_parameter_count)
    err = ReturnPicamError(err)
    return err

def Picam_Acquire(camera, readout_count, readout_time_out, available, errors):
    """ PICAM_API Picam_Acquire( PicamHandle camera, pi64s readout_count, piint readout_time_out, PicamAvailableData* available, PicamAcquisitionErrorsMask* errors) """
    err = picam.Picam_Acquire( camera, readout_count, readout_time_out, available, errors)
    err = ReturnPicamError(err)
    return err

def Picam_StartAcquisition(camera):
    """ PICAM_API Picam_StartAcquisition( PicamHandle camera ) """
    err = picam.Picam_StartAcquisition(camera)
    err = ReturnPicamError(err)
    return err

def Picam_StopAcquisition(camera):
    """ PICAM_API Picam_StopAcquisition( PicamHandle camera ) """
    err = picam.Picam_StopAcquisition(camera)
    err = ReturnPicamError(err)
    return err

def Picam_IsAcquisitionRunning(camera, running):
    """ PICAM_API Picam_IsAcquisitionRunning( PicamHandle camera, pibln* running) """
    err = picam.Picam_IsAcquisitionRunning( camera, running)
    err = ReturnPicamError(err)
    return err

def Picam_WaitForAcquisitionUpdate(camera, readout_time_out, available, status):
    """ PICAM_API Picam_WaitForAcquisitionUpdate( PicamHandle camera, piint readout_time_out, PicamAvailableData* available, PicamAcquisitionStatus* status) """
    err = picam.Picam_WaitForAcquisitionUpdate( camera, readout_time_out, available, status)
    err = ReturnPicamError(err)
    return err


def ReturnPicamError(errcode):
    """expects integer error code.  Returns string with description"""
    if(errcode == 0):
        err = "PicamError_None"
    if(errcode == 4):
        err = "PicamError_UnexpectedError"
    if(errcode == 3):
        err = "PicamError_UnexpectedNullPointer"
    if(errcode == 35):
        err = "PicamError_InvalidPointer"
    if(errcode == 39):
        err = "PicamError_InvalidCount"
    if(errcode == 42):
        err = "PicamError_InvalidOperation"
    if(errcode == 1):
        err = "PicamError_LibraryNotInitialized"
    if(errcode == 5):
        err = "PicamError_LibraryAlreadyInitialized"
    if(errcode == 16):
        err = "PicamError_InvalidEnumeratedType"
    if(errcode == 17):
        err = "PicamError_EnumerationValueNotDefined"
    if(errcode == 18):
        err = "PicamError_NotDiscoveringCameras"
    if(errcode == 19):
        err = "PicamError_AlreadyDiscoveringCameras"
    if(errcode == 34):
        err = "PicamError_NoCamerasAvailable"
    if(errcode == 7):
        err = "PicamError_CameraAlreadyOpened"
    if(errcode == 8):
        err = "PicamError_InvalidCameraID"
    if(errcode == 9):
        err = "PicamError_InvalidHandle"
    if(errcode == 15):
        err = "PicamError_DeviceCommunicationFailed"
    if(errcode == 23):
        err = "PicamError_DeviceDisconnected"
    if(errcode == 24):
        err = "PicamError_DeviceOpenElsewhere"
    if(errcode == 6):
        err = "PicamError_InvalidDemoModel"
    if(errcode == 21):
        err = "PicamError_InvalidDemoSerialNumber"
    if(errcode == 22):
        err = "PicamError_DemoAlreadyConnected"
    if(errcode == 40):
        err = "PicamError_DemoNotSupported"
    if(errcode == 11):
        err = "PicamError_ParameterHasInvalidValueType"
    if(errcode == 13):
        err = "PicamError_ParameterHasInvalidConstraintType"
    if(errcode == 12):
        err = "PicamError_ParameterDoesNotExist"
    if(errcode == 10):
        err = "PicamError_ParameterValueIsReadOnly"
    if(errcode == 2):
        err = "PicamError_InvalidParameterValue"
    if(errcode == 38):
        err = "PicamError_InvalidConstraintCategory"
    if(errcode == 14):
        err = "PicamError_ParameterValueIsIrrelevant"
    if(errcode == 25):
        err = "PicamError_ParameterIsNotOnlineable"
    if(errcode == 26):
        err = "PicamError_ParameterIsNotReadable"
    if(errcode == 28):
        err = "PicamError_InvalidParameterValues"
    if(errcode == 29):
        err = "PicamError_ParametersNotCommitted"
    if(errcode == 30):
        err = "PicamError_InvalidAcquisitionBuffer"
    if(errcode == 36):
        err = "PicamError_InvalidReadoutCount"
    if(errcode == 37):
        err = "PicamError_InvalidReadoutTimeOut"
    if(errcode == 31):
        err = "PicamError_InsufficientMemory"
    if(errcode == 20):
        err = "PicamError_AcquisitionInProgress"
    if(errcode == 27):
        err = "PicamError_AcquisitionNotInProgress"
    if(errcode == 32):
        err = "PicamError_TimeOutOccurred"
    if(errcode == 33):
        err = "PicamError_AcquisitionUpdatedHandlerRegistered"
    if(errcode == 41):
        err = "PicamError_InvalidNvramSection"
    return err


###==================================================================================================###
#print('Initialize Camera.',Picam_InitializeLibrary())
Picam_InitializeLibrary()
#print('\n')
major = piint()
minor = piint()
distribution = piint()
release = piint()
Picam_GetVersion(pointer(major),pointer(minor),pointer(distribution),pointer(release))
#print('Check Software Version. ',Picam_GetVersion(pointer(major),pointer(minor),pointer(distribution),pointer(release)))
#print('Picam Version ',major.value,'.',minor.value,'.',distribution.value,' Released: ',release.value)
major.value
minor.value
distribution.value
release.value
#print('\n')


class PyPICAM():
    """Provides basic camera features and init"""
    camera = PicamHandle()
    readoutstride = piint(0)
    readout_count = pi64s(1)
    readout_time_out = piint(-1) # -1 is same as NO_TIMEOUT?
    available = PicamAvailableData()
    errors = PicamAcquisitionErrorsMask()
    myroi = PicamRoi()


    def __init__(self):
        #print('Opening First Camera')
        #print(Picam_OpenFirstCamera(ctypes.byref(self.camera)))
        Picam_OpenFirstCamera(ctypes.byref(self.camera))

    def close(self):
        """ Return shutter to normal, close camera, and uninitialize PICAM library"""

        ShutterMode = ctypes.c_int(1)  # normal
        #print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode))
        Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode)
        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        #print(Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count)))
        Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count))
        #print("Committed parameters (default shutter status)")
        #print(Picam_DestroyParameters(failed_parameters))
        Picam_DestroyParameters(failed_parameters)

        #print("Closing camera")
        Picam_CloseCamera(self.camera)
        #print("Uninitializing library")
        Picam_UninitializeLibrary()

    def configure_camera(self, T=-75.0, roi=[0,0,1024,1024,1,1], exposureTime=20, shutterMode=1):
        """ Sets 4 MHz ADC rate, temp parameter can be set as integer (Default T=-120)
        roi is a parameter that controls the region of interest:
        roi = [x,y,width,height,x_binning,y_binning]"""
        #print("Setting 4 MHz ADC rate...")
        #print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(2.0)))
        #print("Setting temp setpoint to -120C")
        #print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureSetPoint), pi32f(-120.0)))
        Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(2.0))
        Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureSetPoint), pi32f(T))

        #print("Setting trigger mode")
        # From picam.h: the enumeration of these options is:
        # PicamTriggerResponse_NoResponse               = 1,
        # PicamTriggerResponse_ReadoutPerTrigger        = 2,
        # PicamTriggerResponse_ShiftPerTrigger          = 3,
        # PicamTriggerResponse_ExposeDuringTriggerPulse = 4,
        # PicamTriggerResponse_StartOnSingleTrigger     = 5

        #TriggerResponse = ctypes.c_int(1)  # ignore trigger for now, we use ExposeMonitor as master trigger
        #print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_TriggerResponse), TriggerResponse)
        #print("Setting ROI")
        # Set ROI to x = 100:700 y = 195:205
        self.myroi.x = roi[0]
        self.myroi.y = roi[1]
        self.myroi.width = roi[2]
        self.myroi.height = roi[3]
        self.myroi.x_binning = roi[4]
        self.myroi.y_binning = roi[5]
        rois = PicamRois()
        rois.roi_array = ctypes.pointer(self.myroi)
        rois.roi_count = 1
        #print(Picam_SetParameterRoisValue(self.camera, ctypes.c_int(PicamParameter_Rois), ctypes.pointer(rois)))
        Picam_SetParameterRoisValue(self.camera, ctypes.c_int(PicamParameter_Rois), ctypes.pointer(rois))

        # Set shutter mode:
        # 1 => only opens during exposure time
        # 2 => always closed
        # 3 => always open
        # 4 => opens ahead of time while waiting for a trigger
        #ShutterMode = ctypes.c_int(3)  # always open
        #print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode))
        #ShutterInt = piint(shutterMode)
        ShutterMode = ctypes.c_int(shutterMode)
        Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode)

        # Set exposure time to 20 ms
        #print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_ExposureTime), pi32f(20)))
        Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_ExposureTime), pi32f(exposureTime))

        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count))
        #print(Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count)))
        #print("Cleaning up...")
        #print(Picam_DestroyParameters(failed_parameters))
        Picam_DestroyParameters(failed_parameters)

        #print("Getting readout stride. ", Picam_GetParameterIntegerValue( self.camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(self.readoutstride) ))
        Picam_GetParameterIntegerValue( self.camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(self.readoutstride) )

    def get_temp(self):
        temp = ctypes.c_double()
        Picam_GetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureReading), ctypes.byref(temp))
        return temp.value
        #print(Picam_GetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureReading), ctypes.byref(temp)))
        #print("Temp = %.1f" % temp.value)

    def acquire(self, N=1):
        self.readout_count = pi64s(N)
        #print(Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(self.available), ctypes.byref(self.errors)))
        Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(self.available), ctypes.byref(self.errors))

    def get_data(self):
        """ Routine to access initial data.
        Returns numpy array with shape (400,1340) """

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*self.myroi.width*self.myroi.height

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*self.myroi.width*self.myroi.height)

        """ Create an instance of the pointer type, and point it to initial readout contents (memory address?) """
        DataPointer = ctypes.cast(self.available.initial_readout,DataArrayPointerType)


        """ Create a separate array with readout contents """
        # TODO, check this stuff for slowdowns
        rawdata = DataPointer.contents
        numpydata = np.frombuffer(rawdata, dtype='uint16')
        data = np.reshape(numpydata,(self.myroi.height,self.myroi.width))  # TODO: get dimensions officially,
        # note, the readoutstride is the number of bytes in the array, not the number of elements
        # will need to be smarter about the array size, but for now it works.
        return data

    def get_all_data(self):
        """ Routine to access all data shots from multi-shot run.
        Returns numpy array with shape (x,y,shotcount)."""
        shotcount = self.available.readout_count
        stride = self.readoutstride.value

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*self.myroi.width*self.myroi.height

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*self.myroi.width*self.myroi.height)

        data = np.zeros((self.myroi.height,self.myroi.width,shotcount))

        for shot in range(shotcount):
            """ Create an instance of the pointer type, and point it to initial readout (memory address) """
            DataPointer = ctypes.cast(self.available.initial_readout + stride*shot, DataArrayPointerType)


            """ Create a separate array with readout contents """
            # TODO, check this stuff for slowdowns
            rawdata = DataPointer.contents
            numpydata = np.frombuffer(rawdata, dtype='uint16')
            data[:,:,shot] = np.reshape(numpydata,(self.myroi.height,self.myroi.width))

        return data

    def setIntegrationTime(self, exposureTime=20):
        Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_ExposureTime), pi32f(exposureTime))

    def setTemperature(self, temperature=-75.0):
        Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureSetPoint), pi32f(temperature))




###================================================================================================###
###================================================================================================###
###================================================================================================###

class Driver(InstrumentDriver.InstrumentWorker):

    """ This class implements the Ocean Optics Spectrometer"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # init object
        self.newcam = None
        try:
            # open connection
            #devices = pc.list_devices()
            # check if devices available
            #if len(devices) == 0:
                # no devices found
            #    raise Exception('No spectrometer found')
            #elif len(devices) == 1:
                # one device, use
            self.newcam = PyPICAM()
            self.newcam.configure_camera()
            #else:
                # many devices, look for serial
            #    self.spec = sb.Spectrometer.from_serial_number(self.comCfg.address)
        except Exception as e:
            # re-cast errors as a generic communication error
            raise InstrumentDriver.CommunicationError(str(e))

    def performClose(self, bError=False, options={}):
        """Perform the close instrument connection operation"""
        # check if digitizer object exists
        try:
            if self.newcam is None:
                # do nothing, object doesn't exist (probably was never opened)
                return
        except:
            # never return error here, do nothing, object doesn't exist
            return
        try:
            # close and remove object
            self.newcam.close()
            del self.newcam
        except:
            # never return error here
            pass

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""
        # check quantity
        if quant.name == 'Integration Time':
            # conversion from s -> us
            #self.newcam.set_int_time(int(value*1E3))
            self.newcam.setIntegrationTime(value)
            exposureTime = value
            self.newcam.configure_camera(exposureTime)
        elif quant.name == 'Temperature':
            # temperature set point
            self.newcam.setTemperature(value)
            Temperature = value
            self.newcam.configure_camera(Temperature)
        elif quant.name == 'Configure Camera':
            IntegrationTime = self.getValue('Integration Time')
            Temperature = self.getValue('Temperature')
            ROI_x = self.getValue('ROI X')
            ROI_x = self.getValue('ROI X')
            ROI_y = self.getValue('ROI Y')
            ROI_width = self.getValue('ROI Width')
            ROI_height = self.getValue('ROI Height')
            ROI_x_binning = self.getValue('ROI X Binning')
            ROI_y_binning = self.getValue('ROI Y Binning')
            roi = [int(ROI_x), int(ROI_y), int(ROI_width), int(ROI_height), int(ROI_x_binning), int(ROI_y_binning)]
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=1)
        return value

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        # check type of quantity
        if quant.name == 'Temperature':
            # temperature
            value = self.newcam.get_temp()
        elif quant.name == 'Intensity':
            self.newcam.acquire(N=1)
            value = self.newcam.get_data()
            value = value.mean(0)
        elif quant.name == 'Image': 
            IntegrationTime = self.getValue('Integration Time')
            Temperature = self.getValue('Temperature')
            ROI_x = self.getValue('ROI X')
            ROI_y = self.getValue('ROI Y')
            ROI_width = self.getValue('ROI Width')
            ROI_height = self.getValue('ROI Height')
            ROI_x_binning = self.getValue('ROI X Binning')
            ROI_y_binning = self.getValue('ROI Y Binning')
            roi = [int(ROI_x), int(ROI_y), int(ROI_width), int(ROI_height), int(ROI_x_binning), int(ROI_y_binning)]
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=2) #keep shutter closed
            self.newcam.acquire(N=1)
            dark_value = self.newcam.get_data()
            dark_value = dark_value+0.1 #this 0.1 is actually necessary.  idk why. -HC
            time.sleep(1)
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=1) #now open the shutter
            self.newcam.acquire(N=1)
            value = self.newcam.get_data()
            value = value+0.1 #same here...
            value = value - dark_value
            plt.imshow(value,cmap="inferno")
            plt.colorbar()
            plt.show()
            value = value.mean(0)
        elif quant.name == 'Dark Spectrum':
            IntegrationTime = self.getValue('Integration Time')
            Temperature = self.getValue('Temperature')
            ROI_x = self.getValue('ROI X')
            ROI_y = self.getValue('ROI Y')
            ROI_width = self.getValue('ROI Width')
            ROI_height = self.getValue('ROI Height')
            ROI_x_binning = self.getValue('ROI X Binning')
            ROI_y_binning = self.getValue('ROI Y Binning')
            roi = [int(ROI_x), int(ROI_y), int(ROI_width), int(ROI_height), int(ROI_x_binning), int(ROI_y_binning)]
            value = roi
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=2) #keep shutter closed
            self.newcam.acquire(N=1)
            value = self.newcam.get_data()
            value = value.mean(0)
        elif quant.name == 'Intensity Dark Corrected':
            IntegrationTime = self.getValue('Integration Time')
            Temperature = self.getValue('Temperature')
            ROI_x = self.getValue('ROI X')
            ROI_y = self.getValue('ROI Y')
            ROI_width = self.getValue('ROI Width')
            ROI_height = self.getValue('ROI Height')
            ROI_x_binning = self.getValue('ROI X Binning')
            ROI_y_binning = self.getValue('ROI Y Binning')
            roi = [int(ROI_x), int(ROI_y), int(ROI_width), int(ROI_height), int(ROI_x_binning), int(ROI_y_binning)]
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=2) #keep shutter closed
            self.newcam.acquire(N=1)
            dark_value = self.newcam.get_data()
            dark_value = dark_value.mean(0)
            time.sleep(1)
            #now acquire data
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=1) #now open the shutter
            self.newcam.acquire(N=1)
            value = self.newcam.get_data()
            value = value.mean(0) - dark_value

            vY = value
            value = quant.getTraceDict(vY, dt=0.49297, t0=502.42) #previous fit...
            #value = quant.getTraceDict(vY, dt=0.49266, t0=582.26) #2nd fit...
            #value = quant.getTraceDict(vY, dt=0.49883, t0=374.11)
            #for i in range(0, 1024):
            #    value[i] = value[i]*(3398.7/(3398.7 + 253.16*np.sin(0.002128*i - 0.012418)))
        elif quant.name == 'Configure Camera':
            IntegrationTime = self.getValue('Integration Time')
            Temperature = self.getValue('Temperature')
            ROI_x = self.getValue('ROI X')
            ROI_y = self.getValue('ROI Y')
            ROI_width = self.getValue('ROI Width')
            ROI_height = self.getValue('ROI Height')
            ROI_x_binning = self.getValue('ROI X Binning')
            ROI_y_binning = self.getValue('ROI Y Binning')
            roi = [int(ROI_x), int(ROI_y), int(ROI_width), int(ROI_height), int(ROI_x_binning), int(ROI_y_binning)]
            value = roi
            self.newcam.configure_camera(Temperature, roi, IntegrationTime, shutterMode=1)
        return value

if __name__ == '__main__':

    pass

