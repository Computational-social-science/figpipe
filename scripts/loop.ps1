# figpipe autonomous evolution loop.
#
# RUN BY the Startup launcher (figpipe-evolve.vbs). Kept out of the Startup folder itself so
# it can be edited without touching the login configuration.
#
# Runs the evolution cycle, then sleeps 6 hours, forever. Logs to knowledge/loop.log with a
# timestamp so a silent failure is visible as a GAP in the log rather than as nothing at all.
$py     = 'C:\Users\Administrator\AppData\Local\hermes\tools\python-3.14.7+20260901-win32-x64\python.exe'
$script = 'E:\2026-AI4S\figpipe\scripts\cron_run.py'
$log    = 'E:\2026-AI4S\figpipe\knowledge\loop.log'

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] loop started" | Out-File -FilePath $log -Append -Encoding utf8
while ($true) {
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    try {
        $out = & $py $script 2>&1
        $code = $LASTEXITCODE
        "[$stamp] exit=$code" | Out-File -FilePath $log -Append -Encoding utf8
        $out | Out-File -FilePath $log -Append -Encoding utf8
    } catch {
        "[$stamp] EXCEPTION: $_" | Out-File -FilePath $log -Append -Encoding utf8
    }
    Start-Sleep -Seconds (6 * 3600)
}
