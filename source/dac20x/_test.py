import ctypes, time
from ctypes import byref, create_string_buffer

# -----------------------------------------------------------------------------
# Load VISA
# -----------------------------------------------------------------------------
try:
    visa = ctypes.WinDLL("visa64.dll")
except OSError:
    visa = ctypes.WinDLL("visa32.dll")

# -----------------------------------------------------------------------------
# VISA types
# -----------------------------------------------------------------------------
ViStatus = ctypes.c_int32
ViObject = ctypes.c_uint32
ViSession = ctypes.c_uint32
ViAttr = ctypes.c_uint32
ViAttrState = ctypes.c_uint64
ViUInt16 = ctypes.c_uint16
ViUInt32 = ctypes.c_uint32
ViUInt8 = ctypes.c_ubyte

# -----------------------------------------------------------------------------
# Function prototypes
# -----------------------------------------------------------------------------
visa.viOpenDefaultRM.restype = ViStatus
visa.viOpenDefaultRM.argtypes = [ctypes.POINTER(ViSession)]

visa.viParseRsrc.restype = ViStatus
visa.viParseRsrc.argtypes = [
    ViSession,
    ctypes.c_char_p,
    ctypes.POINTER(ViUInt16),
    ctypes.POINTER(ViUInt16),
]

visa.viOpen.restype = ViStatus
visa.viOpen.argtypes = [
    ViSession,
    ctypes.c_char_p,
    ViUInt32,
    ViUInt32,
    ctypes.POINTER(ViSession),
]

visa.viGetAttribute.restype = ViStatus
visa.viGetAttribute.argtypes = [ViObject, ViAttr, ctypes.c_void_p]

visa.viSetAttribute.restype = ViStatus
visa.viSetAttribute.argtypes = [ViObject, ViAttr, ViAttrState]

visa.viWrite.restype = ViStatus
visa.viWrite.argtypes = [
    ViObject,
    ctypes.c_char_p,
    ViUInt32,
    ctypes.POINTER(ViUInt32),
]

visa.viRead.restype = ViStatus
visa.viRead.argtypes = [
    ViObject,
    ctypes.c_void_p,
    ViUInt32,
    ctypes.POINTER(ViUInt32),
]

visa.viClose.restype = ViStatus
visa.viClose.argtypes = [ViObject]

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
RSRC = b"ASRL4::INSTR"

VI_ATTR_RSRC_CLASS        = 0xBFFF0001
VI_ATTR_RSRC_NAME         = 0xBFFF0002   # FIXED
VI_ATTR_INTF_TYPE         = 0x3FFF0171
VI_ATTR_INTF_NUM          = 0x3FFF0176
VI_ATTR_ASRL_BAUD         = 0x3FFF0021
VI_ATTR_ASRL_DATA_BITS    = 0x3FFF0022
VI_ATTR_ASRL_PARITY       = 0x3FFF0023
VI_ATTR_ASRL_STOP_BITS    = 0x3FFF0024
VI_ATTR_ASRL_FLOW_CNTRL   = 0x3FFF0025
VI_ATTR_SEND_END_EN       = 0x3FFF0016
VI_ATTR_SUPPRESS_END_EN   = 0x3FFF0036
VI_ATTR_TMO_VALUE         = 0x3FFF001A
VI_ATTR_TERMCHAR          = 0x3FFF0018
VI_ATTR_TERMCHAR_EN       = 0x3FFF0038
VI_ATTR_IO_PROT           = 0x3FFF001C
VI_ATTR_ASRL_XON_CHAR     = 0x3FFF00C1
VI_ATTR_ASRL_XOFF_CHAR    = 0x3FFF00C2
VI_ATTR_ASRL_CTS_STATE    = 0x3FFF00AE
VI_ATTR_ASRL_DSR_STATE    = 0x3FFF00B1
VI_ATTR_ASRL_DTR_STATE    = 0x3FFF00B2
VI_ATTR_ASRL_END_IN       = 0x3FFF00B3
VI_ATTR_ASRL_END_OUT      = 0x3FFF00B4
VI_ATTR_ASRL_REPLACE_CHAR = 0x3FFF00BE
VI_ATTR_ASRL_RTS_STATE    = 0x3FFF00C0   # FIXED

VI_TRUE = 1
VI_FALSE = 0
VI_ERROR_TMO = 0xBFFF0015

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def status_hex(status):
    return f"0x{ctypes.c_uint32(status).value:08X}"

def check(name, status, allow_timeout=False):
    u = ctypes.c_uint32(status).value
    if status < 0:
        if allow_timeout and u == VI_ERROR_TMO:
            print(f"{name} -> {status_hex(status)} (timeout)")
            return
        raise RuntimeError(f"{name} failed with {status_hex(status)}")
    print(f"{name} -> {status_hex(status)}")

def get_attr_str(instr, attr, name, size=256):
    buf = create_string_buffer(size)
    st = visa.viGetAttribute(instr, attr, ctypes.cast(buf, ctypes.c_void_p))
    check(f"viGetAttribute({name})", st)
    print(f"    {name} = {buf.value.decode(errors='replace')!r}")
    return buf.value

def get_attr_u32(instr, attr, name):
    val = ViUInt32()
    st = visa.viGetAttribute(instr, attr, ctypes.cast(byref(val), ctypes.c_void_p))
    check(f"viGetAttribute({name})", st)
    print(f"    {name} = {val.value} (0x{val.value:X})")
    return val.value

def get_attr_u16(instr, attr, name):
    val = ViUInt16()
    st = visa.viGetAttribute(instr, attr, ctypes.cast(byref(val), ctypes.c_void_p))
    check(f"viGetAttribute({name})", st)
    print(f"    {name} = {val.value} (0x{val.value:X})")
    return val.value

def get_attr_u8(instr, attr, name):
    val = ViUInt8()
    st = visa.viGetAttribute(instr, attr, ctypes.cast(byref(val), ctypes.c_void_p))
    check(f"viGetAttribute({name})", st)
    print(f"    {name} = {val.value} (0x{val.value:X})")
    return val.value

def set_attr(instr, attr, value, name):
    st = visa.viSetAttribute(instr, attr, ViAttrState(value))
    check(f"viSetAttribute({name}, {value})", st)
    time.sleep(0.1)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    rm = ViSession()
    intf_type = ViUInt16()
    intf_num = ViUInt16()
    instr = ViSession()

    st = visa.viOpenDefaultRM(byref(rm))
    check("viOpenDefaultRM", st)

    st = visa.viParseRsrc(rm, RSRC, byref(intf_type), byref(intf_num))
    check("viParseRsrc", st)
    print(f"    intf_type = {intf_type.value} (0x{intf_type.value:X})")
    print(f"    intf_num  = {intf_num.value} (0x{intf_num.value:X})")

    st = visa.viOpen(rm, RSRC, 0, 0, byref(instr))
    check("viOpen", st)

    # Trace-like order
    get_attr_str(instr, VI_ATTR_RSRC_NAME,         "VI_ATTR_RSRC_NAME")
    get_attr_u16(instr, VI_ATTR_INTF_TYPE,         "VI_ATTR_INTF_TYPE")
    get_attr_u16(instr, VI_ATTR_INTF_NUM,          "VI_ATTR_INTF_NUM")
    get_attr_str(instr, VI_ATTR_RSRC_CLASS,        "VI_ATTR_RSRC_CLASS")
    get_attr_str(instr, VI_ATTR_RSRC_NAME,         "VI_ATTR_RSRC_NAME")
    get_attr_u32(instr, VI_ATTR_ASRL_BAUD,         "VI_ATTR_ASRL_BAUD")
    get_attr_u16(instr, VI_ATTR_ASRL_DATA_BITS,    "VI_ATTR_ASRL_DATA_BITS")
    get_attr_u16(instr, VI_ATTR_ASRL_STOP_BITS,    "VI_ATTR_ASRL_STOP_BITS")
    get_attr_u16(instr, VI_ATTR_ASRL_PARITY,       "VI_ATTR_ASRL_PARITY")
    get_attr_u16(instr, VI_ATTR_SEND_END_EN,       "VI_ATTR_SEND_END_EN")
    get_attr_u16(instr, VI_ATTR_SUPPRESS_END_EN,   "VI_ATTR_SUPPRESS_END_EN")
    get_attr_u32(instr, VI_ATTR_TMO_VALUE,         "VI_ATTR_TMO_VALUE")
    get_attr_u16(instr, VI_ATTR_TERMCHAR_EN,       "VI_ATTR_TERMCHAR_EN")
    get_attr_u8(instr,  VI_ATTR_TERMCHAR,          "VI_ATTR_TERMCHAR")
    get_attr_u16(instr, VI_ATTR_ASRL_END_IN,       "VI_ATTR_ASRL_END_IN")
    get_attr_u16(instr, VI_ATTR_ASRL_END_OUT,      "VI_ATTR_ASRL_END_OUT")
    get_attr_u8(instr,  VI_ATTR_ASRL_REPLACE_CHAR, "VI_ATTR_ASRL_REPLACE_CHAR")
    get_attr_u16(instr, VI_ATTR_IO_PROT,           "VI_ATTR_IO_PROT")
    get_attr_u16(instr, VI_ATTR_ASRL_FLOW_CNTRL,   "VI_ATTR_ASRL_FLOW_CNTRL")
    get_attr_u8(instr,  VI_ATTR_ASRL_XON_CHAR,     "VI_ATTR_ASRL_XON_CHAR")
    get_attr_u8(instr,  VI_ATTR_ASRL_XOFF_CHAR,    "VI_ATTR_ASRL_XOFF_CHAR")
    get_attr_u16(instr, VI_ATTR_ASRL_RTS_STATE,    "VI_ATTR_ASRL_RTS_STATE")
    get_attr_u16(instr, VI_ATTR_ASRL_CTS_STATE,    "VI_ATTR_ASRL_CTS_STATE")
    get_attr_u16(instr, VI_ATTR_ASRL_DTR_STATE,    "VI_ATTR_ASRL_DTR_STATE")
    get_attr_u16(instr, VI_ATTR_ASRL_DSR_STATE,    "VI_ATTR_ASRL_DSR_STATE")

    set_attr(instr, VI_ATTR_ASRL_END_OUT, 2,       "VI_ATTR_ASRL_END_OUT")
    set_attr(instr, VI_ATTR_TERMCHAR_EN, VI_TRUE,  "VI_ATTR_TERMCHAR_EN")
    set_attr(instr, VI_ATTR_TERMCHAR_EN, VI_TRUE,  "VI_ATTR_TERMCHAR_EN")
    set_attr(instr, VI_ATTR_TERMCHAR,    13,       "VI_ATTR_TERMCHAR")
    set_attr(instr, VI_ATTR_TERMCHAR,    13,       "VI_ATTR_TERMCHAR")

    tx = b"SET,3,0"
    written = ViUInt32()
    st = visa.viWrite(instr, tx, len(tx), byref(written))
    check("viWrite", st)
    print(f"    wrote {written.value} bytes: {tx!r}")

    rx = create_string_buffer(1024)
    count = ViUInt32()
    st = visa.viRead(instr, ctypes.cast(rx, ctypes.c_void_p), 1024, byref(count))
    if ctypes.c_uint32(st).value == VI_ERROR_TMO:
        print(f"viRead -> {status_hex(st)} (timeout), bytes read = {count.value}")
    else:
        check("viRead", st)
        print(f"    read {count.value} bytes: {rx.raw[:count.value]!r}")

    visa.viClose(instr)
    visa.viClose(rm)

if __name__ == "__main__":
    main()
