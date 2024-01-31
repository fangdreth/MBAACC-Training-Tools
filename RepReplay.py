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
framestepFlag_g = False
screenSizeEnum_g = 0  # 0=unchanged 1=640x480 2=1280x960 3=1920x1440
debugLogger_g = None
desyncThreshold_g = 60   # roughly 3 seconds

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

    debugLogger_g.vprint("Sending " + key)

    focusApp(meltyPid_g)
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)
    wait(0.2)
    
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
    sleepTime = t + (1 if potatoFlag_g else 0)
    debugLogger_g.vprint("Waiting for: " + str(sleepTime))
    time.sleep(sleepTime)
    
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
    def toString(self):
        return "Score:"+str(self.oldScore)+" X:"+str(self.oldX)+" Y:"+str(self.oldY)+" Health:"+str(self.oldHealth)+" Meter:"+str(self.oldMeter)
    
def main():

    # I know some of these don't need to be global, but I like putting them like this anyway
    global meltyPid_g
    global potatoFlag_g
    global framestepFlag_g
    global debugLogger_g
    global screenSizeEnum_g
    global desyncThreshold_g
    
    debugLogger_g = VLogger(0)
    
    debugLogger_g.vtrace("main", "enter")
    
    # ensure cccaster is in the same directory
    if len([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")]) == 0:
        debugLogger_g.vprint("Move this executable into the same directory as CCCaster before launching it")
        #wrapup()
    
    # ask for a folder
    replayPath = ""
    desyncLevel = 0
    while True:
        os.system('cls')
        debugLogger_g.vprint("Fang's Batch Replay Tool v1.3")
        debugLogger_g.vprint("1+Enter  -  debug level: " + ["Regular(recommended)", "Verbose", "Trace"][debugLogger_g.debugLevel])
        debugLogger_g.vprint("2+Enter  -  desync detection level: " + ["Regular(recommended)", "Lax", "Very Lax", "Off"][desyncLevel])
        debugLogger_g.vprint("3+Enter  -  potato mode for slow computers: " + ("On" if potatoFlag_g else "Off(recommended)"))
        debugLogger_g.vprint("4+Enter  -  framestep mode (skip the f4 menu): " + ("On" if framestepFlag_g else "Off(recommended)"))
        debugLogger_g.vprint("--")
        debugLogger_g.vprint("5+Enter  -  open MBAA.exe to change the screen size. use 640x480, 1280x960, or 1920x1440 for framestep.")
        debugLogger_g.vprint("            Tip: Select your screen size in the drop down, then CLOSE mbaa.exe instead of clicking \"Ok\"")
        debugLogger_g.vprint("6+Enter  -  pre-configure controls. useful for framestep mode")
        debugLogger_g.vprint("\nWhen ready to begin, drag your folder of replays onto this window then press Enter")
        replayPath = input("==> ").strip("\"")
        
        if replayPath == "1":
            debugLogger_g.debugLevel = (debugLogger_g.debugLevel + 1) % 3
            continue
        if replayPath == "2":
            desyncLevel = (desyncLevel + 1) % 4
            if desyncLevel == 3:
                desyncThreshold_g = 9999
            else:
                desyncThreshold_g = 60 + 30 * desyncLevel
            continue
        if replayPath == "3":
            potatoFlag_g = not potatoFlag_g
            continue
        if replayPath == "4":
            framestepFlag_g = not framestepFlag_g
            continue
        if replayPath.lower() == "5":
            os.system('cls')
            os.startfile("MBAA.exe")
            
            # wait for MBAA to open
            mbaaPid = 0
            while mbaaPid == 0:
                mbaaPid = getPid("MBAA.exe")
                wait(0.1)
                
            # wait for MBAA to close
            while mbaaPid != 0:
                if getPid("MBAA.exe") == 0:
                    break
        
            continue
            
        if replayPath.lower() == "6":
            os.system('cls')
            
            # launch cccaster
            os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])

            # wait for cccaster to open
            os.system('cls')
            debugLogger_g.vprint("Please wait for CCCaster to open...")
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
          
            wait(5)
            pressKey('f4')
            pressKey('left')
            pressKey('left')
            pressKey('down')
            pressKey('enter')
            pressKey('8')
            pressKey('2')
            pressKey('esc')
            pressKey('down')
            pressKey('down')
            pressKey('4')
            pressKey('6')
            pressKey('down')
            pressKey('down')
            pressKey('down')
            pressKey('5')
            pressKey('f4')
            
            subprocess.call("TASKKILL /F /PID " + str(cccasterPid), shell=True)
        
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
    debugLogger_g.vprint("Please wait for CCCaster to open...")
    cccasterPid = 0
    while cccasterPid == 0:
        cccasterPid = getPid("cccaster", ".exe")
        wait(0.1)

    # open in framestep mode if it was chosen
    if framestepFlag_g:
        keyboard.press('f8')

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
    
    keyboard.release('f8')

    # change the controls
    if not framestepFlag_g:
        pressKey('f4')
        pressKey('left')
        pressKey('left')
        pressKey('down')
        pressKey('enter')
        pressKey('8')
        pressKey('2')
        pressKey('esc')
        pressKey('down')
        pressKey('down')
        pressKey('4')
        pressKey('6')
        pressKey('down')
        pressKey('down')
        pressKey('down')
        pressKey('5')
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
    
    paraRoundCount = Parameter(4, 0x14CFE4)

    # navigate the replay menu
    debugLogger_g.vprint("Total replays: " + str(replayTotal))
    for currentRep in range(replayTotal):
        debugLogger_g.vprint("Starting Replay: " + str(currentRep+1))
        wait(1)         # nice healthy wait for slower computers
        pressKey('4')   # select $ folder
        wait(0.2)
        pressKey('2')# get off the "go up" folder
        for i in range(currentRep):
            pressKey('2')    # go to next recording
        pressKey('4')   # select recording
        wait(1)
        pressKey('4')   # skip vs screen
        wait(0.5)
        pressKey('4')   # skip intro quote

        # initialize tracking variables.  these are used for detecting desyncs
        P1 = PlayerStruct()
        P2 = PlayerStruct()
        desyncCounter = 0
        
        # get these fresh to avoid carry-over values from the last recording
        getParameter(p1ParaScore, programHandle, baseAddress)
        getParameter(p2ParaScore, programHandle, baseAddress)
        
        # need to keep this for certain desync scenarios
        leaveEarlyFlag = False
        
        # the game starts
        while p1ParaScore.num != 2 and p2ParaScore.num != 2 and not leaveEarlyFlag:
            
            #Cap at 30hz
            time.sleep(0.033)
            
            getParameter(p1ParaScore, programHandle, baseAddress)
            getParameter(p2ParaScore, programHandle, baseAddress)
            
            # detect a round ending
            if P1.oldScore != p1ParaScore.num or P2.oldScore != p2ParaScore.num:
                debugLogger_g.vprint("Round end detected P1-" + str(p1ParaScore.num) + " P2-" + str(p2ParaScore.num))
                
                P1.oldScore = p1ParaScore.num
                P2.oldScore = p2ParaScore.num
                
                desyncCounter = 0
                
                wait(1)
                pressKey('6')   # skip win quote
                
            # monitor player positions, health, and meter to detect a desync
            getParameter(p1ParaX, programHandle, baseAddress)
            getParameter(p1ParaY, programHandle, baseAddress)
            getParameter(p1ParaHealth, programHandle, baseAddress)
            getParameter(p1ParaMeter, programHandle, baseAddress)
            getParameter(p2ParaX, programHandle, baseAddress)
            getParameter(p2ParaY, programHandle, baseAddress)
            getParameter(p2ParaHealth, programHandle, baseAddress)
            getParameter(p2ParaMeter, programHandle, baseAddress)
            if (P1.oldX == p1ParaX.num and P2.oldX == p2ParaX.num and P1.oldY == p1ParaY.num and P2.oldY == p2ParaY.num and P1.oldHealth == p1ParaHealth.num and P2.oldHealth == p2ParaHealth.num and P1.oldMeter == p1ParaMeter.num and P2.oldMeter == p2ParaMeter.num):
                desyncCounter += 1
                if desyncCounter % 10 == 0 and desyncCounter != 0:
                    debugLogger_g.vprint("Desync Counter " + str(desyncCounter) + "/" + str(desyncThreshold_g))
                    debugLogger_g.vprint("P1-"+P1.toString()+" P2-"+P2.toString())
                if desyncCounter == desyncThreshold_g:
                    debugLogger_g.vprint("Desync or Disconnect Detected")
                    if getPid("MBAA.exe") == 0:
                        wrapup()
                    getParameter(paraRoundCount, programHandle, baseAddress)
                    if paraRoundCount.num == 1:
                        pressKey('5')       # pause
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('4')       # next round
                    # final round or the health 
                    elif paraRoundCount.num == 3:
                        pressKey('5')       # pause
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('4')       # return to replay selection
                        time.sleep(0.2)
                        pressKey('2')
                        pressKey('4')       # confirm
                        break;
                    else:   # round count is 2.  this one is ugly
                        # this is sadly the only known way to cover a specific edge case
                        # where the game desyncs, but the player with less life wins anyway
                        pressKey('5')
                        for upIndex in range(7):
                            pressKey('8')      # go to next recording
                        pressKey('4')           # open command menu OR press continue
                        pressKey('6')           # close command menu if open
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')        # go down to Next if menu is still open
                        pressKey('4')           # press Next if menu is still open
                        
                        # check if this was a 2-round match
                        # i.e. see if we are back on the replay select menu or not
                        time.sleep(1)
                        getParameter(paraRoundCount, programHandle, baseAddress)
                        if paraRoundCount.num == 2:
                            debugLogger_g.vprint("Desync edge case detected B)")
                            pressKey('5')           # if Next was not pressed, open Start again
                            pressKey('8')
                            pressKey('8')          # go down to Return
                            pressKey('4')           # press Return
                            time.sleep(0.2)
                            pressKey('2')        # select confirm
                            pressKey('4')           # confirm
                            leaveEarlyFlag = True
                        
            else:
                desyncCounter = 0
                
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
        if desyncCounter < desyncThreshold_g:
            pressKey('6')   # skip game end quote
            wait(1)
            pressKey('6')   # skip closeup
            wait(1)
            pressKey('2')# highlight Replay Selection
            pressKey('4')   # select Replay Selection
            wait(1.5)
        else:
            wait(4)
        
        # I am disabling this until I understand why
        # it causes so much slowdown
        #if getPid("MBAA.exe") == 0:
        #    input("MBAA closed")
        #    break

    wrapup()

if __name__ == '__main__':
    main()