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

