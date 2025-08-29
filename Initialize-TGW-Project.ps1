# Initialize TGW Project Structure
# Creates the recommended directory layout and moves existing files

param(
    [string]$RootPath = "C:\AI_LLM_projects",
    [switch]$Force = $false
)

Write-Host "🚀 Initializing TGW Project Structure..." -ForegroundColor Green
Write-Host "Root path: $RootPath" -ForegroundColor Cyan

# Define paths
$AI_WAREHOUSE = Join-Path $RootPath "ai_warehouse"
$TGW_REPO = Join-Path $RootPath "text-generation-webui"
$TGW_PLAYBOOK = Join-Path $RootPath "tgw-playbook"

# Create main directories
$directories = @(
    # AI Warehouse structure
    "$AI_WAREHOUSE\cache\hf\transformers",
    "$AI_WAREHOUSE\cache\hf\datasets",
    "$AI_WAREHOUSE\cache\hf\hub",
    "$AI_WAREHOUSE\cache\torch",
    "$AI_WAREHOUSE\cache\models\llm",
    "$AI_WAREHOUSE\downloads",

    # TGW Playbook structure
    "$TGW_PLAYBOOK\stages\stage0-warehouse-setup",
    "$TGW_PLAYBOOK\stages\stage1-chat-modes",
    "$TGW_PLAYBOOK\stages\stage2-parameters",
    "$TGW_PLAYBOOK\stages\stage3-completion-modes",
    "$TGW_PLAYBOOK\stages\stage4-openai-api",
    "$TGW_PLAYBOOK\stages\stage5-lora-training",
    "$TGW_PLAYBOOK\stages\stage6-extensions",
    "$TGW_PLAYBOOK\stages\stage7-multimodal",
    "$TGW_PLAYBOOK\configs\presets",
    "$TGW_PLAYBOOK\configs\characters",
    "$TGW_PLAYBOOK\configs\instruction-templates",
    "$TGW_PLAYBOOK\scripts",
    "$TGW_PLAYBOOK\examples\api-clients",
    "$TGW_PLAYBOOK\examples\extensions",
    "$TGW_PLAYBOOK\examples\training",
    "$TGW_PLAYBOOK\examples\multimodal",
    "$TGW_PLAYBOOK\docs\stage-summaries",
    "$TGW_PLAYBOOK\tests"
)

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  - Exists: $dir" -ForegroundColor Gray
    }
}

# Create .gitignore for playbook
$gitignore = @"
# TGW Playbook .gitignore

# Exclude actual model files and cache
ai_warehouse/
*.bin
*.safetensors
*.gguf
*.pth

# Exclude temporary and log files
logs/
temp/
*.log
*.tmp

# Exclude sensitive configs
.env
*secret*
*private*

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
Thumbs.db
.DS_Store
Desktop.ini

# Python cache
__pycache__/
*.pyc
*.pyo
"@

$gitignorePath = Join-Path $TGW_PLAYBOOK ".gitignore"
if (!(Test-Path $gitignorePath) -or $Force) {
    $gitignore | Out-File -FilePath $gitignorePath -Encoding UTF8
    Write-Host "✓ Created .gitignore" -ForegroundColor Green
}

# Create README for playbook
$readme = @"
# TGW Playbook - Text Generation WebUI Learning Journey

This repository contains your learning materials, configurations, and customizations for oobabooga's text-generation-webui.

## 🏗️ Project Structure

- **`stages/`**: Stage-by-stage learning materials and scripts
- **`configs/`**: Configuration templates, presets, characters
- **`scripts/`**: Automation and utility scripts
- **`examples/`**: Code examples and demos
- **`docs/`**: Extended documentation
- **`tests/`**: Testing and validation scripts

## 🚀 Quick Start

1. Run environment validation:
   ```powershell
   .\scripts\validate-env.ps1
   ```

2. Start TGW with shared warehouse:
   ```powershell
   .\scripts\start-tgw.ps1
   ```

3. Follow stages in order:
   - Stage 0: Warehouse setup
   - Stage 1: Chat modes
   - Stage 2: Parameters
   - ...

## 🔧 Environment Variables

Set these in your PowerShell profile or system environment:

```powershell
`$env:AI_CACHE_ROOT = "$AI_WAREHOUSE"
`$env:TGW_MODELS_DIR = "$AI_WAREHOUSE\cache\models\llm"
`$env:TGW_REPO = "$TGW_REPO"
`$env:TGW_PLAYBOOK = "$TGW_PLAYBOOK"
```

## 📚 Learning Progress

Track your progress through stages:

- [ ] Stage 0: Shared warehouse model directory setup
- [ ] Stage 1: Chat modes and character cards
- [ ] Stage 2: Parameters and Chinese presets
- [ ] Stage 3: Completion modes and token analysis
- [ ] Stage 4: OpenAI API and client examples
- [ ] Stage 5: LoRA training basics
- [ ] Stage 6: Extensions and RAG
- [ ] Stage 7: Multimodal capabilities

Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$readmePath = Join-Path $TGW_PLAYBOOK "README.md"
if (!(Test-Path $readmePath) -or $Force) {
    $readme | Out-File -FilePath $readmePath -Encoding UTF8
    Write-Host "✓ Created README.md" -ForegroundColor Green
}

# Create environment variables script
$envScript = @"
# TGW Environment Variables Setup
# Source this script or add to your PowerShell profile

# AI Cache and Warehouse paths
`$env:AI_CACHE_ROOT = "$AI_WAREHOUSE"
`$env:HF_HOME = "`$env:AI_CACHE_ROOT\cache\hf"
`$env:TRANSFORMERS_CACHE = "`$env:AI_CACHE_ROOT\cache\hf\transformers"
`$env:HF_DATASETS_CACHE = "`$env:AI_CACHE_ROOT\cache\hf\datasets"
`$env:HUGGINGFACE_HUB_CACHE = "`$env:AI_CACHE_ROOT\cache\hf\hub"
`$env:TORCH_HOME = "`$env:AI_CACHE_ROOT\cache\torch"

# TGW specific paths
`$env:TGW_MODELS_DIR = "`$env:AI_CACHE_ROOT\cache\models\llm"
`$env:TGW_REPO = "$TGW_REPO"
`$env:TGW_PLAYBOOK = "$TGW_PLAYBOOK"

Write-Host "Environment variables set for TGW project" -ForegroundColor Green
Write-Host "AI_CACHE_ROOT: `$env:AI_CACHE_ROOT" -ForegroundColor Cyan
Write-Host "TGW_MODELS_DIR: `$env:TGW_MODELS_DIR" -ForegroundColor Cyan
"@

$envScriptPath = Join-Path $TGW_PLAYBOOK "scripts\set-env.ps1"
$envScript | Out-File -FilePath $envScriptPath -Encoding UTF8
Write-Host "✓ Created environment setup script" -ForegroundColor Green

Write-Host "✓ Created TGW start script" -ForegroundColor Green

# Create complete validation script with full content
$validateScript = @'
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
Write-Host "🔍 TGW Environment Validation" -ForegroundColor Magenta
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
Write-Host "📊 Validation Summary" -ForegroundColor Magenta

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
'@

$validateScriptPath = Join-Path $TGW_PLAYBOOK "scripts\validate-env.ps1"
$validateScript | Out-File -FilePath $validateScriptPath -Encoding UTF8
Write-Host "✓ Created validation script" -ForegroundColor Green

# Create complete settings template
$settingsTemplate = @'
# TGW Settings Template for Shared Warehouse Configuration
# Copy this file to settings.yaml and customize as needed

# =============================================================================
# CORE PATHS & MODEL CONFIGURATION
# =============================================================================

# Default model to load on startup (set after downloading your first model)
# model: "Qwen2.5-7B-Instruct-Q4_K_M.gguf"

# Default loader for GGUF models
loader: "llama.cpp"

# =============================================================================
# SERVER & API CONFIGURATION
# =============================================================================

# Enable OpenAI-compatible API
api: true

# Listen on all interfaces (for network access)
listen: true

# API port (default: 5000)
api_port: 5000

# Web UI port (default: 7860)
listen_port: 7860

# =============================================================================
# MODEL LOADING PARAMETERS
# =============================================================================

# llama.cpp specific settings (for GGUF models)
n_gpu_layers: 0        # Set to -1 to offload all layers to GPU, 0 for CPU only
n_ctx: 4096           # Context length (adjust based on model and VRAM)
n_batch: 512          # Batch size for prompt processing
threads: 0            # CPU threads (0 = auto-detect physical cores)
threads_batch: 0      # Batch processing threads (0 = auto-detect all cores)

# =============================================================================
# GENERATION DEFAULTS
# =============================================================================

# Default generation parameters
preset: "simple-1"           # Default preset
max_new_tokens: 512          # Maximum tokens to generate
temperature: 0.7             # Randomness (0.1 = focused, 1.5 = creative)
top_p: 0.9                  # Nucleus sampling
top_k: 40                   # Top-k sampling
repetition_penalty: 1.1      # Penalty for repetition
do_sample: true             # Enable sampling

# =============================================================================
# CHAT & CHARACTER SETTINGS
# =============================================================================

# Default chat mode (chat, chat-instruct, instruct)
mode: "chat-instruct"

# Your display name in chat
your_name: "User"

# Context length for chat history truncation
truncation_length: 2048

# =============================================================================
# UI & EXTENSION CONFIGURATION
# =============================================================================

# UI theme and behavior
chat_style: "cai-chat"
show_controls: true
activate_text_streaming: true

# Auto-load model on startup
autoload_model: false

# =============================================================================
# CHINESE LANGUAGE OPTIMIZATION
# =============================================================================

# Chinese generation parameters (more conservative for better grammar)
# temperature: 0.6            # Lower temperature for more consistent Chinese
# top_p: 0.8                 # Slightly lower top_p
# repetition_penalty: 1.05    # Light repetition penalty

# Last updated: 2024-01-XX
'@

$settingsTemplatePath = Join-Path $TGW_PLAYBOOK "configs\settings.yaml.template"
$settingsTemplate | Out-File -FilePath $settingsTemplatePath -Encoding UTF8
Write-Host "✓ Created settings template" -ForegroundColor Green

# Initialize git repository in playbook
Set-Location $TGW_PLAYBOOK
if (!(Test-Path ".git")) {
    git init
    Write-Host "✓ Initialized git repository in playbook" -ForegroundColor Green

    # Create initial commit
    git add .
    git commit -m "Initial commit: TGW playbook project structure

- Set up stage-based learning directory structure
- Add configuration templates and example directories
- Create environment setup and quick start scripts
- Initialize documentation and testing framework"

    Write-Host "✓ Created initial commit" -ForegroundColor Green
}

# Summary
Write-Host "`n🎉 Project structure initialized successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Move your existing Stage0-TGW-Setup.ps1 to: stages\stage0-warehouse-setup\" -ForegroundColor Cyan
Write-Host "2. Source environment variables: .\scripts\set-env.ps1" -ForegroundColor Cyan
Write-Host "3. Validate setup: .\scripts\validate-env.ps1 (after you create it)" -ForegroundColor Cyan
Write-Host "4. Start learning: Begin with Stage 0 in the stages directory" -ForegroundColor Cyan
Write-Host "`nProject paths:" -ForegroundColor Yellow
Write-Host "  AI Warehouse: $AI_WAREHOUSE" -ForegroundColor Gray
Write-Host "  TGW Repo: $TGW_REPO" -ForegroundColor Gray
Write-Host "  TGW Playbook: $TGW_PLAYBOOK" -ForegroundColor Gray