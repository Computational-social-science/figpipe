# Run the watchdog every 30 minutes, forever.
#
# WHY A LOOP AND NOT A SCHEDULED TASK
#   Registering a Windows scheduled task needs administrator rights, and this project runs
#   unattended under a normal user account (the evolution loop itself is launched from the Startup
#   folder for exactly that reason). A background loop started the same way needs no elevation, so
#   the guard ships with the thing it guards instead of depending on a privilege nobody granted.
#
#   The cost is honest: a watchdog loop is itself a process that can die. Two mitigations, and the
#   limitation is stated rather than hidden:
#     * it restarts with the evolution loop at login, from the same Startup entry
#     * it writes knowledge/watchdog.log, so its own death is visible as a gap
#   A genuinely crash-proof watchdog needs a service or a scheduled task, which needs elevation.
$here   = 'E:\2026-AI4S\figpipe'
$wd     = Join-Path $here 'scripts\watchdog.ps1'
$log    = Join-Path $here 'knowledge\watchdog.log'
$everyS = 30 * 60

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] watchdog loop started (pid $PID)" |
    Out-File -FilePath $log -Append -Encoding utf8

while ($true) {
    try {
        & powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File $wd
    } catch {
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] watchdog invocation failed: $_" |
            Out-File -FilePath $log -Append -Encoding utf8
    }
    Start-Sleep -Seconds $everyS
}
