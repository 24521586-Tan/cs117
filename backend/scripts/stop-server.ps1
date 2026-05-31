# Force-stop the backend on port 8000.
# Ctrl+C can't stop uvicorn while a GPU transcription thread is mid-run (the blocking
# faster-whisper call ignores the interrupt), so use this to kill it hard.
#
#   powershell -ExecutionPolicy Bypass -File scripts\stop-server.ps1

$pids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -Expand OwningProcess -Unique
if (-not $pids) { Write-Host "Nothing listening on port 8000."; exit 0 }
foreach ($p in $pids) {
    $name = (Get-Process -Id $p -ErrorAction SilentlyContinue).ProcessName
    Write-Host ("Killing PID {0} ({1})" -f $p, $name)
    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1
if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "STILL listening on 8000 — retry."
} else {
    Write-Host "Port 8000 freed."
}
