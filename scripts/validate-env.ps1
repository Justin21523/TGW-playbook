# TGW Environment Validation Script
# Validates all required paths, dependencies, and configurations

param(
    [switch]$Fix = $false,        # Attempt to fix issues automatically
    [switch]$Verbose = $false,    # Show detailed output
    [switch]$SkipPython = $false  # Skip Python environment checks
)

# Color functions for better output
function Write-Success($msg) { Write-Host "??$msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "??  $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "??$msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "?對?  $msg" -ForegroundColor Cyan }

$script:ErrorCount = 0
$script:WarningCount = 0

function Test-PathExists {
    param([string]$Path, [string]$Description, [switch]$Critical, [switch]$CreateIfMissing)

    if (Test-Path $Path) {
        Write-Success "$Description exists: $Path"
        return $true
    } else {
        if ($CreateIfMissing -and $Fix) {
            try {
                New-Item -ItemType Directory -Path $Path -Force | Out-Null
                Write-Success "$Description created: $Path"
                return $true
            } catch {
                Write-Error "Failed to create $Description at: $Path"
                Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }

        if ($Critical) {
            Write-Error "$Description missing: $Path"
            $script:ErrorCount++
        } else {
            Write-Warning "$Description missing: $Path"
            $script:WarningCount++
        }
        return $false
    }
}

# Main validation logic
Write-Host "?? TGW Environment Validation" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta

# Define expected paths
$AI_CACHE_ROOT = "C:\AI_LLM_projects\ai_warehouse"
$TGW_MODELS_DIR = "$AI_CACHE_ROOT\cache\models\llm"
$TGW_REPO = "C:\AI_LLM_projects\text-generation-webui"
$TGW_PLAYBOOK = "C:\AI_LLM_projects\tgw-playbook"

# Check directory structure
Write-Info "1. Checking directory structure..."
$criticalPaths = @(
    @{Path=$AI_CACHE_ROOT; Desc="AI Warehouse root"; Critical=$true},
    @{Path=$TGW_MODELS_DIR; Desc="TGW models directory"; Critical=$true},
    @{Path=$TGW_REPO; Desc="TGW repository"; Critical=$true},
    @{Path=$TGW_PLAYBOOK; Desc="TGW playbook"; Critical=$false}
)

foreach ($pathInfo in $criticalPaths) {
    Test-PathExists -Path $pathInfo.Path -Description $pathInfo.Desc -Critical:$pathInfo.Critical -CreateIfMissing:(!$pathInfo.Critical)
}

Write-Host ""
Write-Host "?? Validation Summary" -ForegroundColor Magenta

if ($script:ErrorCount -eq 0 -and $script:WarningCount -eq 0) {
    Write-Success "All critical checks passed! Environment is ready for TGW."
} else {
    if ($script:ErrorCount -gt 0) {
        Write-Error "Found $script:ErrorCount critical error(s) that must be fixed."
    }
    if ($script:WarningCount -gt 0) {
        Write-Warning "Found $script:WarningCount warning(s) that should be addressed."
    }
}

exit $(if ($script:ErrorCount -gt 0) { 1 } else { 0 })
