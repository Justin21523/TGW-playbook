# stages/stage3-default-notebook/token_analyzer.py
"""
TGW Token Analyzer & Optimizer
Token 分析與最佳化專用工具

功能：
- Token 使用效率分析
- 成本計算與最佳化建議
- 多語言 tokenization 比較
- Batch processing 最佳化
"""

import json
import re
import time
import requests
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import numpy as np


@dataclass
class TokenAnalysis:
    """Token 分析結果"""

    text: str
    token_count: int
    tokens: List[str]
    token_ids: List[int]
    char_count: int
    efficiency_ratio: float  # chars per token
    estimated_cost: float
    language: str
    complexity_score: float


class TGWTokenAnalyzer:
    """TGW Token 分析器"""

    def __init__(
        self,
        api_base: str = "http://localhost:5000",
        results_dir: str = "./results/token_analysis",
    ):
        self.api_base = api_base
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Token 成本設定（根據不同 API 提供商調整）
        self.cost_per_token = {
            "input": 0.0001,  # 每個輸入 token 的成本
            "output": 0.0002,  # 每個輸出 token 的成本
        }

    def analyze_text(self, text: str, language: str = "auto") -> TokenAnalysis:
        """分析單個文本的 token 資訊"""

        # 檢測語言
        if language == "auto":
            language = self._detect_language(text)

        # 獲取 tokenization 結果
        token_data = self._get_tokenization(text)

        if not token_data:
            # 如果 API 不可用，使用簡單估算
            token_count = self._estimate_tokens(text)
            tokens = text.split()
            token_ids = list(range(len(tokens)))
        else:
            token_count = len(token_data.get("tokens", []))
            tokens = token_data.get("tokens", [])
            token_ids = token_data.get("token_ids", [])

        # 計算效率指標
        char_count = len(text)
        efficiency_ratio = char_count / max(token_count, 1)
        estimated_cost = token_count * self.cost_per_token["input"]
        complexity_score = self._calculate_complexity(text)

        return TokenAnalysis(
            text=text,
            token_count=token_count,
            tokens=tokens,
            token_ids=token_ids,
            char_count=char_count,
            efficiency_ratio=efficiency_ratio,
            estimated_cost=estimated_cost,
            language=language,
            complexity_score=complexity_score,
        )

    def _get_tokenization(self, text: str) -> Optional[Dict]:
        """從 TGW API 獲取 tokenization 結果"""
        try:
            response = requests.post(
                f"{self.api_base}/v1/internal/tokenize",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Tokenization API 回應錯誤: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️ 無法連接 tokenization API: {e}")
            return None

    def _estimate_tokens(self, text: str) -> int:
        """簡單的 token 數量估算"""
        # 基於經驗的估算公式
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        english_words = len(re.findall(r"[a-zA-Z]+", text))
        numbers = len(re.findall(r"\d+", text))
        punctuation = len(re.findall(r"[^\w\s]", text))

        # 中文字符通常 1-2 個 token，英文詞彙平均 1.3 個 token
        estimated = (
            chinese_chars * 1.5
            + english_words * 1.3
            + numbers * 0.8
            + punctuation * 0.5
        )

        return max(int(estimated), 1)

    def _detect_language(self, text: str) -> str:
        """簡單的語言檢測"""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))

        total_chars = len(re.sub(r"\s", "", text))

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

    def _calculate_complexity(self, text: str) -> float:
        """計算文本複雜度分數"""
        # 基於多個指標的複雜度計算
        unique_chars = len(set(text))
        total_chars = len(text)
        avg_word_length = (
            np.mean([len(word) for word in text.split()]) if text.split() else 0
        )

        # 標點符號密度
        punctuation_density = len(re.findall(r"[^\w\s]", text)) / max(total_chars, 1)

        # 複雜度分數 (0-1 之間)
        complexity = min(
            1.0,
            (unique_chars / max(total_chars, 1)) * 2
            + (avg_word_length / 10)
            + punctuation_density,
        )

        return round(complexity, 3)

    def compare_prompts(
        self, prompts: List[str], names: List[str] = None
    ) -> pd.DataFrame:
        """比較多個提示詞的 token 效率"""

        if names is None:
            names = [f"Prompt_{i+1}" for i in range(len(prompts))]

        results = []

        for i, prompt in enumerate(prompts):
            analysis = self.analyze_text(prompt)

            results.append(
                {
                    "Name": names[i],
                    "Token_Count": analysis.token_count,
                    "Char_Count": analysis.char_count,
                    "Efficiency_Ratio": analysis.efficiency_ratio,
                    "Estimated_Cost": analysis.estimated_cost,
                    "Language": analysis.language,
                    "Complexity": analysis.complexity_score,
                }
            )

        df = pd.DataFrame(results)

        # 儲存比較結果
        timestamp = int(time.time())
        filepath = self.results_dir / f"prompt_comparison_{timestamp}.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

        print(f"📊 比較結果已儲存: {filepath}")

        return df

    def optimize_prompt_length(
        self, prompt: str, target_reduction: float = 0.2
    ) -> Dict:
        """最佳化提示詞長度"""

        original_analysis = self.analyze_text(prompt)
        target_tokens = int(original_analysis.token_count * (1 - target_reduction))

        print(
            f"🎯 目標：將 token 數從 {original_analysis.token_count} 減少到 {target_tokens}"
        )

        # 最佳化策略
        optimizations = []

        # 1. 移除冗餘詞彙
        opt1 = self._remove_redundant_words(prompt)
        if opt1 != prompt:
            opt1_analysis = self.analyze_text(opt1)
            optimizations.append(
                {
                    "strategy": "移除冗餘詞彙",
                    "text": opt1,
                    "analysis": opt1_analysis,
                    "reduction": original_analysis.token_count
                    - opt1_analysis.token_count,
                }
            )

        # 2. 簡化句式結構
        opt2 = self._simplify_structure(prompt)
        if opt2 != prompt:
            opt2_analysis = self.analyze_text(opt2)
            optimizations.append(
                {
                    "strategy": "簡化句式結構",
                    "text": opt2,
                    "analysis": opt2_analysis,
                    "reduction": original_analysis.token_count
                    - opt2_analysis.token_count,
                }
            )

        # 3. 使用更精簡的表達
        opt3 = self._use_concise_expressions(prompt)
        if opt3 != prompt:
            opt3_analysis = self.analyze_text(opt3)
            optimizations.append(
                {
                    "strategy": "使用精簡表達",
                    "text": opt3,
                    "analysis": opt3_analysis,
                    "reduction": original_analysis.token_count
                    - opt3_analysis.token_count,
                }
            )

        # 選擇最佳最佳化
        best_optimization = (
            max(optimizations, key=lambda x: x["reduction"]) if optimizations else None
        )

        return {
            "original": {"text": prompt, "analysis": original_analysis},
            "target_tokens": target_tokens,
            "optimizations": optimizations,
            "best_optimization": best_optimization,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _remove_redundant_words(self, text: str) -> str:
        """移除冗餘詞彙"""
        # 移除常見的冗餘表達
        redundant_patterns = [
            (r"\b(請您|請你|麻煩您|麻煩你|可以請您|可以請你)\b", "請"),
            (r"\b(能夠|能夠幫我|能夠協助|能夠幫忙)\b", "能"),
            (r"\b(非常的|特別的|相當的|十分的)\b", "很"),
            (r"\b(進行|實施|執行|開展)\b", "做"),
            (r"\b(提供給|給予|供應)\b", "給"),
            (r"\b(關於|有關於|針對)\b", "對於"),
            (r"\s+", " "),  # 多個空格合併為一個
        ]

        optimized = text
        for pattern, replacement in redundant_patterns:
            optimized = re.sub(pattern, replacement, optimized)

        return optimized.strip()

    def _simplify_structure(self, text: str) -> str:
        """簡化句式結構"""
        # 將複雜句式轉換為簡單句式
        simplifications = [
            # 移除過多的禮貌用語
            (r"不好意思，?", ""),
            (r"如果可以的話，?", ""),
            (r"在您方便的時候，?", ""),
            # 簡化條件句
            (r"如果您能夠?(.+?)的話", r"\1"),
            (r"假如(.+?)的情況下", r"若\1"),
            # 簡化時間表達
            (r"在(.+?)的時候", r"\1時"),
            (r"當(.+?)的時候", r"\1時"),
        ]

        simplified = text
        for pattern, replacement in simplifications:
            simplified = re.sub(pattern, replacement, simplified)

        return simplified.strip()

    def _use_concise_expressions(self, text: str) -> str:
        """使用更精簡的表達"""
        concise_replacements = [
            ("詳細的說明", "說明"),
            ("完整的報告", "報告"),
            ("具體的範例", "範例"),
            ("相關的資訊", "資訊"),
            ("重要的事項", "要點"),
            ("主要的內容", "內容"),
            ("基本的概念", "概念"),
            ("一般的情況", "通常"),
            ("特殊的狀況", "特例"),
            ("大致的方向", "方向"),
        ]

        concise = text
        for verbose, simple in concise_replacements:
            concise = concise.replace(verbose, simple)

        return concise

    def batch_analyze(self, texts: List[str], names: List[str] = None) -> Dict:
        """批次分析多個文本"""

        if names is None:
            names = [f"Text_{i+1}" for i in range(len(texts))]

        print(f"🔄 開始批次分析 {len(texts)} 個文本...")

        results = {
            "analyses": [],
            "summary": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        total_tokens = 0
        total_chars = 0
        languages = {}

        for i, text in enumerate(texts):
            print(f"  分析中... {i+1}/{len(texts)}")

            analysis = self.analyze_text(text)

            results["analyses"].append(
                {"name": names[i], "analysis": analysis.__dict__}
            )

            total_tokens += analysis.token_count
            total_chars += analysis.char_count

            # 統計語言分佈
            lang = analysis.language
            languages[lang] = languages.get(lang, 0) + 1

        # 生成摘要統計
        results["summary"] = {
            "total_texts": len(texts),
            "total_tokens": total_tokens,
            "total_chars": total_chars,
            "avg_tokens_per_text": total_tokens / len(texts),
            "avg_chars_per_text": total_chars / len(texts),
            "avg_efficiency_ratio": total_chars / total_tokens,
            "language_distribution": languages,
            "estimated_total_cost": total_tokens * self.cost_per_token["input"],
        }

        # 儲存結果
        self._save_batch_results(results)

        print("✅ 批次分析完成")
        return results

    def _save_batch_results(self, results: Dict):
        """儲存批次分析結果"""
        timestamp = int(time.time())
        filepath = self.results_dir / f"batch_analysis_{timestamp}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"📁 批次結果已儲存: {filepath}")

    def visualize_comparison(
        self, comparison_df: pd.DataFrame, save_plot: bool = True
    ) -> None:
        """視覺化比較結果"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Token Analysis Comparison", fontsize=16)

        # 1. Token 數量比較
        axes[0, 0].bar(comparison_df["Name"], comparison_df["Token_Count"])
        axes[0, 0].set_title("Token Count Comparison")
        axes[0, 0].set_ylabel("Token Count")
        axes[0, 0].tick_params(axis="x", rotation=45)

        # 2. 效率比較
        axes[0, 1].bar(comparison_df["Name"], comparison_df["Efficiency_Ratio"])
        axes[0, 1].set_title("Efficiency Ratio (Chars/Token)")
        axes[0, 1].set_ylabel("Efficiency Ratio")
        axes[0, 1].tick_params(axis="x", rotation=45)

        # 3. 成本比較
        axes[1, 0].bar(comparison_df["Name"], comparison_df["Estimated_Cost"])
        axes[1, 0].set_title("Estimated Cost Comparison")
        axes[1, 0].set_ylabel("Cost ($)")
        axes[1, 0].tick_params(axis="x", rotation=45)

        # 4. 複雜度比較
        axes[1, 1].bar(comparison_df["Name"], comparison_df["Complexity"])
        axes[1, 1].set_title("Complexity Score")
        axes[1, 1].set_ylabel("Complexity (0-1)")
        axes[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        if save_plot:
            timestamp = int(time.time())
            plot_path = self.results_dir / f"comparison_plot_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            print(f"📈 圖表已儲存: {plot_path}")

        plt.show()

    def generate_optimization_report(
        self, optimization_result: Dict, save_report: bool = True
    ) -> str:
        """生成最佳化報告"""

        original = optimization_result["original"]
        best_opt = optimization_result["best_optimization"]

        report = f"""
# Token 最佳化報告

## 原始提示詞分析
- **Token 數量**: {original['analysis'].token_count}
- **字符數量**: {original['analysis'].char_count}
- **效率比率**: {original['analysis'].efficiency_ratio:.2f}
- **預估成本**: ${original['analysis'].estimated_cost:.4f}
- **語言**: {original['analysis'].language}
- **複雜度**: {original['analysis'].complexity_score}

## 最佳化目標
- **目標 Token 數**: {optimization_result['target_tokens']}
- **目標減少量**: {original['analysis'].token_count - optimization_result['target_tokens']} tokens

## 最佳化策略結果
"""

        if best_opt:
            reduction_percentage = (
                best_opt["reduction"] / original["analysis"].token_count
            ) * 100
            cost_saving = (
                original["analysis"].estimated_cost
                - best_opt["analysis"].estimated_cost
            )

            report += f"""
### 推薦策略: {best_opt['strategy']}

**最佳化前:**
```
{original['text']}
```

**最佳化後:**
```
{best_opt['text']}
```

**改善效果:**
- Token 減少: {best_opt['reduction']} ({reduction_percentage:.1f}%)
- 成本節省: ${cost_saving:.4f} ({(cost_saving/original['analysis'].estimated_cost)*100:.1f}%)
- 新效率比率: {best_opt['analysis'].efficiency_ratio:.2f}
"""

        # 所有策略比較
        report += "\n## 所有策略比較\n\n"
        for opt in optimization_result["optimizations"]:
            reduction_pct = (opt["reduction"] / original["analysis"].token_count) * 100
            report += f"- **{opt['strategy']}**: 減少 {opt['reduction']} tokens ({reduction_pct:.1f}%)\n"

        if save_report:
            timestamp = int(time.time())
            report_path = self.results_dir / f"optimization_report_{timestamp}.md"

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"📄 最佳化報告已儲存: {report_path}")

        return report


def main():
    """主要執行函數"""
    print("🔍 TGW Token Analyzer & Optimizer")
    print("=" * 50)

    # 初始化分析器
    analyzer = TGWTokenAnalyzer()

    # 範例分析
    print("📊 執行範例分析...")

    sample_prompts = [
        "請您協助我撰寫一份關於人工智慧技術發展的詳細報告，內容需要包含當前的技術趨勢、主要應用領域以及未來的發展方向。",
        "寫一份 AI 技術報告，包含技術趨勢、應用領域、發展方向。",
        "Generate an AI technology report covering trends, applications, and future directions.",
    ]

    sample_names = ["冗長版本", "精簡版本", "英文版本"]

    # 比較分析
    comparison_df = analyzer.compare_prompts(sample_prompts, sample_names)
    print("\n📋 提示詞比較結果:")
    print(comparison_df.to_string(index=False))

    # 最佳化示範
    print("\n🔧 執行最佳化示範...")
    optimization_result = analyzer.optimize_prompt_length(
        sample_prompts[0], target_reduction=0.3
    )

    # 生成報告
    report = analyzer.generate_optimization_report(optimization_result)
    print("\n📄 最佳化報告:")
    print(report[:500] + "..." if len(report) > 500 else report)

    print(f"\n✅ 分析完成！結果儲存在: {analyzer.results_dir}")


if __name__ == "__main__":
    main()
