#!/usr/bin/env pwsh
# gpu_watch.ps1 - GPU Temperature Monitor
param(
    [int]$TempThreshold = 80,
    [string]$WebhookUrl = $env:N8N_ESCALATE_WEBHOOK
)

try {
    # Get GPU temperature
    $tempOutput = nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits
    $temp = [int]$tempOutput.Trim()
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    if ($temp -gt $TempThreshold) {
        $alertData = @{
            timestamp = $timestamp
            alert_type = "gpu_temperature"
            temperature = $temp
            threshold = $TempThreshold
            message = "GPU temperature is $temp°C (threshold: $TempThreshold°C)"
        } | ConvertTo-Json
        
        Write-Host "🔥 GPU ALERT: Temperature $temp°C exceeds threshold $TempThreshold°C" -ForegroundColor Red
        
        if ($WebhookUrl) {
            try {
                Invoke-RestMethod -Uri "$WebhookUrl/gpu_alert" -Method POST -Body $alertData -ContentType "application/json"
                Write-Host "Alert sent to webhook" -ForegroundColor Yellow
            } catch {
                Write-Warning "Failed to send webhook alert: $_"
            }
        }
    } else {
        Write-Host "✓ GPU temperature OK: $temp°C" -ForegroundColor Green
    }
    
    # Log to file
    $logEntry = "$timestamp,GPU_TEMP,$temp°C"
    Add-Content -Path "gpu_monitor.log" -Value $logEntry
    
} catch {
    Write-Warning "Failed to get GPU temperature: $_"
    # Check if nvidia-smi is available
    if (!(Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
        Write-Warning "nvidia-smi not found. NVIDIA drivers may not be installed."
    }
}