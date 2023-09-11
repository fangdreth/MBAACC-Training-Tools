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
CCCASTER_PATH = "C:\\Users\\willf\\WH\\MBAACC - Community Edition\\MBAACC"
CCCASTER_PROC = "cccaster*"
MELTY_PROC = "MBAA"
REPLAY_PATH = "C:\\Users\\willf\\WH\\Repos\\MBAACC Training Tools\\MBAACC-Training-Tools\\Reps"

# dictionary of every application (name, pid)
def getPidDict():
    pidDict = {
        p.info["name"]: p.info["pid"]
        for p in psutil.process_iter(attrs=["name", "pid"])
    }
    return pidDict
    
# melty doesn't like .send, so gotta do it manually like this
def pressKey(key):
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)
    time.sleep(0.5)
    
def b_unpack(d_obj):
    num = 0
    num = len(d_obj)
    if num == 1:
        return unpack('b', d_obj.raw)[0]
    elif num == 2:
        return unpack('h', d_obj.raw)[0]
    elif num == 4:
        return unpack('l', d_obj.raw)[0]

def r_mem(ad, b_obj, programHandle, base_ad):
    ReadMem(programHandle, ad + base_ad, b_obj, len(b_obj), None)
    return b_unpack(b_obj)

def para_get(obj, programHandle, base_ad):
    obj.num = r_mem(obj.ad, obj.b_dat, programHandle, base_ad)

class para:
    def __init__(self, byte_len):
        self.ad = 0x00
        self.num = 0
        self.b_dat = create_string_buffer(byte_len)
          
def main():

    # Copy given replays to CCCCaster location and back up old replays
    if not os.path.exists("ReplayVS"):
        os.makedirs("ReplayVS")
    if os.path.exists("ReplayVS\\$"):
        shutil.rmtree("ReplayVS\\$")
    shutil.copytree(REPLAY_PATH , "ReplayVS\\$")
    replayTotal = len(os.listdir("ReplayVS\\$"))

    # TODO
    # write a listener script that will revert the folders when it detects MBAA closing

    # launch cccaster
    currentDir = os.getcwd()
    os.chdir(CCCASTER_PATH) # TODO change this to run in same directory as cccaster
    os.startfile([name for name in os.listdir() if name.startswith("cccaster") and name.endswith(".exe")][0])
    os.chdir(currentDir)

    # wait for cccaster to open
    print("Waiting for CCCaster to open...")
    cccasterPid = 0
    while cccasterPid == 0:
        pidDict = getPidDict()
        for key, value in pidDict.items():
            if key.startswith("cccaster") and key.endswith(".exe"):
                cccasterPid = value
                break
        time.sleep(0.2)

    # launch replay mode    
    keyboard.write('45',delay=1)

    # wait for replay mode to launch
    print("Waiting for MBAA to open...")
    meltyPid = 0
    while meltyPid == 0:
        pidDict = getPidDict()
        for key, value in pidDict.items():
            if key == "MBAA.exe":
                meltyPid = value
                break
        time.sleep(0.2)
          
    # give the user a pep talk
    time.sleep(2)
    os.system('cls')
    print("Open your recording software of choice now")
    print("...")
    print("Unplug any controllers you may have --")
    print("Or at least ensure you do not have a controller as player 1 in the f4 menu")
    print("...")
    print("Once the playback begins, do not tab out")
    print("...")
    input("To begin playback, press Enter")

    # re-focus MBAA
    app = Application().connect(process=meltyPid)
    app.top_window().set_focus()

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
    pressKey('f4')

    # get MBAA handle from its pid
    programHandle = OpenProcess(0x1F0FFF, False, meltyPid)

    # snapshot MBAA
    snapshot = CreateToolhelp32Snapshot(0x00000008, meltyPid)

    # get the module
    lpme = MODULEENTRY32()
    lpme.dwSize = sizeof(lpme)
    result = Module32First(snapshot, byref(lpme))

    # not going into this because Module32First is working fine
    while meltyPid != lpme.th32ProcessID:
        result = Module32Next(snapshot, byref(lpme))

    # get the base address of MBAA in memory
    b_baseAddr = create_string_buffer(8)
    b_baseAddr.raw = lpme.modBaseAddr
    base_ad = unpack('q', b_baseAddr.raw)[0]



            
    # Player 1 score
    p1ParaScore = para(4)
    p1ParaScore.ad = 0x159550

    p1ParaX = para(4)
    p1ParaX.ad = 0x155140 + 0xF8

    p1ParaY = para(4)
    p1ParaY.ad = 0x155248

    # Player 2 Score
    p2ParaScore = para(4)
    p2ParaScore.ad = 0x159580

    p2ParaX = para(4)
    p2ParaX.ad = 0x155140 + 0xF8 + 0xAFC

    p2ParaY = para(4)
    p2ParaY.ad = 0x155248 + 0xAFC


    #subprocess.run(["powershell", "-Command", ".\LaunchFrameStep.ps1"], capture_output=True)
    #subprocess.run(["powershell", "-Command", ".\CCCasterAdapter.ps1 -mode \"41\" -slot \"1\""], capture_output=True)

    DESYNC_THRESHOLD = 30

    # navigate the replay menu
    for currentRep in range(replayTotal):
        for i in range(currentRep):
            pressKey('down')
        pressKey('a')   # select recording
        time.sleep(1)
        pressKey('a')   # skip vs screen
        time.sleep(0.5)
        pressKey('a')   # skip intro quote

        oldP1Score = 0
        oldP2Score = 0
        oldP1X = 0
        oldP1Y = 0
        oldP2X = 0
        oldP2Y = 0
        desyncCounter = 0
        desynced = False
        para_get(p1ParaScore, programHandle, base_ad)
        para_get(p2ParaScore, programHandle, base_ad)
        
        # the game starts
        while p1ParaScore.num != 2 and p2ParaScore.num != 2:
            para_get(p1ParaScore, programHandle, base_ad)
            para_get(p2ParaScore, programHandle, base_ad)
            
            # detect a round ending
            if oldP1Score != p1ParaScore.num or oldP2Score != p2ParaScore.num:
                print("A round has ended")
                oldP1Score = p1ParaScore.num
                oldP2Score = p2ParaScore.num
                keyboard.release('a') # release in the case it was a desync
                desyncCounter = 0
                desynced = False
                time.sleep(1)
                pressKey('a')   # skip win quote
                
            para_get(p1ParaX, programHandle, base_ad)
            para_get(p1ParaY, programHandle, base_ad)
            para_get(p2ParaX, programHandle, base_ad)
            para_get(p2ParaY, programHandle, base_ad)
            if oldP1X == p1ParaX.num and oldP1Y == p1ParaY.num and oldP2X == p2ParaX.num and oldP2Y == p2ParaY.num and not desynced:
                desyncCounter += 1
                if desyncCounter/DESYNC_THRESHOLD > 0.5:
                    print("Potential Desync Detected (" + str(desyncCounter) + "/" + str(DESYNC_THRESHOLD) + ")")
                if desyncCounter == DESYNC_THRESHOLD:
                    print("Desync Detected")
                    desynced = True
                    keyboard.press('a')
            else:
                desyncCounter = 0
            oldP1X = p1ParaX.num
            oldP1Y = p1ParaY.num
            oldP2X = p2ParaX.num
            oldP2Y = p2ParaY.num
            
            time.sleep(0.1)
            
        # exit finished replay
        pressKey('a')   # skip game end quote
        pressKey('down')# highlight Replay Selection
        pressKey('a')   # select Replay Selection
        time.sleep(1)

if __name__ == '__main__':
    main()
   

    
