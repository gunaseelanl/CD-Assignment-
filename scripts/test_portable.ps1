# MD INDUSTRIES
# Developer: M.DHANESVARAN

$ErrorActionPreference = "Stop"

powershell -ExecutionPolicy Bypass -File scripts/build_portable.ps1
python scripts/test_portable.py
