# figpipe autonomous evolution loop.
#
# RUN BY the Startup launcher (figpipe-evolve.vbs). Kept out of the Startup folder itself so
# it can be edited without touching the login configuration.
#
# Runs the evolution cycle, then sleeps 6 hours, forever. Logs to knowledge/loop.log with a
# timestamp so a silent failure is visible as a GAP in the log rather than as nothing at all.
#
# WHY THE BACKOFF EXISTS
#   The first version slept a flat 6 hours after EVERY outcome, including exit code 3 -- which is
#   the measurement lock refusing because another run held it. A lock collision is a transient
#   scheduling accident, not a completed cycle: sleeping six hours on it means one manual run can
#   starve the schedule for a quarter of a day. Observed on 2026-10-20: a manual `cron_run` at
#   01:52 made the loop take exit=3 at 01:54, and it then idled until 07:54 doing nothing.
#
#   A transient refusal now retries after a short backoff; only a completed cycle sleeps the full
#   interval. The retry budget is bounded so a genuinely stuck lock cannot spin forever.
#
# WHY THE HEARTBEAT EXISTS
#   loop.log grows without bound and a watchdog should not have to parse it to answer "is this
#   alive?". knowledge/loop.heartbeat is one line: timestamp | state | pid. A watchdog compares its
#   mtime against a threshold and restarts the loop when it is too old.
$py     = 'C:\Users\Administrator\AppData\Local\hermes\tools\python-3.14.7+20260901-win32-x64\python.exe'
$script = 'E:\2026-AI4S\figpipe\scripts\cron_run.py'
$log    = 'E:\2026-AI4S\figpipe\knowledge\loop.log'
$beat   = 'E:\2026-AI4S\figpipe\knowledge\loop.heartbeat'

#: Exit code the runner uses when the measurement lock refused (see cron_run.py).
$EXIT_BUSY = 3
#: How long to wait after a transient refusal, and how many times to try before a full interval.
$RETRY_SLEEP_S = 300
$RETRY_MAX     = 6

function Write-Log([string]$text) {
    $text | Out-File -FilePath $log -Append -Encoding utf8
}

function Write-Heartbeat([string]$state) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')|$state|$PID" |
        Out-File -FilePath $beat -Encoding utf8
}

Write-Log "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] loop started (pid $PID)"
Write-Heartbeat "started"

while ($true) {
    $attempt = 0
    while ($true) {
        $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        Write-Heartbeat "running"
        try {
            $out = & $py $script 2>&1
            $code = $LASTEXITCODE
            Write-Log "[$stamp] exit=$code"
            if ($out) { Write-Log ($out -join "`n") }
        } catch {
            $code = -1
            Write-Log "[$stamp] EXCEPTION: $_"
        }

        if ($code -eq $EXIT_BUSY) {
            # Transient: another measurement held the lock. Retry shortly, do not sleep six hours.
            $attempt++
            if ($attempt -lt $RETRY_MAX) {
                Write-Log "[$stamp] measurement lock busy; retry $attempt/$RETRY_MAX in ${RETRY_SLEEP_S}s"
                Write-Heartbeat "backoff"
                Start-Sleep -Seconds $RETRY_SLEEP_S
                continue
            }
            Write-Log "[$stamp] lock still busy after $RETRY_MAX attempts; waiting a full interval"
        }
        break
    }
    Write-Heartbeat "idle"
    Start-Sleep -Seconds (6 * 3600)
}
