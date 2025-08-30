# Stage 1: Chat Modes & Chinese Character Cards Setup - FIXED VERSION
# Configures TGW for optimal Chinese conversation experience

$env:TGW_PLAYBOOK = 'C:\AI_LLM_projects\tgw-playbook'

param(
    [string]$PlaybookPath = $env:TGW_PLAYBOOK,
    [switch]$InstallPresets = $true,
    [switch]$InstallCharacters,
    [switch]$TestModes,
    [switch]$Verbose
)

$TGW_PLAYBOOK = $env:TGW_PLAYBOOK
if (-not $TGW_PLAYBOOK) {
    $TGW_PLAYBOOK = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}
if (-not (Test-Path $TGW_PLAYBOOK)) {
    throw "TGW_PLAYBOOK not found. Set `\$env:TGW_PLAYBOOK` or fix path. Current guess: $TGW_PLAYBOOK"
}

# Color output functions
function Write-Success($msg) { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Step($msg) { Write-Host "🔄 $msg" -ForegroundColor Magenta }

# Simple YAML conversion function
function ConvertTo-SimpleYaml {
    param([hashtable]$InputObject)

    $yaml = ""
    foreach ($key in $InputObject.Keys) {
        $value = $InputObject[$key]
        if ($value -is [string] -and ($value.Contains("`n") -or $value.Length -gt 50)) {
            # Multi-line string
            $yaml += "$key" + ": |`n"
            $lines = $value -split "`n"
            foreach ($line in $lines) {
                $yaml += "  $line`n"
            }
        } else {
            # Single line
            $yaml += "$key" + ': "' + $value.Replace('"', '\"') + '"' + "`n"
        }
    }
    return $yaml
}

Write-Host "🎭 Stage 1: Chat Modes & Chinese Character Cards Setup" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta

# Validate environment
if ([string]::IsNullOrEmpty($PlaybookPath) -or !(Test-Path $PlaybookPath)) {
    Write-Error "TGW Playbook path not found. Please set TGW_PLAYBOOK environment variable."
    Write-Info "Run: `$env:TGW_PLAYBOOK = 'C:\AI_LLM_projects\tgw-playbook'"
    exit 1
}

$TGW_REPO = $env:TGW_REPO
if (-not $env:TGW_REPO) {
    $env:TGW_REPO = 'C:\AI_LLM_projects\text-generation-webui'  # fallback
}
if (-not (Test-Path $env:TGW_REPO)) {
    throw "TGW_REPO not found: $($env:TGW_REPO)"
}

if ([string]::IsNullOrEmpty($TGW_REPO) -or !(Test-Path $TGW_REPO)) {
    Write-Error "TGW repository path not found. Please set TGW_REPO environment variable."
    Write-Info "Run: `$env:TGW_REPO = 'C:\AI_LLM_projects\text-generation-webui'"
    exit 1
}

Write-Info "Using paths:"
Write-Host "  Playbook: $PlaybookPath" -ForegroundColor Gray
Write-Host "  TGW Repo: $TGW_REPO" -ForegroundColor Gray

# =============================================================================
# Step 1: Install Chinese Presets
# =============================================================================
if ($InstallPresets) {
    Write-Step "Installing Chinese presets..."

    $presetsTargetDir = Join-Path $TGW_REPO "presets"

    # Ensure target directory exists
    if (!(Test-Path $presetsTargetDir)) {
        New-Item -ItemType Directory -Path $presetsTargetDir -Force | Out-Null
        Write-Info "Created presets directory: $presetsTargetDir"
    }

    # Create Chinese Reasoning preset
    $chineseReasoning = @{
        "temperature" = 0.6
        "top_p" = 0.85
        "top_k" = 30
        "min_p" = 0.02
        "repetition_penalty" = 1.05
        "presence_penalty" = 0.0
        "frequency_penalty" = 0.0
        "max_new_tokens" = 512
        "do_sample" = $true
        "add_bos_token" = $true
        "ban_eos_token" = $false
        "truncation_length" = 4096
    }

    $reasoningPath = Join-Path $presetsTargetDir "中文推理.json"
    try {
        $chineseReasoning | ConvertTo-Json -Depth 10 | Out-File -FilePath $reasoningPath -Encoding UTF8
        Write-Success "Created Chinese Reasoning preset: $reasoningPath"
    } catch {
        Write-Error "Failed to create reasoning preset: $($_.Exception.Message)"
    }

    # Create Chinese Creative preset
    $chineseCreative = @{
        "temperature" = 0.85
        "top_p" = 0.92
        "top_k" = 50
        "min_p" = 0.01
        "repetition_penalty" = 1.08
        "presence_penalty" = 0.1
        "frequency_penalty" = 0.05
        "max_new_tokens" = 800
        "do_sample" = $true
        "add_bos_token" = $true
        "ban_eos_token" = $false
        "truncation_length" = 4096
        "dynamic_temperature" = $true
        "dynatemp_low" = 0.7
        "dynatemp_high" = 1.0
    }

    $creativePath = Join-Path $presetsTargetDir "中文創作.json"
    try {
        $chineseCreative | ConvertTo-Json -Depth 10 | Out-File -FilePath $creativePath -Encoding UTF8
        Write-Success "Created Chinese Creative preset: $creativePath"
    } catch {
        Write-Error "Failed to create creative preset: $($_.Exception.Message)"
    }
}

# =============================================================================
# Step 2: Install Chinese Character Cards
# =============================================================================
if ($InstallCharacters) {
    Write-Step "Installing Chinese character cards..."

    $charactersTargetDir = Join-Path $TGW_REPO "characters"

    # Ensure target directory exists
    if (!(Test-Path $charactersTargetDir)) {
        New-Item -ItemType Directory -Path $charactersTargetDir -Force | Out-Null
        Write-Info "Created characters directory: $charactersTargetDir"
    }

    # Create 小雅 - Academic Assistant
    $xiaoYaContext = "
    小雅是一位專業的中文學術助理，具有豐富的知識背景和嚴謹的學術態度。她擅長：

    📚 **專業領域**:
    - 中文語言文學研究
    - 學術論文撰寫指導
    - 文獻檢索與整理
    - 研究方法論指導

    💭 **性格特點**:
    - 邏輯思維清晰，表達準確簡潔
    - 注重事實依據，避免主觀臆測
    - 耐心細緻，樂於解答學術問題
    - 使用正式但親切的中文表達

    🎯 **工作原則**:
    - 提供準確可靠的學術資訊
    - 引用權威來源支持觀點
    - 承認知識限制，不過度推測
    - 鼓勵批判性思維和獨立研究

    小雅會用專業而溫和的語氣回答問題，在解釋複雜概念時會使用清晰的邏輯結構和適當的舉例。
    "

    $xiaoYaGreeting = "
    您好！我是小雅，您的中文學術助理。我很高興能協助您進行學術研究和寫作。

    我可以幫助您：
    • 解答中文語言文學相關問題
    • 指導學術論文的結構和寫作
    • 分析文本和文獻資料
    • 討論研究方法和學術規範

    請告訴我您想討論的學術主題，我會盡力為您提供專業的見解和建議。
    "

    $xiaoYa = @{
        "name" = "小雅"
        "context" = $xiaoYaContext
        "greeting" = $xiaoYaGreeting
        "your_name" = "研究者"
    }

    $xiaoYaPath = Join-Path $charactersTargetDir "小雅-學術助理.yaml"
    try {
        $yamlContent = ConvertTo-SimpleYaml -InputObject $xiaoYa
        $yamlContent | Out-File -FilePath $xiaoYaPath -Encoding UTF8
        Write-Success "Created 小雅 Academic Assistant character: $xiaoYaPath"
    } catch {
        Write-Error "Failed to create 小雅 character: $($_.Exception.Message)"
    }

    # Create 文心 - Creative Writing Mentor
    $wenXinContext = "
    文心是一位充滿詩意和創造力的中文創作導師，對中華文化有著深厚的理解和熱愛。她的特色包括：

    🎨 **創作專長**：
    - 現代詩歌與古典詩詞創作
    - 散文寫作技巧指導
    - 小說情節構思與人物塑造
    - 創意寫作練習設計

    🌸 **文學素養**：
    - 精通古典文學與現代文學
    - 理解中文語言的韻律美感
    - 擅長運用修辭技巧和文學手法
    - 能夠點評作品的藝術價值

    💫 **教學風格**：
    - 鼓勵原創性和個人風格
    - 注重情感表達的真實性
    - 善於激發學生的創作靈感
    - 使用生動活潑的比喻和意象

    文心的回答充滿想像力和詩意，她會用溫暖而富有感染力的語言激發您的創作熱情。
    "

    $wenXinGreeting = "
    親愛的文友，我是文心～ 🌸

    在這個充滿可能的創作空間裡，讓我們一起探索中文寫作的無限魅力吧！

    我可以陪伴您：
    ✨ 創作詩歌，捕捉生活中的美妙瞬間
    📝 撰寫散文，記錄內心的真實感受
    📖 構思小說，編織引人入勝的故事
    🎭 練習對話，讓文字活靈活現

    無論您想寫什麼，分享什麼，我都會用心傾聽，用愛回應。讓我們開始這趟美妙的創作之旅吧～
    "

    $wenXin = @{
        "name" = "文心"
        "context" = $wenXinContext
        "greeting" = $wenXinGreeting
        "your_name" = "文友"
    }

    $wenXinPath = Join-Path $charactersTargetDir "文心-創作導師.yaml"
    try {
        $yamlContent = ConvertTo-SimpleYaml -InputObject $wenXin
        $yamlContent | Out-File -FilePath $wenXinPath -Encoding UTF8
        Write-Success "Created 文心 Creative Writing Mentor character: $wenXinPath"
    } catch {
        Write-Error "Failed to create 文心 character: $($_.Exception.Message)"
    }
}

# =============================================================================
# Step 3: Create Testing Instructions
# =============================================================================
if ($TestModes) {
    Write-Step "Creating testing instructions..."

    $stageDir = Join-Path $PlaybookPath "stages\stage1-chat-modes"
    if (!(Test-Path $stageDir)) {
        New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
    }

    $testInstructions = "
    # Stage 1 Testing Instructions

    ## 🧪 How to Test Chat Modes

    ### Step 1: Start TGW
    ```powershell
    cd `$env:TGW_REPO
    python server.py --model-dir `$env:TGW_MODELS_DIR --api --listen
    ```

    ### Step 2: Load Model
    1. Go to **Model tab**
    2. Select your Chinese model (e.g., Qwen2.5-7B-Instruct)
    3. Set loader to **llama.cpp**
    4. Click **Load**

    ### Step 3: Configure Chat Mode
    1. Go to **Chat tab**
    2. In **Mode** dropdown, select **chat-instruct**

    ### Step 4: Select Character
    1. Go to **Parameters tab** → **Character section**
    2. In **Character** dropdown, select **小雅-學術助理**

    ### Step 5: Load Preset
    1. In **Parameters tab** → **Generation section**
    2. In **Preset** dropdown, select **中文推理**

    ### Step 6: Test Questions
    Try these questions:
    - 請解釋機器學習的基本概念
    - 中文古詩詞有哪些主要的藝術特色？
    - 如何撰寫一篇結構完整的學術論文？

    ## 🎨 Creative Writing Test
    1. Change character to **文心-創作導師**
    2. Change preset to **中文創作**
    3. Try: "請幫我寫一首關於春天的現代詩"

    ## 📊 Quality Indicators
    ✅ **Good**: Natural Chinese, consistent character voice, logical structure
    ❌ **Poor**: English mixed in, out of character, repetitive content
    "

    $testPath = Join-Path $stageDir "TESTING.md"
    $testInstructions | Out-File -FilePath $testPath -Encoding UTF8
    Write-Success "Created testing instructions: $testPath"
}

# =============================================================================
# Summary
# =============================================================================
Write-Host ""
Write-Host "🎉 Stage 1 Setup Complete!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

if ($InstallPresets) {
    Write-Success "Chinese presets installed in: $(Join-Path $TGW_REPO 'presets')"
    Write-Host "  📄 中文推理.json (Conservative for Q&A)" -ForegroundColor Gray
    Write-Host "  📄 中文創作.json (Creative for writing)" -ForegroundColor Gray
}

if ($InstallCharacters) {
    Write-Success "Character cards installed in: $(Join-Path $TGW_REPO 'characters')"
    Write-Host "  👩‍🎓 小雅-學術助理.yaml (Academic assistant)" -ForegroundColor Gray
    Write-Host "  👩‍🎨 文心-創作導師.yaml (Creative mentor)" -ForegroundColor Gray
}

Write-Host ""
Write-Info "Next Steps:"
Write-Host "1. Start TGW and load a Chinese model" -ForegroundColor Cyan
Write-Host "2. Go to Chat tab → Mode → select 'chat-instruct'" -ForegroundColor Cyan
Write-Host "3. Parameters tab → Character → select a character" -ForegroundColor Cyan
Write-Host "4. Parameters tab → Preset → select a Chinese preset" -ForegroundColor Cyan
Write-Host "5. Start chatting in Chinese!" -ForegroundColor Cyan

if ($Verbose) {
    Write-Host ""
    Write-Info "Files created:"
    if ($InstallPresets) {
        Write-Host "  📁 TGW presets directory:" -ForegroundColor Gray
        Get-ChildItem (Join-Path $TGW_REPO "presets") -Filter "中文*.json" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "    📄 $($_.Name)" -ForegroundColor DarkGray
        }
    }
    if ($InstallCharacters) {
        Write-Host "  📁 TGW characters directory:" -ForegroundColor Gray
        Get-ChildItem (Join-Path $TGW_REPO "characters") -Filter "*助理*.yaml" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "    👤 $($_.Name)" -ForegroundColor DarkGray
        }
        Get-ChildItem (Join-Path $TGW_REPO "characters") -Filter "*導師*.yaml" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "    👤 $($_.Name)" -ForegroundColor DarkGray
        }
    }
}

exit 0