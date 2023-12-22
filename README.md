![alt text](https://github.com/WillHildreth/MBAACC-Training-Tools/blob/main/icon_raw.png?raw=true)

# Batch Replay Tool
This is a tool which offers the ability to create a playlist of replays and automatically play them one after another without any user input required.  It has the ability to detect desyncs and can skip them on its own.  Please please please let me know if you have bugs or it does not work for you.  My discord handle is "Fang\_\_\_"

## Step 1: Setup
Either download the source and double-click on build.bat, or get the executable directly from the Releases page [Add link here].  If you build it yourself, the executable will be created in the same directory under a folder called "dist".  However you got it, take the executable and put it in the same directory as your copy of MBAA.exe.

## Step 2: Prepare your replay files
Create a folder anywhere on your computer where you will put copies of the replays you want to playback.  Melty Blood replay files are kept in a folder called "ReplayVS" in the same directory as the game itself.  Find the replays you want to batch record and select them.  Sorting by date, using shift-click for many files, and control-click for multiple individual files might help you grab only the ones you want.  Copy and paste those replay files into the folder you created at the beginning of this step.

## Step 3: Starting the Batch Replay Tool
Double-click on the batch replay executable.  A window will pop up with instructions to click-and-drag the folder you made in the last step.  Click back on the command window to make sure it is focused, then press Enter.  MBAA will open on its own.

## Step 4: Attach OBS
Download [OBS](https://obsproject.com/).  Open OBS and create a new Scene.  In that Scene, add a new Source for Window Capture.  Select MBAA in the Window Capture dialogue.  Once you are ready, click Start Recording.  **It is important you do NOT fullscreen melty**

## Step 5: Start the replay
Go back to the command window from the Replay Tool.  Press enter on it and step away.  You might be able to use your computer for other things while the replays are running, but you run the risk of control from the program getting desynced.
MBAA will close on its own when the replay batch is finished.  Try not to let OBS run for too long or you'll end up with very large video files.

## FAQ

### Framestep mode?
Enabling framestep mode will allow you to toggle hitboxes on and off during playback.  Here's what you need for framestep to work correctly:
- framestep.exe and framestep.dll in the same directory as CCCaster, MBAA, and RepReplay.exe.  You can find them one folder up from MBAACC in another folder called Tools.
- Disable the frame limiter in CCCaster settings.  Open CCCaster, then go to Settings (7), Experimental Options (D), Disable Caster Frame Limiter (1), Yes (1).

### Pre-configure controls for framestep?
Framestep doesn't have the f4 menu for setting controls, so you have to pre-configure them before running.  Just pick the pre-configure option and let it do its thing.

### Where are the hitboxes?
If you are in framestep mode, after the playback begins, press H on your keyboard to turn them on.

### The hitboxes are on, but they don't match the sprites
MBAA's native resolution is 640x480, and hitboxes won't render correctly unless a multiple of that size is chosen.  640x480, 1280,960, and 1920x1440 are all sizes you can use.

### How does changing screen size work?
Screen size is controlled in MBAA.exe, not CCCaster.  The replay tool has an option in the menu to open MBAA.exe for you so you can change it to what you want, but after the recording is over, you will have to remember to go back on your own and change it to what you prefer.
-Here's a tip.  In MBAA.exe, after you pick your screen size in the dropdown box, you can simply close the window instead of hitting "Ok" and opening up the whole game.

### Should I bother with debug levels?
Not really.  It won't make you a better melty player.

### Which desync detection level should I pick?
This changes the amount of time the script waits before deciding a match is desynced.  Unless you are recording a set with a lot of standing around doing nothing, you probably fine leaving this setting alone.

### Do I need potato mode?
If you can't hit 60 fps in a 20 year old PC game, yes.

### Why does it act so weirdly after some desyncs?
Because of limitations of the script, it can't always perfectly know the circumstances of a desync, so it sends certain streams of inputs that can remedy multiple scenarios at the same time.

### It looks like setting controls in f4 isn't working correctly
This can happen on some foreign keyboard types.  In that case, always use framestep mode and manually set the controls beforehand as follows:
-up is '8'
-down is '2'
-A is '4'
-B is '6'
-Start is '5'