#plans/TODO
# bundle cccaster
# make it pretty
# bundle recording?
# brainstorm how to know when a match is over


Set-ExecutionPolicy RemoteSigned

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

# Main Loop
while($true)
{
	# Menu Loop
	$userSelect = -1
	while($true)
	{
		#Clear-Host
		Write-Output "1 - Frame Step Menu"
		Write-Output "2 - Batch Record Menu"
		$userSelect = Read-Host "="
		break
	}
	
	Switch ($userSelect)
	{
		# Frame Step
		1
		{
			$wshell = New-Object -ComObject wscript.shell
			if ($wshell.AppActivate('CCCaster 3.1004') -eq $false)
			{
				$currentDir = $pwd
				cd $CCCASTER_PATH
				Start-Process -FilePath $($CCCASTER_PATH + "\cccaster.*exe")
				cd $currentDir
				Sleep(1)
			}
			

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
			Stop-Process -Name $CCCASTER_PROC
		}
	}
}

#Set-ExecutionPolicy Restricted