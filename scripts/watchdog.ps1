# figpipe loop watchdog: restart the evolution loop when its heartbeat goes stale.
#
# WHY THIS EXISTS
#   The evolution loop is the only unattended component in this project, and until now nothing
#   checked that it was alive. The evidence that it dies silently is in loop.log: 13 markers over
#   three days, one gap of 10.8 hours against a 6-hour schedule, and -- on 2026-10-20 -- the loop
#   took exit=3 at 01:54 (the measurement lock refused because a manual run held it) and then slept
#   the full six hours doing nothing.
#
#   Every other defect this project found had a guard. This one had only a log line nobody reads.
#
# WHAT IT CHECKS
#   1. knowledge/loop.heartbeat is younger than the staleness threshold, AND
#   2. a powershell process is actually running loop.ps1
#
#   Both, because either alone is wrong: a fresh heartbeat with a dead process means the file is
#   stale-but-touched, and a live process with an old heartbeat means it is wedged.
#
# HOW IT RESTARTS
#   It does NOT kill anything. A wedged loop may be mid-measurement, and killing it would abandon a
#   half-written report -- the exact class of defect this project spent rounds fixing. Instead it
#   logs the condition and, only when the process is GONE, launches a new loop via the same .vbs
#   launcher the Startup folder uses, so there is one launch path, not two.
#
# USAGE
#   powershell -NoProfile -File scripts/watchdog.ps1
#   Run it from Task Scheduler every 30 minutes, or by hand.

$ErrorActionPreference = 'Stop'

$root     = 'E:\2026-AI4S\figpipe'
$beat     = Join-Path $root 'knowledge\loop.heartbeat'
$log      = Join-Path $root 'knowledge\watchdog.log'
$loop     = Join-Path $root 'scripts\loop.ps1'
$launcher = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\figpipe-evolve.vbs'

#: The loop sleeps 6 hours between cycles and writes a heartbeat before and after each. Anything
#: older than this means the loop is not merely sleeping -- it is gone or wedged.
$STALE_MINUTES = 8 * 60

function Write-Log([string]$text) {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $text" |
        Out-File -FilePath $log -Append -Encoding utf8
}

#: The pattern that identifies a running evolution loop. Overridable so a TEST can point it at a
#: script name that is certainly not running, which is the only way to exercise the DEAD branch
#: while the real loop is alive. Without this the guard's failure path is untestable, and an
#: untestable failure path is a control that looks present and does nothing.
$LOOP_PATTERN = if ($env:FIGPIPE_LOOP_PATTERN) { $env:FIGPIPE_LOOP_PATTERN } else { 'loop\.ps1' }

function Get-LoopProcesses {
    Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" |
        Where-Object { $_.CommandLine -and $_.CommandLine -match $LOOP_PATTERN }
}

$problems = @()

# 1. heartbeat age
if (-not (Test-Path $beat)) {
    $problems += "no heartbeat file at $beat"
    $ageMinutes = [double]::PositiveInfinity
} else {
    $ageMinutes = ((Get-Date) - (Get-Item $beat).LastWriteTime).TotalMinutes
    if ($ageMinutes -gt $STALE_MINUTES) {
        $problems += ("heartbeat is {0:N0} min old (threshold {1} min)" -f $ageMinutes, $STALE_MINUTES)
    }
}

# 2. process presence
$procs = @(Get-LoopProcesses)
if ($procs.Count -eq 0) {
    $problems += "no powershell process is running loop.ps1"
}

if ($problems.Count -eq 0) {
    # Healthy. Say so only occasionally: a watchdog that logs every 30 minutes forever is noise.
    $stateFile = Join-Path $root 'knowledge\.watchdog.last-ok'
    $shouldLog = $true
    if (Test-Path $stateFile) {
        $last = (Get-Item $stateFile).LastWriteTime
        $shouldLog = ((Get-Date) - $last).TotalHours -ge 6
    }
    if ($shouldLog) {
        Write-Log ("OK: loop alive, heartbeat {0:N0} min old, {1} process(es)" -f $ageMinutes, $procs.Count)
        (Get-Date).ToString('o') | Out-File -FilePath $stateFile -Encoding utf8
    }
    exit 0
}

# Something is wrong. Report the full condition before acting.
Write-Log ("PROBLEM: " + ($problems -join '; '))

if ($procs.Count -gt 0) {
    # A live process with a stale heartbeat is WEDGED. Do not kill it: it may be mid-measurement,
    # and abandoning a half-written report is the defect class this project keeps fixing.
    Write-Log ("WEDGED: pid(s) " + (($procs | ForEach-Object { $_.ProcessId }) -join ',') +
               " running loop.ps1 but the heartbeat is stale. NOT killing: it may be mid-measurement. " +
               "A human should inspect knowledge/loop.log.")
    exit 2
}

# No process at all: the loop is gone and safe to relaunch.
if (-not (Test-Path $launcher)) {
    Write-Log "CANNOT RESTART: launcher not found at $launcher"
    exit 3
}

Write-Log "RESTARTING: launching $launcher"
try {
    Start-Process -FilePath 'wscript.exe' -ArgumentList "`"$launcher`"" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    $after = @(Get-LoopProcesses)
    if ($after.Count -gt 0) {
        Write-Log ("RESTARTED: pid(s) " + (($after | ForEach-Object { $_.ProcessId }) -join ','))
        exit 0
    }
    Write-Log "RESTART FAILED: launcher returned but no loop process appeared"
    exit 4
} catch {
    Write-Log "RESTART FAILED: $_"
    exit 5
}
