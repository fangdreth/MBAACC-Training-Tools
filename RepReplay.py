from ctypes import windll, wintypes, byref
from struct import unpack, pack
import os
import time
import copy
import ctypes
#import keyboard
import psutil
import math

import cfg_cc
import ad_cc
import save_cc
cfg = cfg_cc
ad = ad_cc
save = save_cc

wintypes = ctypes.wintypes
windll = ctypes.windll
create_string_buffer = ctypes.create_string_buffer
byref = ctypes.byref
WriteMem = windll.kernel32.WriteProcessMemory
ReadMem = windll.kernel32.ReadProcessMemory
OpenProcess = windll.kernel32.OpenProcess
Module32Next = windll.kernel32.Module32Next
Module32First = windll.kernel32.Module32First
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
CloseHandle = windll.kernel32.CloseHandle
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

pid = 0
while pid == 0:
    dict_pids = pidget()
    try:
        pid = dict_pids["MBAA.exe"]
    except:
        os.system('cls')
        print("Waiting for MBAA to start")
        time.sleep(0.2)

h_pro = OpenProcess(0x1F0FFF, False, pid)

snapshot = CreateToolhelp32Snapshot(0x00000008, pid)

lpme = MODULEENTRY32()
lpme.dwSize = sizeof(lpme)

res = Module32First(snapshot, byref(lpme))

while pid != lpme.th32ProcessID:
    res = Module32Next(snapshot, byref(lpme))

b_baseAddr = create_string_buffer(8)
b_baseAddr.raw = lpme.modBaseAddr

base_ad = unpack('q', b_baseAddr.raw)[0]


def b_unpack(d_obj):
    num = 0
    num = len(d_obj)
    print("len(d_obj) " + str(num))
    print("d_obj.raw " + str(d_obj.raw))
    if num == 1:
        return unpack('b', d_obj.raw)[0]
    elif num == 2:
        return unpack('h', d_obj.raw)[0]
    elif num == 4:
        return unpack('l', d_obj.raw)[0]

def r_mem(ad, b_obj):
    ReadMem(cfg.h_pro, ad + cfg.base_ad, b_obj, len(b_obj), None)
    return b_unpack(b_obj)

def para_get(obj):
    obj.num = r_mem(obj.ad, obj.b_dat)

class para:
    def __init__(self, byte_len):
        self.ad = 0x00
        self.num = 0
        self.b_dat = create_string_buffer(byte_len)
        
p1Para = para(4)
p1Para.ad = 0x559550

print("wow you didn't DIE")

while True:
    para_get(p1Para)

    #print(p1Para.num)
    #print(p1Para.b_dat)
    #print(str(p1Para.num).rjust(6, " "))
    print("-")
    time.sleep(0.01)
    break