param (
	[Parameter(Mandatory=$false)][string]$mode="1"
	)

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

$CCCASTER_PATH = "C:\Users\willf\WH\MBAACC - Community Edition\MBAACC"
$CCCASTER_PROC = "cccaster*"
$CCCASTER_EXE = "cccaster.*exe"
$MELTY_PROC = "MBAA"


Add-Type @"
using System;                                                                     
using System.Runtime.InteropServices;
public class SendKeysClass {
[DllImport("user32.dll")]                                                            
public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);}
"@
[system.reflection.assembly]::Loadwithpartialname("system.windows.forms")

function Launch-CCCaster
	{
	$wshell = New-Object -ComObject wscript.shell
	if ($wshell.AppActivate($CCCASTER_PROC) -eq $false)
	{
		$currentDir = $pwd
		cd $CCCASTER_PATH
		Start-Process -FilePath $($CCCASTER_PATH + "\" + $CCCASTER_EXE)
		cd $currentDir
		
		while (!Get-Process $CCCASTER_PROC -ErrorAction SilentlyContinue)
			sleep (1)
	}
}

switch ($mode)
{
	# FrameStep
	"41"
	{
		Launch-CCCaster
		
		[SendKeysClass]::keybd_event([System.Windows.Forms.Keys]::F8, 0x45, 0, 0)
		$wshell.sendkeys('{ESC}{ESC}{ESC}')
		$wshell.sendkeys('{4}{1}')
		while (!Get-Process $MELTY_PROC -ErrorAction SilentlyContinue)
			sleep (5)
		[SendKeysClass]::keybd_event([System.Windows.Forms.Keys]::F8, 0x45, 0x2, 0)

		Write-Host "Waiting for MBAA.exe to close..."
		while (Get-Process $MELTY_PROC -ErrorAction SilentlyContinue)
			sleep (1)
		
		Stop-Process -Name $CCCASTER_PROC
	}
	
	# Batch Replay
	"45"
	{
		Rename-Item -Path "ReplayVS" -NewName "ReplayVS_BAK"
		[SendKeysClass]::keybd_event([System.Windows.Forms.Keys]::F8, 0x45, 0, 0)
		$wshell.sendkeys('{ESC}{ESC}{ESC}')
		$wshell.sendkeys('{4}{1}')
		Sleep(5)
		[SendKeysClass]::keybd_event([System.Windows.Forms.Keys]::F8, 0x45, 0x2, 0)

		Write-Host "Waiting for MBAA.exe to close..."
		while (Get-Process $MELTY_PROC -ErrorAction SilentlyContinue)
		{
			sleep (1)
		}
	}
}

#Set-ExecutionPolicy Restricted -Scope CurrentUser