from ctypes import windll, wintypes, byref
from struct import unpack
from pywinauto import Application
from datetime import datetime
from pathlib import Path
from getpass import getpass
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
import obsws_python
import requests
import webbrowser

CCCASTER_PROC = "cccaster*"
MELTY_PROC = "MBAA"
VERSION = "v1.8"
GITHUB_LATEST = "https://api.github.com/repos/fangdreth/MBAACC-Training-Tools/releases/latest"
GITHUB_RELEASE = "https://github.com/fangdreth/MBAACC-Training-Tools/releases/tag/"
GITHUB_README = "https://github.com/fangdreth/MBAACC-Training-Tools/blob/main/README.md"

meltyPid_g = 0
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
        self.debugLevel = debugLevel    #0=regular 1=verbose 2=trace
        self.fileHandle = None
    
    def log(self, s):
        if self.debugLevel > 0:
            if self.fileHandle == None:
                self.fileHandle = open(datetime.now().strftime("RepReplay_%Y_%m_%d__%H_%M_%S.log"), "a")
            self.fileHandle.write("  "*self.debugTabs + s + "\n")
        print(s)
            
    def vlog(self, s):
        if self.debugLevel > 0:
            self.log(s)
        
    
    def trace(self, methodName, mode=""):
        if self.debugLevel == 2:
            if mode == "enter":
                self.log(methodName)
                self.debugTabs += 1
            else:
                self.debugTabs -= 1
                self.log(methodName)

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
    debugLogger_g.trace("getPidDict", "enter")
    
    pidDict = {
        p.info["name"]: p.info["pid"]
        for p in psutil.process_iter(attrs=["name", "pid"])
    }
    
    debugLogger_g.trace("getPidDict")
    
    return pidDict
    
# return the pid of an application Ex. "MBAA.exe", 
def getPid(appNameStart, appNameEnd=""):
    debugLogger_g.trace("getPid", "enter")
    
    returnVal = 0
    pidDict = getPidDict()
    for key, value in pidDict.items():
        if key.startswith(appNameStart) and key.endswith(appNameEnd):
            returnVal = value
            
    debugLogger_g.trace("getPid")
            
    return returnVal
    
def focusApp(pid):
    debugLogger_g.trace("focusApp", "enter")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = Application().connect(process=pid)
            app.top_window().set_focus()
    except:
        wrapup()
        
    debugLogger_g.trace("focusApp")
    
# melty doesn't like .send, so gotta do it manually like this
def pressKey(key):
    debugLogger_g.trace("pressKey", "enter")

    debugLogger_g.vlog("Sending " + key)

    focusApp(meltyPid_g)
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)
    wait(0.2)
    
    debugLogger_g.trace("pressKey")
    
def getParameter(obj, programHandle, baseAddress):
    debugLogger_g.trace("getParameter", "enter")
    
    ReadMem(programHandle, obj.address + baseAddress, obj.b_dat, len(obj.b_dat), None)
    obj.num = unpack('l', obj.b_dat.raw)[0]
    
    debugLogger_g.trace("getParameter")

def wrapup():
    debugLogger_g.trace("wrapup", "enter")
        
    try:
        cccasterPid = getPid("cccaster", ".exe")
        os.kill(cccasterPid, signal.SIGTERM)
    except:
        pass
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    
    debugLogger_g.trace("wrapup")
    
    sys.exit()
    
def wait(sleepTime):
    debugLogger_g.vlog("Waiting for: " + str(sleepTime))
    time.sleep(sleepTime)
 
def checkForUpdate():
    try:
        response = requests.get(GITHUB_LATEST)
        latestVersion = response.json()["name"]
        if latestVersion != VERSION:
            return (True, latestVersion)
    except:
        debugLogger_g.log("Unable to check for newer version")
        input("Press Enter to continue...")
        
    return (False, "")
 
class OBSController:
    def __init__(self):
        self.enabled = False
        self.port = 4455
        self.password = ""
        self.connected = False
        self.webSocket = None
        self.recordingInProgress = False
        
    def connect(self):
        debugLogger_g.trace("OBSController::connect", "enter")
        
        if not self.connected and self.enabled:
            try:
                self.webSocket = obsws_python.ReqClient(host='localhost', port=self.port, password=self.password)
                self.connected = True
                debugLogger_g.log("Connection successful")
            except:
                debugLogger_g.log("Unable to connect")
                debugLogger_g.trace("OBSController::connect")
                return 1
                
        debugLogger_g.trace("OBSController::connect")
        return 0
            
    def start(self):
        debugLogger_g.trace("OBSController::start", "enter")
        if self.connected and self.enabled:
            try:
                self.webSocket.start_record()
            except:
                debugLogger_g.vlog("OBSControllerObj::start failed.  This may not be a problem")
        debugLogger_g.trace("OBSController::start")
        
    def pause(self):
        debugLogger_g.trace("OBSController::pause", "enter")
        if self.connected and self.enabled:
            try:
                self.webSocket.pause_record()
            except:
                debugLogger_g.vlog("OBSControllerObj::pause failed.  This may not be a problem")
        debugLogger_g.trace("OBSController::pause")
        
    def resume(self):
        debugLogger_g.trace("OBSController::resume", "enter")
        if self.connected and self.enabled:
            if self.recordingInProgress:
                try:
                    self.webSocket.resume_record()
                except:
                    debugLogger_g.vlog("OBSControllerObj::resume failed.  This may not be a problem")
            else:
                self.start()
                self.recordingInProgress = True
        debugLogger_g.trace("OBSController::resume")
        
    def stop(self):
        debugLogger_g.trace("OBSController::stop", "enter")
        if self.connected and self.enabled:
            try:
                self.webSocket.stop_record()
            except:
                debugLogger_g.vlog("OBSControllerObj::stop failed.  This may not be a problem")
            self.recordingInProgress = False
        debugLogger_g.trace("OBSController::stop")
            
  
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
    global debugLogger_g
    
    debugLogger_g = VLogger(0)
    
    debugLogger_g.trace("main", "enter")
    
    newerVersionExists = checkForUpdate()
    
    # ensure cccaster is in the same directory
    if len([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")]) == 0:
        debugLogger_g.log("Move this executable into the same directory as CCCaster before launching it")
        wrapup()
    
    # ask for a folder
    replayPath = ""
    desyncLevel = 0
    desyncThreshold = 60   # roughly 3 seconds
    OBSControllerObj = OBSController()
    sortStyle = 0 # 0=bydatedescending 1=alphabetical
    framestepFlag = False
    activeSubMenu = ""
    while True:
        os.system('cls')
        debugLogger_g.log("Fang's Batch Replay Tool " + VERSION)
        debugLogger_g.log("")
        debugLogger_g.log("")
        if newerVersionExists[0]:
            debugLogger_g.log("0+Enter  -  Get the latest version (" + newerVersionExists[1] + ")")
            debugLogger_g.log("")
        debugLogger_g.log("1+Enter  -  replay sorting style: " + ["Oldest First(recommended)", "Alphabetical(vanilla*)"][sortStyle])
        if sortStyle == 1:
            debugLogger_g.log("            *White Len (W_LEN), Hime (A_EARTH), and a few others are treated slightly differently because of the \"_\".")
        debugLogger_g.log("2+Enter  -  framestep mode...")
        if activeSubMenu == "framestep":
            debugLogger_g.log("                A+Enter  -  enabled: " + ("On" if framestepFlag else "Off(recommended)"))
            debugLogger_g.log("                B+Enter  -  open MBAA.exe to change the screen size. use 640x480, 1280x960, or 1920x1440 for framestep.")
            debugLogger_g.log("                  Tip: Select your screen size in the drop down, then CLOSE mbaa.exe instead of clicking \"Ok\"")
            debugLogger_g.log("                C+Enter  -  pre-configure controls. useful for framestep mode")
            debugLogger_g.log("")
        debugLogger_g.log("3+Enter  -  OBS Integration...")
        if activeSubMenu == "OBS":
            debugLogger_g.log("            A+Enter  -  enabled: " + ("On" if OBSControllerObj.enabled else "Off"))
            if OBSControllerObj.enabled:
                if OBSControllerObj.connected:
                    debugLogger_g.log("            connection established")
                else:
                    debugLogger_g.log("            B+Enter  -  port: " + str(OBSControllerObj.port))
                    debugLogger_g.log("            C+Enter  -  password: " + "*"*len(OBSControllerObj.password))
                    debugLogger_g.log("            D+Enter  -  connect")
            debugLogger_g.log("")
        debugLogger_g.log("4+Enter  -  debug level: " + ["Regular(recommended)", "Verbose", "Trace"][debugLogger_g.debugLevel])
        debugLogger_g.log("5+Enter  -  desync detection level: " + ["Regular(recommended)", "Lax", "Very Lax", "Off"][desyncLevel])
        debugLogger_g.log("6+Enter  -  open the readme")
        debugLogger_g.log("--")
        debugLogger_g.log("\nWhen ready to begin, drag your folder of replays onto this window then press Enter")
        replayPath = input("==> ").strip("\"")
        
        if newerVersionExists[0] and replayPath == "0":
            webbrowser.open(GITHUB_RELEASE + newerVersionExists[1], new=0, autoraise=True)
            wrapup()
        
        if replayPath == "1":
            sortStyle = (sortStyle + 1) % 2
            continue
            
        if replayPath == "2":
            activeSubMenu = ("framestep" if activeSubMenu != "framestep" else "")
            continue
            
        if activeSubMenu == "framestep" and replayPath.lower() == "a":
            framestepFlag = not framestepFlag
            continue
            
        if activeSubMenu == "framestep" and replayPath.lower() == "b":
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
            
        if activeSubMenu == "framestep" and replayPath.lower() == "c":
            os.system('cls')
            
            # launch cccaster
            os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])

            # wait for cccaster to open
            os.system('cls')
            debugLogger_g.log("Please wait for CCCaster to open...")
            cccasterPid = 0
            while cccasterPid == 0:
                cccasterPid = getPid("cccaster", ".exe")
                wait(0.1)

            # launch replay mode
            wait(0.5)
            keyboard.write('45',delay=1)

            # wait for replay mode to launch
            os.system('cls')
            debugLogger_g.log("Please wait for MBAA to open...")
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
        
        if replayPath.lower() == "3":
            activeSubMenu = ("OBS" if activeSubMenu != "OBS" else "")
            continue
        
        if activeSubMenu == "OBS" and replayPath.lower() == "a" :
            OBSControllerObj.enabled = not OBSControllerObj.enabled
            continue
            
        if activeSubMenu == "OBS" and replayPath.lower() == "b":
            os.system('cls')
            while True:
                try:
                    obsPortTemp = int(input("Enter OBS WebSocket port (default 4455): " ))
                    if obsPortTemp < 0 or 65535 < obsPortTemp:
                        raise ValueError
                    OBSControllerObj.port = obsPortTemp
                    break
                except ValueError :
                    debugLogger_g.log("Please provide a valid port in the range 0-65535")
            continue
                    
        if activeSubMenu == "OBS" and replayPath.lower() == "c":
            os.system('cls')
            OBSControllerObj.password = getpass("Enter OBS WebSocket password (leave blank if authorization is disabled): ")
            continue
            
        if activeSubMenu == "OBS" and replayPath.lower() == "d":
            if not OBSControllerObj.connected:
                os.system('cls')
                debugLogger_g.log("Trying to connect...")
                OBSControllerObj.connect()
            input("\nPress Enter to return")
            continue
        
        if replayPath == "4":
            debugLogger_g.debugLevel = (debugLogger_g.debugLevel + 1) % 3
            continue
            
        if replayPath == "5":
            desyncLevel = (desyncLevel + 1) % 4
            if desyncLevel == 3:
                desyncThreshold = 9999
            else:
                desyncThreshold = 60 + 30 * desyncLevel
            continue
        
        if replayPath == "6":
            webbrowser.open(GITHUB_README, new=0, autoraise=True)
            continue
        
        # if they didn't pick a menu option, see if it's a valid path or not
        if not os.path.exists(replayPath):
            debugLogger_g.log("Unable to load given replay folder")
        else: # path found
            os.system('cls')
            
            # get a list of files that will be copied one-by-one to the replay folder
            if sortStyle == 0:    #by date
                replayFiles = sorted(Path(replayPath).iterdir(), key=os.path.getmtime)
            elif sortStyle == 1:  # alphabetical
                replayFiles = sorted(Path(replayPath).iterdir())
                
            # find out how many replays there are
            replayTotal = len(replayFiles)
            debugLogger_g.log("\n" + str(replayTotal) + " replays detected")
            
            if OBSControllerObj.connect() != 0:
                debugLogger_g.log("\nError connecting to OBS.  Make sure OBS is open and configured correctly.")
                input("Press Enter to return")
            
            # add the replay folder if it doesn't exist already
            if not os.path.exists("ReplayVS"):
                debugLogger_g.vlog("Creating ReplayVS folder")
                os.makedirs("ReplayVS")
                
            # add the replay folder if it doesn't exist already
            if not os.path.exists("ReplayVS\\$"):
                debugLogger_g.vlog("Creating $ folder")
                os.makedirs("ReplayVS\\$")
            
            debugLogger_g.log("\nMBAA is going to open after you press Enter again.\nAfter it opens come back to this console.")
            input("")
            break

    # launch cccaster
    os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])

    # wait for cccaster to open
    os.system('cls')
    debugLogger_g.log("Please wait for CCCaster to open...")
    cccasterPid = 0
    while cccasterPid == 0:
        cccasterPid = getPid("cccaster", ".exe")
        wait(0.1)

    # open in framestep mode if it was chosen
    if framestepFlag:
        keyboard.press('f8')

    # launch replay mode
    wait(0.5)
    keyboard.write('45',delay=1)

    # wait for replay mode to launch
    os.system('cls')
    debugLogger_g.log("Please wait for MBAA to open...")
    while meltyPid_g == 0:
        meltyPid_g = getPid("MBAA.exe")
        wait(0.1)
          
    # give the user a pep talk
    wait(2)
    os.system('cls')
    if OBSControllerObj.enabled and OBSControllerObj.connected:
        debugLogger_g.log("OBS is connected and will automatically handle starting and stopping the recording.")
    else:
        debugLogger_g.log("Open your recording software of choice now.")
        debugLogger_g.log("Remember to stop the recording once playback has ended.")
    debugLogger_g.log("")
    debugLogger_g.log("Make sure Player 1 is not assigned to a controller in the F4 menu.")
    debugLogger_g.log("")
    debugLogger_g.log("Make sure Melty is NOT in fullscreen.")
    debugLogger_g.log("")
    debugLogger_g.log("When you are ready to begin playback, press Enter on this window.")
    input("")
    os.system('cls')
    debugLogger_g.log("Playback has begun.  Please wait for the replay to finish.")

    # re-focus MBAA
    focusApp(meltyPid_g)
    
    keyboard.release('f8')

    # change the controls
    if not framestepFlag:
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
    debugLogger_g.log("Total replays: " + str(replayTotal))
    for currentRep in range(replayTotal):
        debugLogger_g.log("Starting Replay: " + str(currentRep+1))
        
        # Delete the old replay...
        try:
            debugLogger_g.log("Deleting old replay")
            shutil.rmtree("ReplayVS\\$")
        except:
            pass
        
        # ...and copy the next one
        try:
            debugLogger_g.log("Copying replay #" + str(currentRep+1) + ": " + str(replayFiles[currentRep]))
            os.makedirs("ReplayVS\\$")
            shutil.copy(replayFiles[currentRep] , "ReplayVS\\$")
            debugLogger_g.log("Replay Copied")
        except:
            debugLogger_g.log("Failed to copy replay")
            wrapup()
        
        # Select the current replay
        wait(1)         # nice healthy wait for slower computers
        pressKey('4')   # select $ folder
        wait(0.2)
        pressKey('2')# get off the "go up" folder
        pressKey('4')   # select recording
        
        OBSControllerObj.resume()
        
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
                debugLogger_g.log("Round end detected P1-" + str(p1ParaScore.num) + " P2-" + str(p2ParaScore.num))
                
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
                    debugLogger_g.log("Desync Counter " + str(desyncCounter) + "/" + str(desyncThreshold))
                    debugLogger_g.log("P1-"+P1.toString()+" P2-"+P2.toString())
                if desyncCounter == desyncThreshold:
                    debugLogger_g.log("Desync or Disconnect Detected")
                    OBSControllerObj.pause()
                    if getPid("MBAA.exe") == 0:
                        wrapup()
                    getParameter(paraRoundCount, programHandle, baseAddress)
                    if paraRoundCount.num == 1:     #every round 1 desync can be handled by hitting next round
                        pressKey('5')       # pause
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('2')
                        pressKey('4')       # next round
                    # final round or the health 
                    elif paraRoundCount.num == 3:   #every round 3 desync can be handled by hitting Return
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
                            debugLogger_g.log("Desync edge case detected")
                            pressKey('5')           # if Next was not pressed, open Start again
                            pressKey('8')
                            pressKey('8')          # go down to Return
                            pressKey('4')           # press Return
                            time.sleep(0.2)
                            pressKey('2')        # select confirm
                            pressKey('4')           # confirm
                            leaveEarlyFlag = True
                    OBSControllerObj.resume()
                        
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
        debugLogger_g.log("Replay " + str(currentRep) + " finished")
        
        if desyncCounter < desyncThreshold:
            pressKey('6')   # skip game end quote
            wait(1)
            OBSControllerObj.pause()    # most aesthetic spot to pause
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

    OBSControllerObj.stop()
    wrapup()

if __name__ == '__main__':
    main()