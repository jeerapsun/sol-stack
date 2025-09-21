#!/usr/bin/env pwsh
# backup_pg.ps1 - PostgreSQL Backup Script
param(
    [string]$BackupDir = "D:\backups",
    [string]$Host = "localhost",
    [string]$Port = "5432"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$backupFile = Join-Path $BackupDir "pg_${timestamp}.sql"

# Ensure backup directory exists
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
    Write-Host "Created backup directory: $BackupDir" -ForegroundColor Green
}

# Load environment variables
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#].+?)=(.+)$") {
            Set-Item -Path "env:$($matches[1])" -Value $matches[2]
        }
    }
}

$env:PGPASSWORD = $env:POSTGRES_PASSWORD

try {
    Write-Host "Creating PostgreSQL backup..." -ForegroundColor Cyan
    pg_dump -h $Host -p $Port -U $env:POSTGRES_USER -d $env:POSTGRES_DB -F p -f $backupFile
    
    if (Test-Path $backupFile) {
        $size = (Get-Item $backupFile).Length / 1KB
        Write-Host "✓ Backup created: $backupFile ($([math]::Round($size, 2)) KB)" -ForegroundColor Green
        
        # Keep only last 7 days of backups
        Get-ChildItem $BackupDir -Name "pg_*.sql" | 
            Sort-Object -Descending | 
            Select-Object -Skip 7 | 
            ForEach-Object { Remove-Item (Join-Path $BackupDir $_) -Force }
    } else {
        Write-Error "Backup failed - file not created"
    }
} catch {
    Write-Error "Backup failed: $_"
} finally {
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
}