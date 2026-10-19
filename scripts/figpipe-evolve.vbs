' Launches the figpipe evolution loop AND its watchdog, hidden, without blocking login.
'
' WHY .vbs: Windows executes only .exe/.bat/.cmd/.lnk/.vbs/.com from the Startup folder. A
' .ps1 placed there is silently ignored -- which is why the first attempt produced no
' loop.log and no process. This launcher is the actual entry point.
'
' WHY TWO PROCESSES: the evolution loop runs every 6 hours; the watchdog checks every 30 minutes
' that the loop is alive and restarts it when it is gone. Starting only the loop means a dead loop
' stays dead until the next login -- which is exactly what happened between 2026-10-18 and 20.
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""E:\2026-AI4S\figpipe\scripts\loop.ps1""", 0, False
WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""E:\2026-AI4S\figpipe\scripts\watchdog_loop.ps1""", 0, False
