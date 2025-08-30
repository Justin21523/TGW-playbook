#!/usr/bin/env python3
"""
TGW Stage 3 完整工具包
整合所有 Stage 3 功能的主要工具類別
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import yaml

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TGWToolkit:
    """TGW Stage 3 完整工具包"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化工具包"""
        self.base_dir = Path(__file__).parent.parent
        self.config = self._load_config(config_path)
        self.api_base = self.config.get('tgw_api', {}).get('base_url', 'http://localhost:5000')
        self.session = requests.Session()

        # 建立結果目錄
        self.results_dir = self.base_dir / 'results'
        self.results_dir.mkdir(exist_ok=True)

        logger.info(f"TGW Toolkit 初始化完成，API: {self.api_base}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """載入配置檔案"""
        if config_path is None:
            config_path = self.base_dir / 'configs' / 'advanced_config.yaml'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置檔案不存在: {config_path}，使用預設配置")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """取得預設配置"""
        return {
            'tgw_api': {'base_url': 'http://localhost:5000'},
            'token_analysis': {'efficiency': {'good_ratio': 2.5}},
            'batch_generation': {'concurrency': {'max_concurrent_requests': 3}},
            'quality_assessment': {'metrics': {'readability_weight': 0.25}}
        }

    def health_check(self) -> bool:
        """檢查 TGW API 健康狀態"""
        try:
            response = self.session.get(f"{self.api_base}/v1/models", timeout=10)
            if response.status_code == 200:
                logger.info("TGW API 健康狀態良好")
                return True
            else:
                logger.error(f"TGW API 回應異常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"TGW API 連接失敗: {e}")
            return False

    def analyze_prompt_efficiency(self, prompt: str) -> Dict[str, Any]:
        """分析提示詞效率"""
        try:
            # 取得 tokenization 結果
            response = self.session.post(
                f"{self.api_base}/v1/internal/tokenize",
                json={"text": prompt},
                timeout=30
            )

            if response.status_code != 200:
                return {"error": f"API 錯誤: {response.status_code}"}

            data = response.json()
            tokens = data.get("tokens", [])

            # 計算效率指標
            char_count = len(prompt)
            token_count = len(tokens)
            efficiency_ratio = char_count / max(token_count, 1)

            # 複雜度分析
            complexity = self._calculate_complexity(prompt)

            # 語言檢測
            language = self._detect_language(prompt)

            return {
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "char_count": char_count,
                "token_count": token_count,
                "tokens": tokens[:10],  # 只返回前10個tokens
                "efficiency_ratio": round(efficiency_ratio, 3),
                "complexity_score": complexity,
                "language": language,
                "quality_assessment": self._assess_prompt_quality(prompt, efficiency_ratio),
                "recommendations": self._generate_efficiency_recommendations(efficiency_ratio, complexity),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"提示詞分析失敗: {e}")
            return {"error": str(e)}

    def _calculate_complexity(self, text: str) -> float:
        """計算文本複雜度"""
        if not text:
            return 0.0

        # 基本複雜度指標
        unique_chars = len(set(text))
        total_chars = len(text)
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)

        # 標點符號密度
        import re
        punctuation_count = len(re.findall(r'[^\w\s]', text))
        punctuation_density = punctuation_count / max(total_chars, 1)

        # 複雜度分數（0-1）
        complexity = min(1.0,
            (unique_chars / max(total_chars, 1)) * 2 +
            (avg_word_length / 15) * 0.5 +
            punctuation_density * 2
        )

        return round(complexity, 3)

    def _detect_language(self, text: str) -> str:
        """簡單語言檢測"""
        import re

        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.sub(r'\s', '', text))

        if total_chars == 0:
            return "unknown"

        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars

        if chinese_ratio > 0.3:
            return "chinese"
        elif english_ratio > 0.5:
            return "english"
        else:
            return "mixed"

    def _assess_prompt_quality(self, prompt: str, efficiency_ratio: float) -> Dict[str, Any]:
        """評估提示詞品質"""
        quality_scores = {}

        # 效率評分
        if efficiency_ratio >= 3.0:
            quality_scores["efficiency"] = {"score": 0.9, "level": "excellent"}
        elif efficiency_ratio >= 2.5:
            quality_scores["efficiency"] = {"score": 0.7, "level": "good"}
        elif efficiency_ratio >= 2.0:
            quality_scores["efficiency"] = {"score": 0.5, "level": "acceptable"}
        else:
            quality_scores["efficiency"] = {"score": 0.3, "level": "poor"}

        # 清晰度評分（基於結構化程度）
        structure_indicators = ["：", ":", "1.", "2.", "3.", "•", "-", "要求", "格式", "包含"]
        structure_score = sum(1 for indicator in structure_indicators if indicator in prompt)
        clarity_score = min(1.0, structure_score / 5)

        quality_scores["clarity"] = {
            "score": clarity_score,
            "level": "excellent" if clarity_score >= 0.8 else "good" if clarity_score >= 0.6 else "acceptable"
        }

        # 具體性評分（基於具體要求）
        specificity_indicators = ["字數", "格式", "包含", "要求", "範例", "步驟"]
        specificity_score = sum(1 for indicator in specificity_indicators if indicator in prompt)
        specificity_normalized = min(1.0, specificity_score / 4)

        quality_scores["specificity"] = {
            "score": specificity_normalized,
            "level": "excellent" if specificity_normalized >= 0.8 else "good" if specificity_normalized >= 0.6 else "acceptable"
        }

        # 計算總體品質分數
        overall_score = (
            quality_scores["efficiency"]["score"] * 0.4 +
            quality_scores["clarity"]["score"] * 0.3 +
            quality_scores["specificity"]["score"] * 0.3
        )

        quality_scores["overall"] = {
            "score": round(overall_score, 3),
            "level": "excellent" if overall_score >= 0.8 else "good" if overall_score >= 0.6 else "needs_improvement"
        }

        return quality_scores

    def _generate_efficiency_recommendations(self, efficiency_ratio: float, complexity: float) -> List[str]:
        """生成效率改進建議"""
        recommendations = []

        if efficiency_ratio < 2.0:
            recommendations.append("考慮移除冗餘詞彙以提高 token 效率")
            recommendations.append("使用更精簡的表達方式")

        if complexity > 0.7:
            recommendations.append("簡化句式結構以提高可讀性")
            recommendations.append("減少複雜的標點符號使用")

        if efficiency_ratio < 2.5 and complexity < 0.3:
            recommendations.append("在保持簡潔的同時，可以增加更具體的要求")

        if not recommendations:
            recommendations.append("提示詞效率良好，建議保持現有風格")

        return recommendations

    def batch_generate_with_analysis(self,
                                   prompts: List[str],
                                   parameters: Dict[str, Any] = None,
                                   analyze_quality: bool = True) -> Dict[str, Any]:
        """批次生成並進行品質分析"""

        if parameters is None:
            parameters = self.config.get('batch_generation', {}).get('parameter_presets', {}).get('balanced', {})

        results = {
            "tasks": [],
            "summary": {},
            "quality_analysis": {},
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"開始批次生成 {len(prompts)} 個提示詞...")

        for i, prompt in enumerate(prompts):
            logger.info(f"處理提示詞 {i+1}/{len(prompts)}")

            # 生成內容
            generation_result = self._single_generate(prompt, parameters)

            # 分析品質（如果啟用）
            quality_metrics = {}
            if analyze_quality and generation_result.get("success", False):
                quality_metrics = self._analyze_generation_quality(
                    prompt,
                    generation_result.get("generated_text", "")
                )

            task_result = {
                "task_id": f"task_{i+1:03d}",
                "prompt": prompt,
                "generation_result": generation_result,
                "quality_metrics": quality_metrics,
                "timestamp": datetime.now().isoformat()
            }

            results["tasks"].append(task_result)

        # 生成摘要統計
        results["summary"] = self._generate_batch_summary(results["tasks"])

        # 生成品質分析報告
        if analyze_quality:
            results["quality_analysis"] = self._generate_quality_analysis(results["tasks"])

        # 儲存結果
        self._save_batch_results(results)

        logger.info("批次生成完成")
        return results

    def _single_generate(self, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """單一生成請求"""
        try:
            start_time = time.time()

            response = self.session.post(
                f"{self.api_base}/v1/completions",
                json={
                    "prompt": prompt,
                    **parameters
                },
                timeout=60
            )

            generation_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("choices", [{}])[0].get("text", "")

                return {
                    "success": True,
                    "generated_text": generated_text,
                    "generation_time": round(generation_time, 2),
                    "token_usage": data.get("usage", {}),
                    "parameters": parameters
                }
            else:
                return {
                    "success": False,
                    "error": f"API 錯誤: {response.status_code}",
                    "generation_time": round(generation_time, 2)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generation_time": 0
            }

    def _analyze_generation_quality(self, prompt: str, generated_text: str) -> Dict[str, Any]:
        """分析生成內容品質"""
        if not generated_text:
            return {"error": "沒有生成內容可分析"}

        # 基本統計
        char_count = len(generated_text)
        word_count = len(generated_text.split())

        # 計算品質指標
        readability = self._calculate_readability(generated_text)
        coherence = self._calculate_coherence(generated_text)
        completeness = self._calculate_completeness(generated_text, prompt)
        relevance = self._calculate_relevance(generated_text, prompt)

        # 整體品質分數
        weights = self.config.get('quality_assessment', {}).get('metrics', {})
        overall_quality = (
            readability * weights.get('readability_weight', 0.25) +
            coherence * weights.get('coherence_weight', 0.25) +
            completeness * weights.get('completeness_weight', 0.25) +
            relevance * weights.get('relevance_weight', 0.25)
        )

        return {
            "basic_stats": {
                "char_count": char_count,
                "word_count": word_count
            },
            "quality_scores": {
                "readability": round(readability, 3),
                "coherence": round(coherence, 3),
                "completeness": round(completeness, 3),
                "relevance": round(relevance, 3),
                "overall": round(overall_quality, 3)
            }
        }

    def _calculate_readability(self, text: str) -> float:
        """計算可讀性分數"""
        import re

        if not text.strip():
            return 0.0

        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # 平均句子長度
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # 可讀性分數（基於句子長度，理想長度為15字左右）
        readability = max(0, min(1, 1 - abs(avg_sentence_length - 15) / 30))

        return readability

    def _calculate_coherence(self, text: str) -> float:
        """計算連貫性分數"""
        if not text.strip():
            return 0.0

        # 檢查連接詞使用
        connectors = self.config.get('quality_assessment', {}).get('coherence', {}).get('connector_words', [])
        connector_count = sum(1 for connector in connectors if connector in text)

        # 基於文本長度的期望連接詞數量
        words = text.split()
        expected_connectors = len(words) / 50  # 每50個詞期望有1個連接詞

        coherence_score = min(1.0, connector_count / max(expected_connectors, 1))

        return coherence_score

    def _calculate_completeness(self, text: str, prompt: str) -> float:
        """計算完整性分數"""
        if not text.strip():
            return 0.0

        # 長度相對性檢查
        min_ratio = self.config.get('quality_assessment', {}).get('completeness', {}).get('min_length_ratio', 2.0)
        length_ratio = len(text) / max(len(prompt), 1)
        length_score = min(1.0, length_ratio / min_ratio)

        # 結尾完整性檢查
        conclusion_phrases = self.config.get('quality_assessment', {}).get('completeness', {}).get('required_conclusion_phrases', [])
        has_conclusion = any(phrase in text for phrase in conclusion_phrases)
        conclusion_score = 1.0 if has_conclusion else 0.7

        completeness = length_score * 0.7 + conclusion_score * 0.3

        return completeness

    def _calculate_relevance(self, text: str, prompt: str) -> float:
        """計算相關性分數"""
        if not text.strip() or not prompt.strip():
            return 0.0

        import re

        # 提取關鍵詞
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        text_words = set(re.findall(r'\b\w+\b', text.lower()))

        # 過濾常見詞
        common_words = {'的', '是', '在', '有', '和', '與', '或', '但', '這', '那', '一', '個', 'a', 'an', 'the', 'is', 'are', 'and', 'or', 'but'}
        prompt_words -= common_words
        text_words -= common_words

        # 計算重疊度
        if prompt_words:
            overlap_ratio = len(prompt_words & text_words) / len(prompt_words)
        else:
            overlap_ratio = 0.0

        return overlap_ratio

    def _generate_batch_summary(self, tasks: List[Dict]) -> Dict[str, Any]:
        """生成批次處理摘要"""
        total_tasks = len(tasks)
        successful_tasks = [t for t in tasks if t["generation_result"].get("success", False)]
        failed_tasks = [t for t in tasks if not t["generation_result"].get("success", False)]

        if successful_tasks:
            avg_generation_time = sum(t["generation_result"]["generation_time"] for t in successful_tasks) / len(successful_tasks)

            # 品質統計
            quality_scores = []
            for task in successful_tasks:
                if "quality_scores" in task.get("quality_metrics", {}):
                    quality_scores.append(task["quality_metrics"]["quality_scores"]["overall"])

            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        else:
            avg_generation_time = 0
            avg_quality = 0

        return {
            "total_tasks": total_tasks,
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / total_tasks * 100 if total_tasks > 0 else 0,
            "avg_generation_time": round(avg_generation_time, 2),
            "avg_quality_score": round(avg_quality, 3)
        }

    def _generate_quality_analysis(self, tasks: List[Dict]) -> Dict[str, Any]:
        """生成品質分析報告"""
        quality_data = []

        for task in tasks:
            if "quality_scores" in task.get("quality_metrics", {}):
                scores = task["quality_metrics"]["quality_scores"]
                quality_data.append(scores)

        if not quality_data:
            return {"message": "沒有可分析的品質資料"}

        # 計算各項指標的平均值和分佈
        metrics = ["readability", "coherence", "completeness", "relevance", "overall"]
        analysis = {}

        for metric in metrics:
            values = [data[metric] for data in quality_data if metric in data]
            if values:
                analysis[metric] = {
                    "mean": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                    "count": len(values)
                }

        # 品質等級分佈
        overall_scores = [data["overall"] for data in quality_data if "overall" in data]
        quality_distribution = {
            "excellent": len([s for s in overall_scores if s >= 0.8]),
            "good": len([s for s in overall_scores if 0.6 <= s < 0.8]),
            "acceptable": len([s for s in overall_scores if 0.4 <= s < 0.6]),
            "poor": len([s for s in overall_scores if s < 0.4])
        }

        analysis["distribution"] = quality_distribution

        return analysis

    def _save_batch_results(self, results: Dict[str, Any]):
        """儲存批次結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.results_dir / f"batch_results_{timestamp}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"批次結果已儲存: {filepath}")

    def visualize_quality_analysis(self, results: Dict[str, Any], save_plot: bool = True) -> None:
        """視覺化品質分析結果"""
        if "quality_analysis" not in results:
            logger.warning("沒有品質分析資料可視覺化")
            return

        quality_analysis = results["quality_analysis"]

        if "message" in quality_analysis:
            logger.warning(quality_analysis["message"])
            return

        # 設定繪圖風格
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('TGW 批次生成品質分析報告', fontsize=16, fontweight='bold')

        # 1. 品質指標比較
        metrics = ["readability", "coherence", "completeness", "relevance"]
        means = [quality_analysis[metric]["mean"] for metric in metrics if metric in quality_analysis]

        if means:
            axes[0, 0].bar(metrics, means, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
            axes[0, 0].set_title('各項品質指標平均分數')
            axes[0, 0].set_ylabel('分數')
            axes[0, 0].set_ylim(0, 1)
            axes[0, 0].tick_params(axis='x', rotation=45)

        # 2. 品質分佈
        if "distribution" in quality_analysis:
            dist = quality_analysis["distribution"]
            labels = list(dist.keys())
            values = list(dist.values())

            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            axes[0, 1].pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
            axes[0, 1].set_title('品質等級分佈')

        # 3. 成功率和平均時間
        summary = results.get("summary", {})
        if summary:
            success_rate = summary.get("success_rate", 0)
            avg_time = summary.get("avg_generation_time", 0)

            axes[1, 0].bar(['成功率 (%)', '平均時間 (秒)'], [success_rate, avg_time * 10],
                          color=['#2ecc71', '#3498db'])
            axes[1, 0].set_title('處理效率統計')
            axes[1, 0].set_ylabel('數值')

        # 4. 品質分數範圍
        if "overall" in quality_analysis:
            overall = quality_analysis["overall"]
            data_to_plot = [overall["min"], overall["mean"], overall["max"]]
            labels = ['最低', '平均', '最高']

            axes[1, 1].bar(labels, data_to_plot, color=['#e74c3c', '#f39c12', '#2ecc71'])
            axes[1, 1].set_title('整體品質分數範圍')
            axes[1, 1].set_ylabel('分數')
            axes[1, 1].set_ylim(0, 1)

        plt.tight_layout()

        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = self.results_dir / f"quality_analysis_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"品質分析圖表已儲存: {plot_path}")

        plt.show()

    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """生成綜合分析報告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = results.get("summary", {})
        quality_analysis = results.get("quality_analysis", {})

        report = f"""# TGW Stage 3 批次生成分析報告

**生成時間**: {timestamp}
**分析版本**: TGW Toolkit v1.0

## 📊 執行摘要

- **總任務數**: {summary.get('total_tasks', 0)}
- **成功任務**: {summary.get('successful_tasks', 0)}
- **失敗任務**: {summary.get('failed_#!/bin/bash
# Stage 3 完整部署和設置腳本
# 自動建立完整的 Stage 3 環境和所有必要檔案

set -e  # 遇到錯誤立即退出

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 函數：顯示帶顏色的訊息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() { print_message $GREEN "✅ $1"; }
print_warning() { print_message $YELLOW "⚠️  $1"; }
print_error() { print_message $RED "❌ $1"; }
print_info() { print_message $CYAN "ℹ️  $1"; }
print_header() { print_message $PURPLE "🎯 $1"; }

# 設定路徑變數
PLAYBOOK_ROOT="/mnt/c/AI_LLM_projects/tgw-playbook"
STAGE3_DIR="$PLAYBOOK_ROOT/stages/stage3-default-notebook"
TGW_REPO="/mnt/c/AI_LLM_projects/text-generation-webui"

print_header "TGW Stage 3 - Default/Notebook Tabs 完整部署"
echo "=========================================="

# 檢查必要的前置條件
print_info "檢查前置條件..."

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安裝或不在 PATH 中"
    exit 1
fi
print_success "Python3 環境正常"

# 檢查 curl 和 jq
if ! command -v curl &> /dev/null; then
    print_warning "curl 未安裝，將安裝..."
    sudo apt update && sudo apt install -y curl
fi

if ! command -v jq &> /dev/null; then
    print_warning "jq 未安裝，將安裝..."
    sudo apt update && sudo apt install -y jq
fi

# 檢查基礎目錄
if [ ! -d "$PLAYBOOK_ROOT" ]; then
    print_error "Playbook 根目錄不存在: $PLAYBOOK_ROOT"
    print_info "請先執行 Stage 0 設置"
    exit 1
fi
print_success "Playbook 根目錄存在"

# 建立 Stage 3 目錄結構
print_info "建立 Stage 3 目錄結構..."
