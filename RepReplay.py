from ctypes import windll, wintypes, byref
from struct import unpack
from pywinauto import Application
import os
import time
import ctypes
import psutil
import shutil
import subprocess
import keyboard
import warnings
import signal
import sys

DEBUG = True

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

# Constants.  Consider getting these dynamically in the future
CCCASTER_PROC = "cccaster*"
MELTY_PROC = "MBAA"

# dictionary of every application (name, pid)
def getPidDict():
    pidDict = {
        p.info["name"]: p.info["pid"]
        for p in psutil.process_iter(attrs=["name", "pid"])
    }
    return pidDict
    
# return the pid of an application Ex. "MBAA.exe", 
def getPid(appNameStart, appNameEnd=""):
    pidDict = getPidDict()
    for key, value in pidDict.items():
        if key.startswith(appNameStart) and key.endswith(appNameEnd):
            return value
    return 0
    
def focusApp(pid):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = Application().connect(process=pid)
            app.top_window().set_focus()
    except:
        pass
    
# melty doesn't like .send, so gotta do it manually like this
def pressKey(key):
    meltyPid = getPid("MBAA.exe")
    if meltyPid == 0:
        wrapup()
    focusApp(meltyPid)
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)
    time.sleep(0.1)
    
def getParameter(obj, programHandle, baseAddress):
    ReadMem(programHandle, obj.address + baseAddress, obj.b_dat, len(obj.b_dat), None)
    obj.num = unpack('l', obj.b_dat.raw)[0]

def wrapup():
    try:
        cccasterPid = getPid("cccaster", ".exe")
        os.kill(cccasterPid, signal.SIGTERM)
    except:
        pass
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    vprint("Press any key to close...", True)
    sys.exit()
    
def vprint(s, hold=False):
    if DEBUG:
        # I know this is inefficient
        f = open("RepRelpay.log", "a")
        f.write(s + "\n")
    if hold:
        input(s)
    else:
        print(s)
        
class Parameter:
    def __init__(self, byteLength, address):
        self.address = address
        self.num = 0
        self.b_dat = create_string_buffer(byteLength)
         
class PlayerStruct:
    def __init__(self):
        self.oldScore = 0
        self.oldX = 0
        self.oldY = 0
        self.oldHealth = 0
        self.oldMeter = 0
        self.oldScore = 0
         
def main():

    # ensure cccaster is in the same directory
    if len([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")]) == 0:
        vprint("Move this executable into the same directory as CCCaster before launching it")
        wrapup()
    
    # ask for a folder
    vprint("Click and drag your folder of replays onto this window then press Enter")
    replayPath = input("==> ").strip("\"")
    vprint(replayPath)
    if not os.path.exists(replayPath):
        vprint("Unable to load given replay folder")
        wrapup()

    # Copy given replays to CCCCaster location relpay folder in a new folder called $
    if not os.path.exists("ReplayVS"):
        os.makedirs("ReplayVS")
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    try:
        shutil.copytree(replayPath , "ReplayVS\\$")
        vprint("Replays Copied")
    except:
        vprint("Failed to copy replays")
        wrapup()
    replayTotal = len(os.listdir("ReplayVS\\$"))


    # launch cccaster
    os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])

    # wait for cccaster to open
    os.system('cls')
    vprint("Please wait for for CCCaster to open...")
    cccasterPid = 0
    while cccasterPid == 0:
        cccasterPid = getPid("cccaster", ".exe")
        time.sleep(0.1)

    # launch replay mode
    time.sleep(0.5)
    keyboard.write('45',delay=1)


    # wait for replay mode to launch
    os.system('cls')
    vprint("Please wait for MBAA to open...")
    meltyPid = 0
    while meltyPid == 0:
        meltyPid = getPid("MBAA.exe")
        time.sleep(0.1)
          
    # give the user a pep talk
    time.sleep(2)
    os.system('cls')
    vprint("Open your recording software of choice now")
    vprint("")
    vprint("Make sure Player 1 is not assigned to a controller in the F4 menu")
    vprint("")
    vprint("Make sure Melty is NOT in fullscreen")
    vprint("")
    vprint("To begin playback, press Enter now", True)
    os.system('cls')
    vprint("Playback has begun.  Please do wait for the replay to finish.")

    # re-focus MBAA
    focusApp(meltyPid)

    # change the controls
    pressKey('f4')
    pressKey('left')
    pressKey('left')
    pressKey('down')
    pressKey('down')
    pressKey('enter')
    pressKey('down')
    pressKey('esc')
    pressKey('down')
    pressKey('down')
    pressKey('a')
    pressKey('down')
    pressKey('down')
    pressKey('down')
    pressKey('down')
    pressKey('s')
    pressKey('f4')

    # get MBAA handle from its pid
    programHandle = OpenProcess(0x1F0FFF, False, meltyPid)

    # snapshot MBAA
    snapshot = CreateToolhelp32Snapshot(0x00000008, meltyPid)

    # get the module
    lpme = MODULEENTRY32()
    lpme.dwSize = sizeof(lpme)
    Module32First(snapshot, byref(lpme))

    # probably not necessary, but won't hurt to leave
    while meltyPid != lpme.th32ProcessID:
        Module32Next(snapshot, byref(lpme))

    # get the base address of MBAA in memory
    b_baseAddr = create_string_buffer(8)
    b_baseAddr.raw = lpme.modBaseAddr
    baseAddress = unpack('q', b_baseAddr.raw)[0]

    # Player 1 parameters
    p1ParaScore = Parameter(4, 0x159550)
    p1ParaX = Parameter(4, 0x155140 + 0xF8)
    p1ParaY = Parameter(4, 0x155248)
    p1ParaHealth = Parameter(4, 0x1551EC)
    p1ParaMeter = Parameter(4, 0x155210)

    # Player 2 parameters
    p2ParaScore = Parameter(4, 0x159580)
    p2ParaX = Parameter(4, 0x155140 + 0xF8 + 0xAFC)
    p2ParaY = Parameter(4, 0x155248 + 0xAFC)
    p2ParaHealth = Parameter(4, 0x1551EC + 0xAFC)
    p2ParaMeter = Parameter(4, 0x155210 + 0xAFC)

    DESYNC_THRESHOLD = 30

    # navigate the replay menu
    vprint("Total replays: " + str(replayTotal))
    for currentRep in range(replayTotal):
        pressKey('a')   # select $ folder
        pressKey('down')# get off the "go up" folder
        for i in range(currentRep):
            pressKey('down')    # go to next recording
        pressKey('a')   # select recording
        time.sleep(1)
        pressKey('a')   # skip vs screen
        time.sleep(0.5)
        pressKey('a')   # skip intro quote

        # initialize tracking variables.  these are used for detecting desyncs
        P1 = PlayerStruct()
        P2 = PlayerStruct()
        desyncCounter = 0
        
        # get these fresh to avoid carry-over values from the last recording
        getParameter(p1ParaScore, programHandle, baseAddress)
        getParameter(p2ParaScore, programHandle, baseAddress)
        
        # the game starts
        while p1ParaScore.num != 2 and p2ParaScore.num != 2:
            
            # bail if melty is closed
            if getPid("MBAA.exe") == 0:
                wrapup()
        
            getParameter(p1ParaScore, programHandle, baseAddress)
            getParameter(p2ParaScore, programHandle, baseAddress)
            
            # detect a round ending
            if P1.oldScore != p1ParaScore.num or P2.oldScore != p2ParaScore.num:
                vprint("Round end detected P1-" + str(p1ParaScore.num) + " P2-" + str(p2ParaScore.num))
                
                P1.oldScore = p1ParaScore.num
                P2.oldScore = p2ParaScore.num
                
                desyncCounter = 0
                
                time.sleep(1)
                
                pressKey('a')   # skip win quote
                
            # monitor player positions, health, and meter to detect a desync
            # default threshold for a desync is 3 seconds with no change
            getParameter(p1ParaX, programHandle, baseAddress)
            getParameter(p1ParaY, programHandle, baseAddress)
            getParameter(p1ParaHealth, programHandle, baseAddress)
            getParameter(p1ParaMeter, programHandle, baseAddress)
            getParameter(p2ParaX, programHandle, baseAddress)
            getParameter(p2ParaY, programHandle, baseAddress)
            getParameter(p2ParaHealth, programHandle, baseAddress)
            getParameter(p2ParaMeter, programHandle, baseAddress)
            if (P1.oldX != p1ParaX.num or P2.oldX != p2ParaX.num or
                P1.oldY != p1ParaY.num or P2.oldY != p2ParaY.num or
                P1.oldHealth != p1ParaHealth.num or P2.oldHealth != p2ParaHealth.num or
                P1.oldMeter != p1ParaMeter.num or P2.oldMeter != p2ParaMeter.num):
                desyncCounter = 0    
            else:
                desyncCounter += 1
                if desyncCounter == DESYNC_THRESHOLD:
                    vprint("Desync Detected")
                    if (p1ParaHealth.num > p2ParaHealth.num and p1ParaScore == 1) or (p2ParaHealth.num > p1ParaHealth.num and p2ParaScore == 1):
                        pressKey('s')       # pause
                        pressKey('down')
                        pressKey('down')
                        pressKey('down')
                        pressKey('down')
                        pressKey('down')
                        pressKey('a')       # return to replay selection
                        pressKey('down')
                        pressKey('a')       # confirm
                    else:
                        pressKey('s')       # pause
                        pressKey('down')
                        pressKey('down')
                        pressKey('down')
                        pressKey('down')
                        pressKey('a')       # next round
                
            P1.oldX = p1ParaX.num
            P1.oldY = p1ParaY.num
            P1.oldHealth = p1ParaHealth.num
            P1.oldMeter = p1ParaMeter.num
            P2.oldX = p2ParaX.num
            P2.oldY = p2ParaY.num
            P2.oldHealth = p2ParaHealth.num
            P2.oldMeter = p2ParaMeter.num
            
            time.sleep(0.1)
            
        # exit a finished replay
        vprint("Replay " + str(currentRep) + " finished")
        pressKey('a')   # skip game end quote
        pressKey('down')# highlight Replay Selection
        pressKey('a')   # select Replay Selection
        time.sleep(1)
        
        if getPid("MBAA.exe") == 0:
            input("MBAA closed")
            break

    wrapup()

if __name__ == '__main__':
    main()