# Stage 2: Advanced Parameter Tuning & Chinese Optimization
# Creates task-specific presets and provides parameter analysis tools

param(
    [string]$PlaybookPath = $env:TGW_PLAYBOOK,
    [string]$TGWPath = $env:TGW_REPO,
    [switch]$InstallAdvancedPresets = $true,
    [switch]$CreateAnalysisTools = $true,
    [switch]$RunParameterTests = $false,
    [switch]$Verbose = $false
)

# Color output functions
function Write-Success($msg) { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Step($msg) { Write-Host "🔄 $msg" -ForegroundColor Magenta }

Write-Host "🎛️ Stage 2: Advanced Parameter Tuning & Chinese Optimization" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta

# Validate environment
if ([string]::IsNullOrEmpty($PlaybookPath) -or !(Test-Path $PlaybookPath)) {
    Write-Error "TGW Playbook path not found. Please set TGW_PLAYBOOK environment variable."
    exit 1
}

if ([string]::IsNullOrEmpty($TGWPath) -or !(Test-Path $TGWPath)) {
    Write-Error "TGW repository path not found. Please set TGW_REPO environment variable."
    exit 1
}

Write-Info "Using paths:"
Write-Host "  Playbook: $PlaybookPath" -ForegroundColor Gray
Write-Host "  TGW Repo: $TGWPath" -ForegroundColor Gray

# =============================================================================
# Step 1: Install Advanced Chinese Presets
# =============================================================================
if ($InstallAdvancedPresets) {
    Write-Step "Installing advanced Chinese presets..."

    $presetsDir = Join-Path $TGWPath "presets"
    if (!(Test-Path $presetsDir)) {
        New-Item -ItemType Directory -Path $presetsDir -Force | Out-Null
    }

    # Define advanced presets with detailed parameter explanations
    $advancedPresets = @{
        "中文技術文檔" = @{
            "temperature" = 0.3
            "top_p" = 0.75
            "top_k" = 20
            "min_p" = 0.05
            "repetition_penalty" = 1.02
            "mirostat_mode" = 2
            "mirostat_tau" = 3.5
            "mirostat_eta" = 0.05
            "temperature_last" = $true
            "max_new_tokens" = 1024
            "truncation_length" = 8192
            "sampler_priority" = @("top_k", "tfs", "typical_p", "top_p", "min_p", "mirostat", "temperature")
            "description" = "專為中文技術文檔設計的極保守參數。使用 mirostat 2 確保一致性，temperature_last 避免低概率詞彙。"
        }

        "中文對話聊天" = @{
            "temperature" = 0.75
            "top_p" = 0.88
            "top_k" = 35
            "min_p" = 0.02
            "repetition_penalty" = 1.08
            "presence_penalty" = 0.3
            "frequency_penalty" = 0.1
            "dynamic_temperature" = $true
            "dynatemp_low" = 0.6
            "dynatemp_high" = 0.9
            "dynatemp_exponent" = 1.3
            "smoothing_factor" = 0.15
            "max_new_tokens" = 600
            "description" = "針對中文日常對話優化的動態參數。使用動態溫度增加自然變化，presence/frequency penalty 避免重複。"
        }

        "中文學術分析" = @{
            "temperature" = 0.45
            "top_p" = 0.82
            "top_k" = 25
            "min_p" = 0.03
            "repetition_penalty" = 1.03
            "mirostat_mode" = 1
            "mirostat_tau" = 4.0
            "mirostat_eta" = 0.08
            "epsilon_cutoff" = 3.0
            "eta_cutoff" = 2.5
            "max_new_tokens" = 800
            "description" = "為中文學術分析特調的平衡參數。使用 mirostat 1 和 epsilon/eta cutoff 確保邏輯一致性。"
        }

        "中文詩詞創作" = @{
            "temperature" = 1.1
            "top_p" = 0.95
            "top_k" = 60
            "min_p" = 0.008
            "repetition_penalty" = 1.12
            "presence_penalty" = 0.2
            "frequency_penalty" = 0.15
            "dynamic_temperature" = $true
            "dynatemp_low" = 0.8
            "dynatemp_high" = 1.3
            "dynatemp_exponent" = 1.5
            "smoothing_factor" = 0.25
            "max_new_tokens" = 400
            "description" = "專為中文詩詞創作設計的高創意參數。高溫度配合動態調節增加靈感，較高重複懲罰確保用詞豐富。"
        }

        "中文程式註解" = @{
            "temperature" = 0.25
            "top_p" = 0.7
            "top_k" = 15
            "min_p" = 0.08
            "repetition_penalty" = 1.01
            "mirostat_mode" = 2
            "mirostat_tau" = 2.8
            "mirostat_eta" = 0.03
            "epsilon_cutoff" = 5.0
            "eta_cutoff" = 4.0
            "temperature_last" = $true
            "max_new_tokens" = 256
            "description" = "為中文程式碼註解優化的超保守參數。極低溫度確保術語準確，強 epsilon/eta cutoff 避免錯誤表達。"
        }

        "中文故事續寫" = @{
            "temperature" = 0.9
            "top_p" = 0.9
            "top_k" = 45
            "min_p" = 0.015
            "repetition_penalty" = 1.1
            "presence_penalty" = 0.25
            "frequency_penalty" = 0.2
            "dynamic_temperature" = $true
            "dynatemp_low" = 0.75
            "dynatemp_high" = 1.05
            "smoothing_factor" = 0.2
            "max_new_tokens" = 1200
            "description" = "針對中文故事續寫調優的創意平衡參數。動態溫度增加情節變化，penalty 確保角色豐富性。"
        }
    }

    # Create preset files
    foreach ($presetName in $advancedPresets.Keys) {
        $presetData = $advancedPresets[$presetName]
        $presetPath = Join-Path $presetsDir "$presetName.json"

        try {
            $presetData | ConvertTo-Json -Depth 10 | Out-File -FilePath $presetPath -Encoding UTF8
            Write-Success "Created advanced preset: $presetName"

            if ($Verbose) {
                Write-Host "  📄 File: $presetPath" -ForegroundColor Gray
                Write-Host "  📝 Description: $($presetData.description)" -ForegroundColor Gray
            }
        } catch {
            Write-Error "Failed to create preset $presetName`: $($_.Exception.Message)"
        }
    }
}

# =============================================================================
# Step 2: Create Parameter Analysis Tools
# =============================================================================
if ($CreateAnalysisTools) {
    Write-Step "Creating parameter analysis tools..."

    $toolsDir = Join-Path $PlaybookPath "stages\stage2-parameters\tools"
    if (!(Test-Path $toolsDir)) {
        New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    }

    # Parameter comparison tool
    $comparisonTool = @'
# Parameter Comparison Tool
# Analyzes differences between presets and suggests optimal combinations

param(
    [string]$Preset1 = "中文推理",
    [string]$Preset2 = "中文創作",
    [switch]$ShowDetails = $false
)

$presetsDir = Join-Path $env:TGW_REPO "presets"

function Compare-Presets {
    param($preset1Path, $preset2Path, $name1, $name2)

    if (!(Test-Path $preset1Path) -or !(Test-Path $preset2Path)) {
        Write-Error "Preset files not found"
        return
    }

    $p1 = Get-Content $preset1Path | ConvertFrom-Json
    $p2 = Get-Content $preset2Path | ConvertFrom-Json

    Write-Host "🔍 Comparing $name1 vs $name2" -ForegroundColor Cyan
    Write-Host "=" * 50

    $keyParams = @("temperature", "top_p", "top_k", "min_p", "repetition_penalty",
                   "mirostat_mode", "mirostat_tau", "dynamic_temperature")

    foreach ($param in $keyParams) {
        $val1 = if ($p1.PSObject.Properties.Name -contains $param) { $p1.$param } else { "N/A" }
        $val2 = if ($p2.PSObject.Properties.Name -contains $param) { $p2.$param } else { "N/A" }

        $color = if ($val1 -eq $val2) { "Gray" } else { "Yellow" }
        Write-Host "  $param`: $val1 → $val2" -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "💡 Analysis:" -ForegroundColor Green

    if ($p1.temperature -lt $p2.temperature) {
        Write-Host "  • $name1 更保守 (低溫度)，$name2 更創意 (高溫度)" -ForegroundColor White
    }

    if ($p1.PSObject.Properties.Name -contains "mirostat_mode" -and $p1.mirostat_mode -gt 0) {
        Write-Host "  • $name1 使用 Mirostat 自適應採樣，確保一致性" -ForegroundColor White
    }

    if ($p2.PSObject.Properties.Name -contains "dynamic_temperature" -and $p2.dynamic_temperature) {
        Write-Host "  • $name2 使用動態溫度，增加自然變化" -ForegroundColor White
    }
}

$preset1Path = Join-Path $presetsDir "$Preset1.json"
$preset2Path = Join-Path $presetsDir "$Preset2.json"

Compare-Presets $preset1Path $preset2Path $Preset1 $Preset2

Write-Host ""
Write-Host "🚀 Quick Test Commands:" -ForegroundColor Magenta
Write-Host "  Test $Preset1`: 請解釋量子物理的基本原理" -ForegroundColor Gray
Write-Host "  Test $Preset2`: 寫一首關於春天的現代詩" -ForegroundColor Gray
'@

    $comparisonPath = Join-Path $toolsDir "Compare-Presets.ps1"
    $comparisonTool | Out-File -FilePath $comparisonPath -Encoding UTF8
    Write-Success "Created preset comparison tool"

    # Parameter optimization guide
    $optimizationGuide = @'
# Chinese Parameter Optimization Guide

## 🎯 Parameter Effects on Chinese Generation

### Core Sampling Parameters

**Temperature (溫度)**
- 0.1-0.4: 事實性問答、技術文檔 (保守穩定)
- 0.5-0.7: 學術討論、分析思考 (平衡理性)
- 0.8-1.2: 創意寫作、詩詞創作 (靈活創意)
- 1.3+: 實驗性創作、腦力激盪 (高度隨機)

**Top-P (核採樣)**
- 0.7-0.8: 技術、正式文檔 (詞彙精準)
- 0.85-0.92: 一般對話、分析 (自然流暢)
- 0.95+: 創意寫作 (詞彙豐富)

**Min-P (最小機率閾值)**
- 0.05+: 技術文檔 (避免低頻詞彙錯誤)
- 0.02-0.04: 一般應用 (平衡準確性與多樣性)
- 0.01-: 創意寫作 (允許罕見但合適的詞彙)

### Advanced Samplers for Chinese

**Mirostat (自適應採樣)**
- Mode 1: 適合長文分析，保持邏輯連貫
- Mode 2: 適合技術文檔，嚴格控制輸出質量
- Tau 值: 2-4 (保守), 4-6 (平衡), 6-8 (創意)

**Dynamic Temperature (動態溫度)**
- 增加自然變化，避免機械式回答
- Low: 基礎溫度，High: 峰值溫度
- 適合對話、故事等需要變化的場景

**Quadratic Sampling (二次採樣)**
- Smoothing factor 0.1-0.3
- 增加採樣分佈的平滑度
- 適合創意寫作和詩詞創作

### Chinese-Specific Considerations

**中文 Token 特性**
- 中文字符密度高，同樣長度包含更多信息
- 調低 max_new_tokens，提高 truncation_length
- 重複懲罰要適中，避免破壞語法結構

**語法與文化因素**
- Presence penalty 控制話題豐富度
- Frequency penalty 避免詞彙重複
- 考慮中文的語序和修辭習慣

## 🧪 Testing Methodology

### A/B Testing Process
1. 選擇基準預設 (如"中文推理")
2. 調整單一參數
3. 使用標準測試問題
4. 記錄輸出質量評分
5. 比較並保存最佳組合

### Standard Test Questions
**事實性**: "請解釋人工智能的基本概念"
**分析性**: "分析《紅樓夢》中賈寶玉的人物形象"
**創意性**: "寫一首關於秋天的現代詩"
**技術性**: "解釋 HTTP 協議的工作原理"

### Quality Metrics
- **流暢度** (1-5): 語言自然程度
- **準確性** (1-5): 事實正確性
- **相關性** (1-5): 回答切題程度
- **創意性** (1-5): 表達豐富程度
- **一致性** (1-5): 風格統一程度

Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
'@

    $guidePath = Join-Path $toolsDir "Chinese-Parameter-Guide.md"
    $optimizationGuide | Out-File -FilePath $guidePath -Encoding UTF8
    Write-Success "Created parameter optimization guide"

    # Quality assessment tool
    $assessmentTool = @'
# Chinese Generation Quality Assessment Tool
# Provides structured evaluation of model outputs

param(
    [string]$TestPrompt = "請解釋什麼是人工智能？",
    [string]$PresetName = "中文推理",
    [int]$NumTests = 3
)

function Invoke-QualityAssessment {
    param($prompt, $preset, $iterations)

    Write-Host "🧪 Quality Assessment for Preset: $preset" -ForegroundColor Cyan
    Write-Host "📝 Test Prompt: $prompt" -ForegroundColor Gray
    Write-Host "🔁 Iterations: $iterations"
    Write-Host "=" * 60

    for ($i = 1; $i -le $iterations; $i++) {
        Write-Host "Test $i/$iterations" -ForegroundColor Yellow
        Write-Host "-" * 30

        # Instructions for manual testing
        Write-Host "1. Set preset to: $preset" -ForegroundColor White
        Write-Host "2. Input prompt: $prompt" -ForegroundColor White
        Write-Host "3. Generate response" -ForegroundColor White
        Write-Host "4. Rate the output (1-5 scale):" -ForegroundColor White

        Write-Host "   📝 流暢度 (Fluency): " -NoNewline -ForegroundColor Cyan
        $fluency = Read-Host

        Write-Host "   🎯 準確性 (Accuracy): " -NoNewline -ForegroundColor Cyan
        $accuracy = Read-Host

        Write-Host "   🔗 相關性 (Relevance): " -NoNewline -ForegroundColor Cyan
        $relevance = Read-Host

        Write-Host "   🎨 創意性 (Creativity): " -NoNewline -ForegroundColor Cyan
        $creativity = Read-Host

        Write-Host "   📏 一致性 (Consistency): " -NoNewline -ForegroundColor Cyan
        $consistency = Read-Host

        # Calculate average
        $scores = @($fluency, $accuracy, $relevance, $creativity, $consistency)
        $average = ($scores | Measure-Object -Average).Average

        Write-Host "   📊 Average Score: $([math]::Round($average, 2))" -ForegroundColor Green
        Write-Host ""

        # Log results
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$preset,$prompt,$fluency,$accuracy,$relevance,$creativity,$consistency,$([math]::Round($average, 2))"
        $logPath = Join-Path $env:TGW_PLAYBOOK "stages\stage2-parameters\quality-log.csv"

        if (!(Test-Path $logPath)) {
            "Timestamp,Preset,Prompt,Fluency,Accuracy,Relevance,Creativity,Consistency,Average" | Out-File $logPath -Encoding UTF8
        }
        $logEntry | Out-File $logPath -Append -Encoding UTF8
    }

    Write-Host "✅ Assessment completed. Results logged to quality-log.csv" -ForegroundColor Green
}

Invoke-QualityAssessment $TestPrompt $PresetName $NumTests
'@

    $assessmentPath = Join-Path $toolsDir "Assess-Quality.ps1"
    $assessmentTool | Out-File -FilePath $assessmentPath -Encoding UTF8
    Write-Success "Created quality assessment tool"
}

# =============================================================================
# Step 3: Create Parameter Testing Framework
# =============================================================================
if ($RunParameterTests) {
    Write-Step "Setting up parameter testing framework..."

    $testingDir = Join-Path $PlaybookPath "stages\stage2-parameters\testing"
    if (!(Test-Path $testingDir)) {
        New-Item -ItemType Directory -Path $testingDir -Force | Out-Null
    }

    # Create test scenarios
    $testScenarios = @{
        "技術問答" = @(
            "請解釋機器學習的基本概念和應用領域",
            "HTTP 和 HTTPS 協議有什麼差異？",
            "什麼是雲計算？它有哪些優勢和挑戰？"
        )
        "學術分析" = @(
            "分析《詩經》中的愛情主題及其文學價值",
            "比較中西方教育制度的差異及其影響",
            "探討人工智能對未來就業市場的衝擊"
        )
        "創意寫作" = @(
            "寫一首關於城市夜景的現代詩",
            "創作一個關於時間旅行的短篇故事開頭",
            "描述你心目中理想的未來世界"
        )
        "日常對話" = @(
            "聊聊你對最近天氣變化的看法",
            "推薦幾部值得看的電影並說明理由",
            "分享一些提高工作效率的小技巧"
        )
    }

    $scenariosJson = $testScenarios | ConvertTo-Json -Depth 3
    $scenariosPath = Join-Path $testingDir "test-scenarios.json"
    $scenariosJson | Out-File -FilePath $scenariosPath -Encoding UTF8
    Write-Success "Created test scenarios"

    # Create batch testing script
    $batchTester = '
    # Batch Parameter Testing Script
    # Systematically tests presets against scenarios

    param(
        [string[]]$Presets = @("中文推理", "中文創作", "中文技術文檔", "中文對話聊天"),
        [string]$ScenarioType = "技術問答"
    )

    $scenariosPath = Join-Path $PSScriptRoot "test-scenarios.json"
    if (!(Test-Path $scenariosPath)) {
        Write-Error "Test scenarios file not found"
        exit 1
    }

    $scenarios = Get-Content $scenariosPath | ConvertFrom-Json

    if (!$scenarios.$ScenarioType) {
        Write-Error "Scenario type '$ScenarioType' not found"
        Write-Host "Available types: $($scenarios.PSObject.Properties.Name -join ', ')" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "🚀 Batch Testing: $ScenarioType" -ForegroundColor Magenta
    Write-Host "🎛️ Presets: $($Presets -join ', ')" -ForegroundColor Cyan
    Write-Host "=" * 60

    foreach ($preset in $Presets) {
        Write-Host "Testing preset: $preset" -ForegroundColor Yellow
        Write-Host "-" * 30

        foreach ($question in $scenarios.$ScenarioType) {
            Write-Host "📝 Question: $question" -ForegroundColor White
            Write-Host "⚙️  Preset: $preset" -ForegroundColor Gray
            Write-Host "🎯 Instructions:" -ForegroundColor Green
            Write-Host "   1. Load preset '$preset' in TGW UI"
            Write-Host "   2. Input the question above"
            Write-Host "   3. Generate response"
            Write-Host "   4. Note quality and characteristics"
            Write-Host ""

            Read-Host "Press Enter to continue to next test..."
            Write-Host ""
        }

        Write-Host "✅ Completed testing for $preset" -ForegroundColor Green
        Write-Host ""
    }

    Write-Host "🎉 All testing completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Review responses and identify best preset-scenario combinations"
    Write-Host "2. Use .\tools\Assess-Quality.ps1 for detailed evaluation"
    Write-Host "3. Create custom presets based on findings"
    '

    $batchTesterPath = Join-Path $testingDir "Batch-Test.ps1"
    $batchTester | Out-File -FilePath $batchTesterPath -Encoding UTF8
    Write-Success "Created batch testing script"
}

# =============================================================================
# Step 4: Create Documentation
# =============================================================================
Write-Step "Creating Stage 2 documentation..."

$stageDir = Join-Path $PlaybookPath "stages\stage2-parameters"
if (!(Test-Path $stageDir)) {
    New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
}

$documentation = "
# Stage 2: Advanced Parameter Tuning & Chinese Optimization

## 🎯 Overview

Stage 2 focuses on advanced parameter tuning specifically optimized for Chinese language generation. We move beyond basic temperature/top_p settings to explore sophisticated sampling techniques like Mirostat, dynamic temperature, and quadratic sampling.

## 📦 Installed Presets

### Task-Specific Chinese Presets

| Preset | Use Case | Key Features |
|--------|----------|--------------|
| **中文技術文檔** | Technical documentation | Mirostat 2, low temp, high precision |
| **中文對話聊天** | Conversational chat | Dynamic temp, presence penalty |
| **中文學術分析** | Academic analysis | Mirostat 1, epsilon/eta cutoff |
| **中文詩詞創作** | Poetry & literature | High temp, quadratic sampling |
| **中文程式註解** | Code comments | Ultra-low temp, strict constraints |
| **中文故事續寫** | Story continuation | Balanced creativity, penalty tuning |

## 🔧 How to Use

### 1. Load Advanced Presets
```
Parameters tab → Generation section → Preset dropdown → Select preset
```

### 2. Understanding Parameter Combinations

**Conservative Stack (技術文檔)**:
- Low temperature (0.25-0.4)
- Mirostat mode 2 for consistency
- temperature_last = true
- Strong epsilon/eta cutoff

**Creative Stack (詩詞創作)**:
- High temperature (0.9-1.2)
- Dynamic temperature enabled
- Quadratic sampling (smoothing_factor > 0)
- Higher repetition penalties

**Balanced Stack (學術分析)**:
- Medium temperature (0.4-0.6)
- Mirostat mode 1
- Moderate sampling constraints
- Epsilon/eta cutoff for quality

### 3. Testing and Optimization

**Use Analysis Tools**:
```powershell
# Compare presets
.\tools\Compare-Presets.ps1 -Preset1 "中文推理" -Preset2 "中文技術文檔"

# Quality assessment
.\tools\Assess-Quality.ps1 -TestPrompt "您的測試問題" -PresetName "中文學術分析"

# Batch testing
.\testing\Batch-Test.ps1 -Presets @("中文推理", "中文創作") -ScenarioType "學術分析"
```

## 📊 Parameter Deep Dive

### Advanced Sampling Explained

**Mirostat Adaptive Sampling**
- Maintains target perplexity (tau value)
- Mode 1: Classic algorithm, good for analysis
- Mode 2: Improved stability, ideal for technical content
- Eta: Learning rate for perplexity adjustment

**Dynamic Temperature**
- Varies temperature based on context uncertainty
- Low/High range defines temperature bounds
- Exponent controls curve steepness
- Excellent for natural conversation flow

**Min-P Sampling**
- Minimum probability threshold relative to top token
- More stable than top_p for technical content
- Higher values = more conservative
- Better than top_k for Chinese due to token distribution

**Quadratic Sampling**
- Smooths probability distribution
- Smoothing factor 0.1-0.3 typical
- Reduces extreme peaks/valleys
- Enhances creative coherence

### Chinese Language Considerations

**Token Density**
- Chinese characters pack more meaning per token
- Reduce max_new_tokens, increase truncation_length
- Adjust repetition penalty ranges accordingly

**Grammar Structure**
- Chinese grammar more flexible than English
- Lower repetition penalties to preserve natural flow
- Use presence_penalty for topic diversity

**Cultural Context**
- Different temperature ranges work better for Chinese
- Cultural expressions need creative freedom
- Technical terms require precision

## 🧪 Quality Assessment Framework

### Evaluation Dimensions
1. **流暢度 (Fluency)**: Natural Chinese expression
2. **準確性 (Accuracy)**: Factual correctness
3. **相關性 (Relevance)**: Answers the question
4. **創意性 (Creativity)**: Original expression
5. **一致性 (Consistency)**: Maintains style/tone

### Testing Methodology
1. Select baseline preset
2. Modify single parameter
3. Test with standard questions
4. Rate outputs 1-5 scale
5. Log results for analysis

## 🎨 Preset Customization Guide

### Creating Custom Presets

**Step 1: Start with Base**
- Copy existing preset closest to your needs
- Identify primary use case and constraints

**Step 2: Iterative Tuning**
- Adjust one parameter at a time
- Test extensively before next change
- Document changes and rationale

**Step 3: Validation**
- Test across multiple scenarios
- Compare against existing presets
- Gather feedback from multiple users

### Common Adjustments

**Too Conservative?**
- Increase temperature by 0.1-0.2
- Lower min_p threshold
- Reduce mirostat tau value

**Too Random?**
- Decrease temperature
- Enable mirostat mode 2
- Increase min_p threshold

**Too Repetitive?**
- Increase repetition_penalty
- Add presence_penalty
- Enable frequency_penalty

**Not Creative Enough?**
- Enable dynamic_temperature
- Add quadratic sampling
- Increase temperature range

## 📈 Performance Optimization

### Speed vs Quality Trade-offs

**Faster Generation**:
- Lower max_new_tokens
- Simpler sampling (disable mirostat)
- Fewer penalty calculations

**Higher Quality**:
- Enable advanced sampling
- Use mirostat adaptive control
- Apply multiple penalty types

### Memory Considerations

**Context Management**:
- Balance truncation_length with performance
- Consider repetition_penalty_range impact
- Monitor memory usage with long contexts

## 🚀 Next Steps

After mastering Stage 2, you'll be ready for:
- **Stage 3**: Default/Notebook tabs and raw completions
- **Stage 4**: OpenAI API integration and automation
- **Stage 5**: LoRA training with optimized parameters

## 📝 Change Log

$(Get-Date -Format "yyyy-MM-dd"): Created Stage 2 advanced parameter system
- Added 6 task-specific Chinese presets
- Created analysis and testing tools
- Established quality assessment framework
- Documented parameter optimization methodology

Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"

$docPath = Join-Path $stageDir "README.md"
$documentation | Out-File -FilePath $docPath -Encoding UTF8
Write-Success "Created comprehensive documentation"

# =============================================================================
# Summary & Next Steps
# =============================================================================
Write-Host ""
Write-Host "🎉 Stage 2 Advanced Parameter Tuning Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

Write-Success "Installed 6 advanced Chinese presets:"
$presetNames = @("中文技術文檔", "中文對話聊天", "中文學術分析", "中文詩詞創作", "中文程式註解", "中文故事續寫")
foreach ($name in $presetNames) {
    Write-Host "  🎛️ $name" -ForegroundColor Gray
}

Write-Success "Created analysis and testing tools:"
Write-Host "  🔍 Compare-Presets.ps1 - Parameter comparison" -ForegroundColor Gray
Write-Host "  📊 Assess-Quality.ps1 - Quality evaluation" -ForegroundColor Gray
Write-Host "  📋 Chinese-Parameter-Guide.md - Optimization guide" -ForegroundColor Gray
Write-Host "  🧪 Batch-Test.ps1 - Systematic testing" -ForegroundColor Gray

Write-Host ""
Write-Info "Recommended Testing Workflow:"
Write-Host "1. Start TGW and load Chinese model" -ForegroundColor Cyan
Write-Host "2. Test technical questions with '中文技術文檔' preset" -ForegroundColor Cyan
Write-Host "3. Test creative writing with '中文詩詞創作' preset" -ForegroundColor Cyan
Write-Host "4. Use comparison tools to understand differences" -ForegroundColor Cyan
Write-Host "5. Run quality assessments and log results" -ForegroundColor Cyan

Write-Host ""
Write-Info "Key Learning Points:"
Write-Host "• Mirostat sampling for consistency in technical content" -ForegroundColor White
Write-Host "• Dynamic temperature for natural conversation variation" -ForegroundColor White
Write-Host "• Quadratic sampling for creative writing enhancement" -ForegroundColor White
Write-Host "• Chinese-specific token density considerations" -ForegroundColor White
Write-Host "• Systematic testing and quality assessment methods" -ForegroundColor White

Write-Host ""
Write-Warning "Important Notes:"
Write-Host "• Advanced samplers may slow generation speed" -ForegroundColor Yellow
Write-Host "• Some parameters require specific model support" -ForegroundColor Yellow
Write-Host "• Always test presets with your specific use cases" -ForegroundColor Yellow

Write-Host ""
Write-Info "Files created in:"
Write-Host "  📁 TGW presets: $(Join-Path $TGWPath 'presets')" -ForegroundColor Gray
Write-Host "  📁 Analysis tools: $(Join-Path $PlaybookPath 'stages\stage2-parameters\tools')" -ForegroundColor Gray
Write-Host "  📁 Documentation: $(Join-Path $PlaybookPath 'stages\stage2-parameters')" -ForegroundColor Gray

exit 0