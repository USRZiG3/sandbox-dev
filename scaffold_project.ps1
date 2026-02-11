<#
    scaffold_project.ps1
    ---------------------
    Purpose: Creates initial folder structure and core files
             for the MNAV Macropad software project.
#>

# --- Base Paths ---
$BasePath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SrcPath = Join-Path $BasePath "src"
$Dirs = @(
    "config",
    "tests",
    "src/gui",
    "src/firmware",
    "src/utils"
)

# --- Create directories ---
foreach ($dir in $Dirs) {
    $fullPath = Join-Path $BasePath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath | Out-Null
        Write-Host "Created: $dir"
    }
}

# --- Initialize key files ---
New-Item "$BasePath/README.md" -ItemType File -Force | Out-Null
New-Item "$BasePath/.env" -ItemType File -Force | Out-Null
New-Item "$BasePath/requirements.txt" -ItemType File -Force | Out-Null

$InitPaths = Get-ChildItem "$SrcPath" -Recurse -Include * | Where-Object { $_.PSIsContainer }
foreach ($path in $InitPaths) {
    New-Item -ItemType File -Path (Join-Path $path.FullName "__init__.py") -Force | Out-Null
}

# --- Basic placeholder content ---
Set-Content "$BasePath/config/macropad.json" "{`n  `"device_port`": `"COM3`",`n  `"log_level`": `"DEBUG`",`n  `"config_version`": `"1.0`"`n}"
Set-Content "$BasePath/.env" "DEVICE_PORT=COM3`nLOG_LEVEL=DEBUG`nCONFIG_PATH=config/macropad.json"
Set-Content "$BasePath/requirements.txt" "pyserial==3.5`npillow==10.4.0`npyqt6==6.7.0"

Set-Content "$BasePath/README.md" @"
# MNAV Macropad Software

**Phase:** Environment Setup & Framework Scaffolding  
**Purpose:** This repository powers the MNAV macropad — a custom Raspberry Pi Pico–based macro controller with GUI configuration.

## Structure
- `src/gui/`: PyQt6-based configuration interface  
- `src/firmware/`: Pico serial communication and flashing logic  
- `src/utils/`: Logging, configuration helpers, and shared utilities  
- `config/`: JSON configuration for device and app settings  
- `tests/`: Automated test scripts

## Next Steps
1. Activate venv: `.\MNAV\Scripts\activate`
2. Run GUI mockup: `python src/gui/main_window.py`
3. Validate Pico serial handshake: `python src/firmware/serial_test.py`
"@

Write-Host "`n✅ Project scaffold complete!"
