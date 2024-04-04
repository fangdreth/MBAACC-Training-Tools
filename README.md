![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/images/icon_raw.png?raw=true)

# Fang Replay Tool v1.8
This is a tool which offers the ability to create a playlist of replays and automatically play them one after another without any user input required.  It has the ability to detect desyncs and can skip them on its own.  Please please please let me know if you have bugs or it does not work for you.  My discord handle is "Fang\_\_\_"

### Step 1: Setup
Download the [latest version](https://github.com/fangdreth/MBAACC-Training-Tools/releases/tag/v1.8) and copy "RepReplay.exe" into the same folder as CCCaster and MBAA.exe.

### Step 2: Prepare your replay files
Create a folder anywhere on you computer, then copy the replays you want to record into that folder.  By default, replays are saved in the same directory as CCCaster in a folder called "ReplayVS".

### Step 3: Starting the Replay Tool
Double-click RepReplay.exe.  You will see a terminal pop up where you can configure how you want to run the tool.  See the section below for more details.  Once you are satisfied, click and drag the folder you created in the last step onto the terminal and press enter.  CCCaster and then MBAA will open.  Click back on the original terminal for instructions on how to begin.

# Building
Install the modules you need
- `pip install PyInstaller`
- `pip install pywinauto`
- `pip install psutil`
- Clone the repository from `https://github.com/fangdreth/MBAACC-Training-Tools`.
- Run `build.bat`

RepReplay.exe will be created in a folder called "dist".


# OBS Integration
Enabling OBS Integration will allow direct communication between the Replay Tool and OBS.  This will allow the tool to pause recording in between replays and to automatically stop the recording after the final replay.

### Download OBS
You need [OBS](https://obsproject.com/) version 28.0.0 or later.

### Create Scene
![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/images/OBS_SceneSourceAudio.png?raw=true)
- In OBS, in the Scenes tab, press the [+] button, give the scene a name, then press Ok.
- In the Sources tab, press the [+] button, select Window Capture, press Ok, in the Window dropdown, find MBAA.exe (it must be open), then press Ok.
- In the Scenes tab, press the [+] button, select Application Audio Capture, press Ok, in the Window dropdown, find MBAA.exe (it must be open), then press Ok.
- In the Audio Mixer tab, mute the Desktop Audio and Mic/Aux audio channels.

### Enable WebSockets
![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/images/OBS_WebSocket.png?raw=true)
- In OBS, in Tools->WebSocket Server Settings, check the box for Enable WebSocket Server.
- Either uncheck the box for Enable Authentication or create a password.  It does not matter.

### Connect to OBS from the Replay Tool
- In the Replay Tool, open the OBS Integration submenu.
- Enable it.
- If you changed the port, enter the new port.  4455 is the default.
- If you set a password, enter the password.  If you unchecked the box for Enable Authentication, you can leave the password blank.
- Test the connection.

![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/images/OBS_Config.png?raw=true)

![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/images/OBS_Connected.png?raw=true)


# Framestep mode
Enabling framestep mode will allow you to toggle hitboxes on and off during playback, pause, and advance frame by frame.  Here's what you need for framestep to work 

### Requirements
- Copy framestep.exe and framestep.dll into the same directory as CCCaster, MBAA, and RepReplay.exe.  You can find them one folder up from MBAACC in another folder called Tools.
- Disable the frame limiter in CCCaster settings.  Open CCCaster, then go to Settings (7), Experimental Options (D), Disable Caster Frame Limiter (1), Yes (1).
- Change MBAA's resolution to a multiple of 640x480.  Anything else will cause warping on the displayed hitboxes.

### Enable Framestep Mode
In the Replay Tool, make sure Framestep Mode is enabled.

### Pre-configure controls
Framestep doesn't have the f4 menu for setting controls, so you have to pre-configure them before running.  In the Framestep Mode submenu, pick the pre-configure option and let it do its thing.

### Framestep Features
Once playback has begun, you can press `h` on your keyboard to toggle hitbox display.

You can press `p` to pause and unpause the game.  While paused, `space` will advance once frame.

# FAQ

### Should I bother with debug levels?
Not really.

### Which desync detection level should I pick?
This changes the amount of time the script waits before deciding a match is desynced.  Unless you are recording a set with a lot of standing around doing nothing, you are probably fine leaving this setting alone.

### Why does it act so weirdly after some desyncs?
There are a lot of edge cases that can be hard to detect, so the script sends a specific string of inputs that can resolve many different cases.

### It looks like setting controls in f4 isn't working correctly

First, make sure you don't have any controllers set as player 1.

If you have a foreign keyboard (this is common with Japanese), then the f4 menu won't work as expected.  In that case, always use framestep mode and manually set the controls beforehand as follows:
- up is '8'
- down is '2'
- A is '4'
- B is '6'
- Start is '5'