from ctypes import windll, wintypes, byref
from struct import unpack
from pywinauto import Application
from datetime import datetime
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

CCCASTER_PROC = "cccaster*"
MELTY_PROC = "MBAA"

meltyPid_g = 0
potatoFlag_g = False
debugLogger_g = None

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

class VLogger:
    def __init__(self, debugLevel):
        self.debugTabs = 0
        self.debugLevel = debugLevel
        self.fileHandle = None
    
    def vprint(self, s, hold=False):
        if self.debugLevel > 0:
            if self.fileHandle == None:
                self.fileHandle = open(datetime.now().strftime("RepReplay_%Y_%m_%d__%H_%M_%S.log"), "a")
            self.fileHandle.write("  "*self.debugTabs + s + "\n")
        if hold:
            input(s)
        else:
            print(s)
    
    def vtrace(self, methodName, mode=""):
        if self.debugLevel == 2:
            if mode == "enter":
                self.vprint(methodName)
                self.debugTabs += 1
            else:
                self.debugTabs -= 1
                self.vprint(methodName)

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

# dictionary of every application (name, pid)
def getPidDict():
    debugLogger_g.vtrace("getPidDict", "enter")
    
    pidDict = {
        p.info["name"]: p.info["pid"]
        for p in psutil.process_iter(attrs=["name", "pid"])
    }
    
    debugLogger_g.vtrace("getPidDict")
    
    return pidDict
    
# return the pid of an application Ex. "MBAA.exe", 
def getPid(appNameStart, appNameEnd=""):
    debugLogger_g.vtrace("getPid", "enter")
    
    returnVal = 0
    pidDict = getPidDict()
    for key, value in pidDict.items():
        if key.startswith(appNameStart) and key.endswith(appNameEnd):
            returnVal = value
            
    debugLogger_g.vtrace("getPid")
            
    return returnVal
    
def focusApp(pid):
    debugLogger_g.vtrace("focusApp", "enter")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = Application().connect(process=pid)
            app.top_window().set_focus()
    except:
        wrapup()
        
    debugLogger_g.vtrace("focusApp")
    
# melty doesn't like .send, so gotta do it manually like this
def pressKey(key):
    debugLogger_g.vtrace("pressKey", "enter")

    focusApp(meltyPid_g)
    
    debugLogger_g.vprint("Sending " + key)
    
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)
    wait(0.1)
    
    debugLogger_g.vtrace("pressKey")
    
def getParameter(obj, programHandle, baseAddress):
    debugLogger_g.vtrace("getParameter", "enter")
    
    ReadMem(programHandle, obj.address + baseAddress, obj.b_dat, len(obj.b_dat), None)
    obj.num = unpack('l', obj.b_dat.raw)[0]
    
    debugLogger_g.vtrace("getParameter")

def wrapup():
    debugLogger_g.vtrace("wrapup", "enter")
        
    try:
        cccasterPid = getPid("cccaster", ".exe")
        os.kill(cccasterPid, signal.SIGTERM)
    except:
        pass
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    debugLogger_g.vprint("Press any key to close...", True)
    
    debugLogger_g.vtrace("wrapup")
    
    sys.exit()
    
def wait(t):
    time.sleep(t + (1 if potatoFlag_g else 0))
    
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
    global meltyPid_g
    global potatoFlag_g
    global debugLogger_g
    
    debugLogger_g = VLogger(0)
    
    debugLogger_g.vtrace("main", "enter")
    
    # ensure cccaster is in the same directory
    if len([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")]) == 0:
        debugLogger_g.vprint("Move this executable into the same directory as CCCaster before launching it")
        #wrapup()
    
    # ask for a folder
    replayPath = ""
    while True:
        os.system('cls')
        debugLogger_g.vprint("Fang's Batch Replay Tool v1.2")
        debugLogger_g.vprint("1+Enter  -  cycle debug level: " + ["Regular(recommended)", "Verbose"][debugLogger_g.debugLevel])
        debugLogger_g.vprint("2+Enter  -  toggle potato mode for slow computers: " + ("On" if potatoFlag_g else "Off(recommended)"))
        debugLogger_g.vprint("When ready to begin, drag your folder of replays onto this window then press Enter")
        replayPath = input("==> ").strip("\"")
        
        if replayPath == "1":
            debugLogger_g.debugLevel = (debugLogger_g.debugLevel + 1) % 2
            continue
        if replayPath == "2":
            potatoFlag_g = not potatoFlag_g
            continue
        
        if not os.path.exists(replayPath):
            debugLogger_g.vprint("Unable to load given replay folder")
        else:
            debugLogger_g.vprint("\nFolder found.  MBAA is going to open after you press Enter again.\nAfter it opens come back to this console.", True)
            break

    # Copy given replays to CCCCaster location relpay folder in a new folder called $
    if not os.path.exists("ReplayVS"):
        os.makedirs("ReplayVS")
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    try:
        shutil.copytree(replayPath , "ReplayVS\\$")
        debugLogger_g.vprint("Replays Copied")
    except:
        debugLogger_g.vprint("Failed to copy replays")
        wrapup()
    replayTotal = len(os.listdir("ReplayVS\\$"))


    # launch cccaster
    os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])

    # wait for cccaster to open
    os.system('cls')
    debugLogger_g.vprint("Please wait for for CCCaster to open...")
    cccasterPid = 0
    while cccasterPid == 0:
        cccasterPid = getPid("cccaster", ".exe")
        wait(0.1)

    # launch replay mode
    wait(0.5)
    keyboard.write('45',delay=1)


    # wait for replay mode to launch
    os.system('cls')
    debugLogger_g.vprint("Please wait for MBAA to open...")
    while meltyPid_g == 0:
        meltyPid_g = getPid("MBAA.exe")
        wait(0.1)
          
    # give the user a pep talk
    wait(2)
    os.system('cls')
    debugLogger_g.vprint("Open your recording software of choice now")
    debugLogger_g.vprint("")
    debugLogger_g.vprint("Make sure Player 1 is not assigned to a controller in the F4 menu")
    debugLogger_g.vprint("")
    debugLogger_g.vprint("Make sure Melty is NOT in fullscreen")
    debugLogger_g.vprint("")
    debugLogger_g.vprint("To begin playback, press Enter now", True)
    os.system('cls')
    debugLogger_g.vprint("Playback has begun.  Please do wait for the replay to finish.")

    # re-focus MBAA
    focusApp(meltyPid_g)

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
    pressKey('b')
    pressKey('down')
    pressKey('down')
    pressKey('down')
    pressKey('s')
    pressKey('f4')

    # get MBAA handle from its pid
    programHandle = OpenProcess(0x1F0FFF, False, meltyPid_g)

    # snapshot MBAA
    snapshot = CreateToolhelp32Snapshot(0x00000008, meltyPid_g)

    # get the module
    lpme = MODULEENTRY32()
    lpme.dwSize = sizeof(lpme)
    Module32First(snapshot, byref(lpme))

    # probably not necessary, but won't hurt to leave
    while meltyPid_g != lpme.th32ProcessID:
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
    debugLogger_g.vprint("Total replays: " + str(replayTotal))
    for currentRep in range(replayTotal):
        pressKey('a')   # select $ folder
        pressKey('down')# get off the "go up" folder
        for i in range(currentRep):
            pressKey('down')    # go to next recording
        pressKey('a')   # select recording
        wait(1)
        pressKey('a')   # skip vs screen
        wait(0.5)
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
                debugLogger_g.vprint("Round end detected P1-" + str(p1ParaScore.num) + " P2-" + str(p2ParaScore.num))
                
                P1.oldScore = p1ParaScore.num
                P2.oldScore = p2ParaScore.num
                
                desyncCounter = 0
                
                wait(1)
                
                pressKey('b')   # skip win quote
                
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
                    debugLogger_g.vprint("Desync Detected")
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
            
            wait(0.1)
            
        # exit a finished replay
        debugLogger_g.vprint("Replay " + str(currentRep) + " finished")
        pressKey('b')   # skip game end quote
        wait(1)
        pressKey('b')   # skip closeup
        wait(1)
        pressKey('down')# highlight Replay Selection
        pressKey('a')   # select Replay Selection
        wait(1)
        
        if getPid("MBAA.exe") == 0:
            input("MBAA closed")
            break

    wrapup()

if __name__ == '__main__':
    main()