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
#
# SINGLE INSTANCE, by an exclusive file handle
#   The launcher is idempotent, but a script started DIRECTLY -- a manual run, a stale Startup
#   entry, a restart during the fork-bomb window -- bypasses that check. The log shows the result:
#   190 "watchdog loop started" lines against ONE live process, so instances accumulated and each
#   ran its own watchdog every 30 minutes.
#
#   WHY A FILE HANDLE AND NOT A MUTEX: `New-Object System.Threading.Mutex($true, name, [ref]$new)`
#   reports createdNew only for the first creator in a process's lifetime, and the handle is
#   released when the object is collected. Two processes both saw "created" and both ran. An
#   exclusive-share file handle is held for the process lifetime and a second opener FAILS -- the
#   same primitive `figpipe/lock.py` uses for measurements.
$lockFile = 'E:\2026-AI4S\figpipe\knowledge\.watchdog-loop.lock'
try {
    $lockHandle = [System.IO.File]::Open($lockFile, 'OpenOrCreate', 'ReadWrite', 'None')
} catch {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] another watchdog loop holds the lock; exiting" |
        Out-File -FilePath 'E:\2026-AI4S\figpipe\knowledge\watchdog.log' -Append -Encoding utf8
    exit 0
}

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
