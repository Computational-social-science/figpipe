' Launches the figpipe evolution loop AND its watchdog, hidden, without blocking login.
'
' WHY .vbs: Windows executes only .exe/.bat/.cmd/.lnk/.vbs/.com from the Startup folder. A
' .ps1 placed there is silently ignored -- which is why the first attempt produced no
' loop.log and no process. This launcher is the actual entry point.
'
' WHY TWO PROCESSES: the evolution loop runs every 6 hours; the watchdog checks every 30 minutes
' that the loop is alive and restarts it when it is gone. Starting only the loop means a dead loop
' stays dead until the next login -- which is exactly what happened between 2026-10-18 and 20.
'
' WHY THE SINGLE-INSTANCE CHECK: this launcher is called from three places (login, the watchdog,
' and by hand), and without a check every call starts ANOTHER loop and ANOTHER watchdog. On
' 2026-10-20 a restart drill produced 76 processes in ten seconds -- two watchdogs each restarting
' a loop the other had just restarted. A launcher must be idempotent, or the thing it guards
' becomes a fork bomb.
Set WshShell = CreateObject("WScript.Shell")
Set Svc = GetObject("winmgmts:\\.\root\cimv2")

Function CountMatching(needle)
    Dim q, p, n
    n = 0
    Set q = Svc.ExecQuery("SELECT CommandLine FROM Win32_Process WHERE Name='powershell.exe'")
    For Each p In q
        If Not IsNull(p.CommandLine) Then
            If InStr(LCase(p.CommandLine), LCase(needle)) > 0 Then n = n + 1
        End If
    Next
    CountMatching = n
End Function

If CountMatching("loop.ps1") = 0 Then
    WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""E:\2026-AI4S\figpipe\scripts\loop.ps1""", 0, False
End If

If CountMatching("watchdog_loop.ps1") = 0 Then
    WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""E:\2026-AI4S\figpipe\scripts\watchdog_loop.ps1""", 0, False
End If
