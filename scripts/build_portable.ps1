# MD INDUSTRIES
# Developer: M.DHANESVARAN

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python not found in PATH"
}

New-Item -ItemType Directory -Force bin | Out-Null
New-Item -ItemType Directory -Force output | Out-Null

@'
@echo off
python -m pyportcc %*
'@ | Set-Content -Encoding ascii bin\pyportcc.cmd

@'
#!/usr/bin/env sh
python -m pyportcc "$@"
'@ | Set-Content -Encoding ascii bin\pyportcc

Write-Host "Portable build completed. Use python -m pyportcc or bin\\pyportcc.cmd."
