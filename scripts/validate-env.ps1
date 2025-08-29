# TGW Environment Validation Script
# Validates all required paths, dependencies, and configurations

param(
    [switch]$Fix = $false,        # Attempt to fix issues automatically
    [switch]$Verbose = $false,    # Show detailed output
    [switch]$SkipPython = $false  # Skip Python environment checks
)

# Color functions for better output
function Write-Success($msg) { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "ℹ️  $msg" -ForegroundColor Cyan }

$script:ErrorCount = 0
$script:WarningCount = 0

function Test-PathExists {
    param([string]$Path, [string]$Description, [switch]$Critical, [switch]$CreateIfMissing)

    if (Test-Path $Path) {
        Write-Success "$Description exists: $Path"
        if ($Verbose) {
            $item = Get-Item $Path -Force
            Write-Host "    Type: $($item.GetType().Name), Size: $(if($item.PSIsContainer){'Directory'}else{'{0:N0} bytes' -f $item.Length})" -ForegroundColor Gray
        }
        return $true
    }
    else {
        if ($CreateIfMissing -and $Fix) {
            try {
                New-Item -ItemType Directory -Path $Path -Force | Out-Null
                Write-Success "$Description created: $Path"
                return $true
            }
            catch {
                Write-Error "Failed to create $Description at: $Path"
                Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }

        if ($Critical) {
            Write-Error "$Description missing: $Path"
            $script:ErrorCount++
        }
        else {
            Write-Warning "$Description missing: $Path"
            $script:WarningCount++
        }
        return $false
    }
}

function Test-EnvironmentVariable {
    param([string]$Name, [string]$ExpectedPath = $null, [switch]$Critical)

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        if ($Critical) {
            Write-Error "Environment variable $Name is not set"
            $script:ErrorCount++
        }
        else {
            Write-Warning "Environment variable $Name is not set"
            $script:WarningCount++
        }
        return $false
    }

    Write-Success "Environment variable $Name = $value"

    # Check if expected path matches (if provided)
    if ($ExpectedPath -and $value -ne $ExpectedPath) {
        Write-Warning "Environment variable $Name doesn't match expected path"
        Write-Host "    Expected: $ExpectedPath" -ForegroundColor Gray
        Write-Host "    Actual:   $value" -ForegroundColor Gray
        $script:WarningCount++
    }

    # Check if the path actually exists
    if (![string]::IsNullOrWhiteSpace($ExpectedPath) -or (Test-Path $value -IsValid)) {
        if (!(Test-Path $value)) {
            Write-Warning "Path in environment variable $Name does not exist: $value"
            $script:WarningCount++
        }
    }

    return $true
}

function Test-PythonEnvironment {
    Write-Info "Checking Python environment..."

    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        }
        else {
            Write-Error "Python not found in PATH"
            $script:ErrorCount++
            return $false
        }
    }
    catch {
        Write-Error "Python not accessible: $($_.Exception.Message)"
        $script:ErrorCount++
        return $false
    }

    # Check key Python packages
    $requiredPackages = @(
        @{Name = "torch"; ImportName = "torch" },
        @{Name = "transformers"; ImportName = "transformers" },
        @{Name = "gradio"; ImportName = "gradio" },
        @{Name = "accelerate"; ImportName = "accelerate" }
    )

    foreach ($pkg in $requiredPackages) {
        try {
            $result = python -c "import $($pkg.ImportName); print($($pkg.ImportName).__version__)" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python package $($pkg.Name): $result"
            }
            else {
                Write-Warning "Python package $($pkg.Name) not found or not importable"
                $script:WarningCount++
            }
        }
        catch {
            Write-Warning "Failed to check Python package $($pkg.Name): $($_.Exception.Message)"
            $script:WarningCount++
        }
    }

    return $true
}

function Test-GitRepository {
    param([string]$Path, [string]$Description)

    if (Test-Path (Join-Path $Path ".git")) {
        Write-Success "$Description is a git repository"

        if ($Verbose) {
            Push-Location $Path
            try {
                $branch = git branch --show-current 2>$null
                $remote = git remote get-url origin 2>$null
                Write-Host "    Branch: $branch" -ForegroundColor Gray
                Write-Host "    Remote: $remote" -ForegroundColor Gray
            }
            catch {
                Write-Host "    Git info unavailable" -ForegroundColor Gray
            }
            finally {
                Pop-Location
            }
        }
        return $true
    }
    else {
        Write-Warning "$Description is not a git repository"
        $script:WarningCount++
        return $false
    }
}

function Test-DirectoryJunction {
    param([string]$LinkPath, [string]$TargetPath)

    if (Test-Path $LinkPath) {
        $item = Get-Item $LinkPath -Force
        if ($item.LinkType -eq "Junction") {
            $actualTarget = $item.Target
            if ($actualTarget -eq $TargetPath) {
                Write-Success "Directory junction correct: $LinkPath -> $TargetPath"
                return $true
            }
            else {
                Write-Warning "Directory junction target mismatch"
                Write-Host "    Expected: $TargetPath" -ForegroundColor Gray
                Write-Host "    Actual:   $actualTarget" -ForegroundColor Gray
                $script:WarningCount++
                return $false
            }
        }
        else {
            Write-Warning "Path exists but is not a junction: $LinkPath"
            $script:WarningCount++
            return $false
        }
    }
    else {
        Write-Info "Directory junction not found: $LinkPath"
        return $false
    }
}

# Main validation logic
Write-Host "🔍 TGW Environment Validation" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta

# Define expected paths
$AI_CACHE_ROOT = "C:\AI_LLM_projects\ai_warehouse"
$TGW_MODELS_DIR = "$AI_CACHE_ROOT\cache\models\llm"
$TGW_REPO = "C:\AI_LLM_projects\text-generation-webui"
$TGW_PLAYBOOK = "C:\AI_LLM_projects\tgw-playbook"

Write-Info "Expected configuration:"
Write-Host "  AI_CACHE_ROOT: $AI_CACHE_ROOT" -ForegroundColor Gray
Write-Host "  TGW_MODELS_DIR: $TGW_MODELS_DIR" -ForegroundColor Gray
Write-Host "  TGW_REPO: $TGW_REPO" -ForegroundColor Gray
Write-Host "  TGW_PLAYBOOK: $TGW_PLAYBOOK" -ForegroundColor Gray
Write-Host ""

# 1. Check directory structure
Write-Info "1. Checking directory structure..."
$criticalPaths = @(
    @{Path = $AI_CACHE_ROOT; Desc = "AI Warehouse root"; Critical = $true },
    @{Path = "$AI_CACHE_ROOT\cache"; Desc = "Cache directory"; Critical = $true },
    @{Path = "$AI_CACHE_ROOT\cache\hf"; Desc = "HuggingFace cache"; Critical = $false },
    @{Path = "$AI_CACHE_ROOT\cache\hf\transformers"; Desc = "Transformers cache"; Critical = $false },
    @{Path = "$AI_CACHE_ROOT\cache\torch"; Desc = "Torch cache"; Critical = $false },
    @{Path = $TGW_MODELS_DIR; Desc = "TGW models directory"; Critical = $true },
    @{Path = $TGW_REPO; Desc = "TGW repository"; Critical = $true },
    @{Path = $TGW_PLAYBOOK; Desc = "TGW playbook"; Critical = $false }
)

foreach ($pathInfo in $criticalPaths) {
    Test-PathExists -Path $pathInfo.Path -Description $pathInfo.Desc -Critical:$pathInfo.Critical -CreateIfMissing:(!$pathInfo.Critical)
}

Write-Host ""

# 2. Check environment variables
Write-Info "2. Checking environment variables..."
Test-EnvironmentVariable -Name "AI_CACHE_ROOT" -ExpectedPath $AI_CACHE_ROOT
Test-EnvironmentVariable -Name "HF_HOME" -ExpectedPath "$AI_CACHE_ROOT\cache\hf"
Test-EnvironmentVariable -Name "TRANSFORMERS_CACHE" -ExpectedPath "$AI_CACHE_ROOT\cache\hf\transformers"
Test-EnvironmentVariable -Name "TORCH_HOME" -ExpectedPath "$AI_CACHE_ROOT\cache\torch"
Test-EnvironmentVariable -Name "TGW_MODELS_DIR" -ExpectedPath $TGW_MODELS_DIR -Critical
Test-EnvironmentVariable -Name "TGW_REPO" -ExpectedPath $TGW_REPO
Test-EnvironmentVariable -Name "TGW_PLAYBOOK" -ExpectedPath $TGW_PLAYBOOK

Write-Host ""

# 3. Check TGW specific configuration
Write-Info "3. Checking TGW configuration..."

# Check if TGW models directory is properly configured
$tgwModelsPath = Join-Path $TGW_REPO "models"
$junctionExists = Test-DirectoryJunction -LinkPath $tgwModelsPath -TargetPath $TGW_MODELS_DIR

# Check for TGW key files
if (Test-Path $TGW_REPO) {
    $tgwFiles = @("server.py", "requirements.txt", "webui.py")
    foreach ($file in $tgwFiles) {
        $filePath = Join-Path $TGW_REPO $file
        if (Test-Path $filePath) {
            Write-Success "TGW file found: $file"
        }
        else {
            Write-Warning "TGW file missing: $file"
            $script:WarningCount++
        }
    }
}

Write-Host ""

# 4. Check Python environment (if not skipped)
if (!$SkipPython) {
    Write-Info "4. Checking Python environment..."
    Test-PythonEnvironment
}
else {
    Write-Info "4. Skipping Python environment check (--SkipPython specified)"
}

Write-Host ""

# 5. Check Git repositories
Write-Info "5. Checking Git repositories..."
if (Test-Path $TGW_REPO) {
    Test-GitRepository -Path $TGW_REPO -Description "TGW repository"
}
if (Test-Path $TGW_PLAYBOOK) {
    Test-GitRepository -Path $TGW_PLAYBOOK -Description "TGW playbook"
}

Write-Host ""

# 6. Check for existing models
Write-Info "6. Checking for existing models..."
if (Test-Path $TGW_MODELS_DIR) {
    $modelDirs = Get-ChildItem $TGW_MODELS_DIR -Directory 2>$null
    if ($modelDirs.Count -gt 0) {
        Write-Success "Found $($modelDirs.Count) model(s) in warehouse:"
        foreach ($modelDir in $modelDirs | Select-Object -First 5) {
            $modelFiles = Get-ChildItem $modelDir.FullName -File -Include "*.gguf", "*.bin", "*.safetensors" 2>$null
            $modelFileCount = ($modelFiles | Measure-Object).Count
            Write-Host "  📦 $($modelDir.Name) ($modelFileCount files)" -ForegroundColor Gray
        }
        if ($modelDirs.Count -gt 5) {
            Write-Host "  ... and $($modelDirs.Count - 5) more" -ForegroundColor Gray
        }
    }
    else {
        Write-Info "No models found in warehouse (this is normal for first-time setup)"
    }
}
else {
    Write-Warning "Models directory not accessible"
}

Write-Host ""

# 7. Summary and recommendations
Write-Host "📊 Validation Summary" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta

if ($script:ErrorCount -eq 0 -and $script:WarningCount -eq 0) {
    Write-Success "All checks passed! Environment is ready for TGW."
}
else {
    if ($script:ErrorCount -gt 0) {
        Write-Error "Found $script:ErrorCount critical error(s) that must be fixed."
    }
    if ($script:WarningCount -gt 0) {
        Write-Warning "Found $script:WarningCount warning(s) that should be addressed."
    }
}

Write-Host ""

# Provide fix recommendations
if ($script:ErrorCount -gt 0 -or $script:WarningCount -gt 0) {
    Write-Info "💡 Recommendations:"

    if (!$junctionExists -and (Test-Path $TGW_REPO)) {
        Write-Host "  • Create directory junction: mklink /D `"$tgwModelsPath`" `"$TGW_MODELS_DIR`"" -ForegroundColor Cyan
    }

    if ($script:ErrorCount -gt 0) {
        Write-Host "  • Run with -Fix flag to attempt automatic repairs" -ForegroundColor Cyan
        Write-Host "  • Check that all required directories exist and are accessible" -ForegroundColor Cyan
    }

    if ($script:WarningCount -gt 0) {
        Write-Host "  • Set missing environment variables using scripts\set-env.ps1" -ForegroundColor Cyan
        Write-Host "  • Install missing Python packages if needed" -ForegroundColor Cyan
    }
}

Write-Host "  • Use -Verbose flag for detailed information" -ForegroundColor Cyan
Write-Host "  • Use -SkipPython to skip Python environment checks" -ForegroundColor Cyan

# Exit with appropriate code
if ($script:ErrorCount -gt 0) {
    exit 1
}
else {
    exit 0
}