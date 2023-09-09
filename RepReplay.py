from ctypes import windll, wintypes, byref
from struct import unpack
import os
import time
import ctypes
import psutil
import subprocess
import keyboard

wintypes = ctypes.wintypes
windll = ctypes.windll
create_string_buffer = ctypes.create_string_buffer
byref = ctypes.byref
ReadMem = windll.kernel32.ReadProcessMemory
OpenProcess = windll.kernel32.OpenProcess
Module32Next = windll.kernel32.Module32Next
Module32First = windll.kernel32.Module32First
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
sizeof = ctypes.sizeof

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",             wintypes.DWORD),
        ("th32ModuleID",       wintypes.DWORD),
        ("th32ProcessID",      wintypes.DWORD),
        ("GlblcntUsage",       wintypes.DWORD),
        ("ProccntUsage",       wintypes.DWORD),
        ("modBaseAddr",        ctypes.POINTER(wintypes.BYTE)),
        ("modBaseSize",        wintypes.DWORD),
        ("hModule",            wintypes.HMODULE),
        ("szModule",           ctypes.c_byte * 256),
        ("szExePath",          ctypes.c_byte * 260),
    ]

def pidget():
    dict_pids = {
        p.info["name"]: p.info["pid"]
        for p in psutil.process_iter(attrs=["name", "pid"])
    }
    return dict_pids
    
def pressKey(key):
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)


CCCASTER_PATH = "C:\\Users\\willf\\WH\\MBAACC - Community Edition\\MBAACC"
CCCASTER_PROC = "cccaster*"
MELTY_PROC = "MBAA"

currentDir = os.getcwd()
os.chdir(CCCASTER_PATH)
os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])
os.chdir(currentDir)

cccasterPid = 0
while cccasterPid == 0:
    dict_pids = pidget()
    for key, value in dict_pids.items():
        if key.startswith("cccaster") and key.endswith(".exe"):
            cccasterPid = value
            break
    print("Waiting for CCCaster to open...")
    time.sleep(0.2)
    
keyboard.write('45',delay=1)

meltyPid = 0
while meltyPid == 0:
    dict_pids = pidget()
    for key, value in dict_pids.items():
        if key == "MBAA.exe":
            meltyPid = value
            break
    print("Waiting for MBAA to open...")
    time.sleep(0.2)
      
time.sleep(5)
pressKey('f4')
pressKey('left')
pressKey('left')
pressKey('down')
pressKey('down')
pressKey('down')
pressKey('down')
pressKey('down')
pressKey('a')
pressKey('down')
pressKey('b')
pressKey('f4')

repTotal = len(os.listdir("Reps"))

print("Open your recording software of choice now")
input("To begin playback, press Enter")

keyboard.write('f4')

#meltyPid = 0
#while meltyPid == 0:
#    dict_pids = pidget()
#    try:
#        meltyPid = dict_pids["MBAA.exe"]
 #   except:
#        #os.system('cls')
 #       print("Waiting for MBAA to start")
#        time.sleep(0.2)

programHandle = OpenProcess(0x1F0FFF, False, meltyPid)

snapshot = CreateToolhelp32Snapshot(0x00000008, meltyPid)

lpme = MODULEENTRY32()
lpme.dwSize = sizeof(lpme)

result = Module32First(snapshot, byref(lpme))

# not going into this because Module32First is working fine
while meltyPid != lpme.th32ProcessID:
    result = Module32Next(snapshot, byref(lpme))

b_baseAddr = create_string_buffer(8)
b_baseAddr.raw = lpme.modBaseAddr

base_ad = unpack('q', b_baseAddr.raw)[0]


def b_unpack(d_obj):
    num = 0
    num = len(d_obj)
    if num == 1:
        return unpack('b', d_obj.raw)[0]
    elif num == 2:
        return unpack('h', d_obj.raw)[0]
    elif num == 4:
        return unpack('l', d_obj.raw)[0]

def r_mem(ad, b_obj):
    ReadMem(programHandle, ad + base_ad, b_obj, len(b_obj), None)
    return b_unpack(b_obj)

def para_get(obj):
    obj.num = r_mem(obj.ad, obj.b_dat)

class para:
    def __init__(self, byte_len):
        self.ad = 0x00
        self.num = 0
        self.b_dat = create_string_buffer(byte_len)
        
p1Para = para(4)
p1Para.ad = 0x159550

p2Para = para(4)
p2Para.ad = 0x159580

#subprocess.run(["powershell", "-Command", ".\LaunchFrameStep.ps1"], capture_output=True)
#subprocess.run(["powershell", "-Command", ".\CCCasterAdapter.ps1 -mode \"41\" -slot \"1\""], capture_output=True)

while p1Para.num != 2:
    print(p1Para.num)
    para_get(p1Para)
    
    time.sleep(0.1)
print("game over p1 won")