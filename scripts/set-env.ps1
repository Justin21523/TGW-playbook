# TGW Environment Variables Setup
# Source this script or add to your PowerShell profile

# AI Cache and Warehouse paths
$env:AI_CACHE_ROOT = "C:\AI_LLM_projects\ai_warehouse"
$env:HF_HOME = "$env:AI_CACHE_ROOT\cache\hf"
$env:TRANSFORMERS_CACHE = "$env:AI_CACHE_ROOT\cache\hf\transformers"
$env:HF_DATASETS_CACHE = "$env:AI_CACHE_ROOT\cache\hf\datasets"
$env:HUGGINGFACE_HUB_CACHE = "$env:AI_CACHE_ROOT\cache\hf\hub"
$env:TORCH_HOME = "$env:AI_CACHE_ROOT\cache\torch"

# TGW specific paths
$env:TGW_MODELS_DIR = "$env:AI_CACHE_ROOT\cache\models\llm"
$env:TGW_REPO = "C:\AI_LLM_projects\text-generation-webui"
$env:TGW_PLAYBOOK = "C:\AI_LLM_projects\tgw-playbook"

Write-Host "Environment variables set for TGW project" -ForegroundColor Green
Write-Host "AI_CACHE_ROOT: $env:AI_CACHE_ROOT" -ForegroundColor Cyan
Write-Host "TGW_MODELS_DIR: $env:TGW_MODELS_DIR" -ForegroundColor Cyan
