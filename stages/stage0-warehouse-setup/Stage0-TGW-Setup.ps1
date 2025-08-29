# Stage 0: TGW Shared Warehouse Setup
# Two approaches: --model-dir flag vs mklink directory junction

# === PREREQUISITES ===
# Ensure directories exist
$AI_CACHE_ROOT = "C:\AI_LLM_projects\ai_warehouse"
$TGW_MODELS_DIR = "$AI_CACHE_ROOT\cache\models\llm"
$TGW_REPO = "C:\AI_LLM_projects\text-generation-webui"

Write-Host "Creating shared warehouse directories..." -ForegroundColor Green
New-Item -ItemType Directory -Path $TGW_MODELS_DIR -Force | Out-Null

# === APPROACH A: --model-dir Flag Method ===
Write-Host "`n=== APPROACH A: Using --model-dir flag ===" -ForegroundColor Yellow

# Navigate to TGW repo
Set-Location $TGW_REPO

# Start TGW with shared model directory
Write-Host "Starting TGW with shared model directory..." -ForegroundColor Cyan
Write-Host "Command: python server.py --model-dir `"$TGW_MODELS_DIR`" --api --listen" -ForegroundColor Gray

# Note: This will start the server - run manually to see UI
# python server.py --model-dir "$TGW_MODELS_DIR" --api --listen

Write-Host "`n=== APPROACH B: mklink Directory Junction ===" -ForegroundColor Yellow

# Stop any running TGW instance first
Write-Host "If TGW is running, stop it with Ctrl+C first" -ForegroundColor Red

# Remove existing models directory if it exists
$existingModelsDir = Join-Path $TGW_REPO "models"
if (Test-Path $existingModelsDir) {
    Write-Host "Removing existing models directory..." -ForegroundColor Cyan
    # Check if it's already a junction
    $item = Get-Item $existingModelsDir -Force
    if ($item.LinkType -eq "Junction") {
        cmd /c "rmdir /s /q `"$existingModelsDir`""
    }
    else {
        Remove-Item $existingModelsDir -Recurse -Force
    }
}

# Create directory junction (requires admin privileges)
Write-Host "Creating directory junction..." -ForegroundColor Cyan
Write-Host "Command: mklink /D `"$existingModelsDir`" `"$TGW_MODELS_DIR`"" -ForegroundColor Gray

# Create the junction
cmd /c "mklink /D `"$existingModelsDir`" `"$TGW_MODELS_DIR`""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Directory junction created successfully" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to create junction. Run as Administrator!" -ForegroundColor Red
}

# Start TGW normally (it will use the junction)
Write-Host "`nWith junction method, start TGW normally:" -ForegroundColor Cyan
Write-Host "python server.py --api --listen" -ForegroundColor Gray

Write-Host "`n=== VERIFICATION COMMANDS ===" -ForegroundColor Yellow
Write-Host "1. Check if models directory points to warehouse:"
Write-Host "   dir `"$existingModelsDir`"" -ForegroundColor Gray
Write-Host "2. Test API endpoint:"
Write-Host "   curl http://127.0.0.1:5000/v1/models" -ForegroundColor Gray
Write-Host "3. Check warehouse contents:"
Write-Host "   dir `"$TGW_MODELS_DIR`"" -ForegroundColor Gray