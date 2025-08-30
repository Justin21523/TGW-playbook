# stages/stage3-default-notebook/batch_processor.py
"""
TGW Batch Generation & Quality Control Tool
批次生成與品質控制專用工具

功能：
- 批次文本生成
- 品質評估和篩選
- 一致性檢查
- 輸出格式標準化
- 生成結果比較和排序
"""

import json
import time
import asyncio
import aiohttp
import requests
import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from datetime import datetime
import statistics


@dataclass
class GenerationTask:
    """生成任務"""

    id: str
    prompt: str
    parameters: Dict[str, Any]
    template_name: str = ""
    priority: int = 1
    metadata: Dict[str, Any] = None


@dataclass
class GenerationResult:
    """生成結果"""

    task_id: str
    prompt: str
    generated_text: str
    parameters: Dict[str, Any]
    generation_time: float
    token_count: int
    quality_score: float
    metadata: Dict[str, Any]
    timestamp: str
    success: bool
    error_message: str = ""


class QualityMetrics:
    """品質評估指標"""

    @staticmethod
    def calculate_readability(text: str) -> float:
        """計算可讀性分數 (0-1)"""
        if not text.strip():
            return 0.0

        sentences = re.split(r"[.!?。！？]", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # 平均句子長度
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # 標點符號密度
        punctuation_count = len(re.findall(r"[.!?。！？,，;；:]", text))
        punctuation_density = punctuation_count / max(len(text.split()), 1)

        # 可讀性分數 (基於句子長度和標點使用)
        readability = (
            max(0, min(1, 1 - (avg_sentence_length - 15) / 30)) * 0.7
            + min(punctuation_density * 10, 1) * 0.3
        )

        return round(readability, 3)

    @staticmethod
    def calculate_coherence(text: str) -> float:
        """計算連貫性分數 (0-1)"""
        if not text.strip():
            return 0.0

        sentences = re.split(r"[.!?。！？]", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5  # 單句默認中等連貫性

        # 檢查連接詞使用
        connectors = [
            "因此",
            "所以",
            "但是",
            "然而",
            "此外",
            "另外",
            "首先",
            "其次",
            "最後",
            "總之",
        ]
        connector_usage = sum(1 for connector in connectors if connector in text)
        connector_score = min(connector_usage / max(len(sentences) * 0.3, 1), 1)

        # 檢查重複概念 (簡單詞彙重複分析)
        words = text.split()
        unique_words = set(words)
        repetition_ratio = len(unique_words) / max(len(words), 1)

        # 連貫性分數
        coherence = connector_score * 0.6 + repetition_ratio * 0.4

        return round(coherence, 3)

    @staticmethod
    def calculate_completeness(text: str, prompt: str) -> float:
        """計算完整性分數 (0-1)"""
        if not text.strip():
            return 0.0

        # 基於長度的完整性 (相對於提示詞)
        length_ratio = len(text) / max(
            len(prompt) * 2, 100
        )  # 期望輸出是提示詞的2倍以上
        length_score = min(length_ratio, 1)

        # 檢查是否有明確結尾
        has_conclusion = any(
            ending in text for ending in ["總結", "結論", "綜上", "最後", "。", "！"]
        )
        conclusion_score = 1.0 if has_conclusion else 0.5

        # 完整性分數
        completeness = length_score * 0.7 + conclusion_score * 0.3

        return round(completeness, 3)

    @staticmethod
    def calculate_relevance(text: str, prompt: str) -> float:
        """計算相關性分數 (0-1)"""
        if not text.strip() or not prompt.strip():
            return 0.0

        # 提取提示詞中的關鍵詞
        prompt_words = set(re.findall(r"\b\w+\b", prompt.lower()))
        text_words = set(re.findall(r"\b\w+\b", text.lower()))

        # 計算詞彙重疊度
        if prompt_words:
            overlap_ratio = len(prompt_words & text_words) / len(prompt_words)
        else:
            overlap_ratio = 0.0

        return round(overlap_ratio, 3)


class TGWBatchGenerator:
    """TGW 批次生成器"""

    def __init__(
        self,
        api_base: str = "http://localhost:5000",
        results_dir: str = "./results/batch_generation",
        max_concurrent: int = 3,
    ):
        self.api_base = api_base
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.quality_metrics = QualityMetrics()

    def create_task(
        self,
        prompt: str,
        parameters: Dict[str, Any] = None,
        template_name: str = "",
        priority: int = 1,
        metadata: Dict[str, Any] = None,
    ) -> GenerationTask:
        """建立生成任務"""

        if parameters is None:
            parameters = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 512,
                "repetition_penalty": 1.1,
            }

        if metadata is None:
            metadata = {}

        # 生成任務 ID
        task_id = hashlib.md5(f"{prompt}_{time.time()}".encode()).hexdigest()[:8]

        return GenerationTask(
            id=task_id,
            prompt=prompt,
            parameters=parameters,
            template_name=template_name,
            priority=priority,
            metadata=metadata,
        )

    def generate_single(self, task: GenerationTask) -> GenerationResult:
        """執行單個生成任務"""

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.api_base}/v1/completions",
                json={"prompt": task.prompt, **task.parameters},
                headers={"Content-Type": "application/json"},
                timeout=60,  # 60秒超時
            )

            generation_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("choices", [{}])[0].get("text", "")

                # 計算品質分數
                quality_score = self._calculate_overall_quality(
                    generated_text, task.prompt
                )

                # 估算 token 數量
                token_count = len(generated_text.split())  # 簡化估算

                return GenerationResult(
                    task_id=task.id,
                    prompt=task.prompt,
                    generated_text=generated_text,
                    parameters=task.parameters,
                    generation_time=generation_time,
                    token_count=token_count,
                    quality_score=quality_score,
                    metadata=task.metadata,
                    timestamp=datetime.now().isoformat(),
                    success=True,
                )
            else:
                return GenerationResult(
                    task_id=task.id,
                    prompt=task.prompt,
                    generated_text="",
                    parameters=task.parameters,
                    generation_time=generation_time,
                    token_count=0,
                    quality_score=0.0,
                    metadata=task.metadata,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=f"API 錯誤: {response.status_code}",
                )

        except Exception as e:
            generation_time = time.time() - start_time
            return GenerationResult(
                task_id=task.id,
                prompt=task.prompt,
                generated_text="",
                parameters=task.parameters,
                generation_time=generation_time,
                token_count=0,
                quality_score=0.0,
                metadata=task.metadata,
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message=str(e),
            )

    def batch_generate(
        self,
        tasks: List[GenerationTask],
        quality_threshold: float = 0.6,
        max_retries: int = 2,
    ) -> Dict[str, List[GenerationResult]]:
        """批次生成執行"""

        print(f"🚀 開始批次生成 {len(tasks)} 個任務...")

        # 按優先級排序
        tasks.sort(key=lambda t: t.priority, reverse=True)

        all_results = []
        successful_results = []
        failed_results = []
        low_quality_results = []

        # 使用線程池並行執行
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 提交所有任務
            future_to_task = {
                executor.submit(self.generate_single, task): task for task in tasks
            }

            for i, future in enumerate(as_completed(future_to_task)):
                task = future_to_task[future]

                try:
                    result = future.result()
                    all_results.append(result)

                    print(f"  完成 {i+1}/{len(tasks)} - 任務 {task.id}")

                    if result.success:
                        if result.quality_score >= quality_threshold:
                            successful_results.append(result)
                            print(f"    ✅ 成功 (品質: {result.quality_score:.3f})")
                        else:
                            low_quality_results.append(result)
                            print(f"    ⚠️ 品質不佳 (品質: {result.quality_score:.3f})")
                    else:
                        failed_results.append(result)
                        print(f"    ❌ 失敗: {result.error_message}")

                except Exception as e:
                    print(f"    💥 執行異常: {e}")

        # 品質不佳的結果重試
        if low_quality_results and max_retries > 0:
            print(f"🔄 重試 {len(low_quality_results)} 個品質不佳的任務...")

            retry_tasks = []
            for result in low_quality_results:
                # 調整參數進行重試
                retry_params = result.parameters.copy()
                retry_params["temperature"] = max(
                    0.3, retry_params.get("temperature", 0.7) - 0.2
                )

                retry_task = GenerationTask(
                    id=f"{result.task_id}_retry",
                    prompt=result.prompt,
                    parameters=retry_params,
                    metadata=result.metadata,
                )
                retry_tasks.append(retry_task)

            retry_results = self.batch_generate(
                retry_tasks, quality_threshold, max_retries - 1
            )
            successful_results.extend(retry_results["successful"])

        # 整理結果
        results = {
            "successful": successful_results,
            "failed": failed_results,
            "low_quality": low_quality_results,
            "all": all_results,
            "summary": {
                "total_tasks": len(tasks),
                "successful_count": len(successful_results),
                "failed_count": len(failed_results),
                "low_quality_count": len(low_quality_results),
                "success_rate": len(successful_results) / len(tasks) * 100,
                "avg_quality_score": (
                    statistics.mean([r.quality_score for r in successful_results])
                    if successful_results
                    else 0
                ),
                "total_generation_time": sum(r.generation_time for r in all_results),
                "avg_generation_time": (
                    statistics.mean([r.generation_time for r in all_results])
                    if all_results
                    else 0
                ),
            },
        }

        # 儲存結果
        self._save_batch_results(results)

        print(f"✅ 批次生成完成！")
        print(
            f"   成功: {len(successful_results)}/{len(tasks)} ({results['summary']['success_rate']:.1f}%)"
        )
        print(f"   平均品質分數: {results['summary']['avg_quality_score']:.3f}")

        return results

    def _calculate_overall_quality(self, text: str, prompt: str) -> float:
        """計算整體品質分數"""

        readability = self.quality_metrics.calculate_readability(text)
        coherence = self.quality_metrics.calculate_coherence(text)
        completeness = self.quality_metrics.calculate_completeness(text, prompt)
        relevance = self.quality_metrics.calculate_relevance(text, prompt)

        # 加權平均
        overall_quality = (
            readability * 0.25
            + coherence * 0.25
            + completeness * 0.25
            + relevance * 0.25
        )

        return round(overall_quality, 3)

    def _save_batch_results(self, results: Dict):
        """儲存批次結果"""
        timestamp = int(time.time())
        filepath = self.results_dir / f"batch_results_{timestamp}.json"

        # 將 dataclass 轉換為 dict
        serializable_results = {
            "successful": [asdict(r) for r in results["successful"]],
            "failed": [asdict(r) for r in results["failed"]],
            "low_quality": [asdict(r) for r in results["low_quality"]],
            "all": [asdict(r) for r in results["all"]],
            "summary": results["summary"],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

        print(f"💾 批次結果已儲存: {filepath}")

    def create_content_variations(
        self,
        base_prompt: str,
        variation_params: List[Dict[str, Any]],
        variation_names: List[str] = None,
    ) -> List[GenerationTask]:
        """建立內容變化任務"""

        if variation_names is None:
            variation_names = [f"變化_{i+1}" for i in range(len(variation_params))]

        tasks = []

        for i, params in enumerate(variation_params):
            task = self.create_task(
                prompt=base_prompt,
                parameters=params,
                template_name=variation_names[i],
                metadata={"variation_type": variation_names[i]},
            )
            tasks.append(task)

        return tasks

    def filter_results_by_quality(
        self, results: List[GenerationResult], min_quality: float = 0.7
    ) -> List[GenerationResult]:
        """按品質篩選結果"""

        filtered = [r for r in results if r.quality_score >= min_quality]

        print(
            f"🔍 品質篩選: {len(filtered)}/{len(results)} 符合標準 (>= {min_quality})"
        )

        return filtered

    def rank_results_by_quality(
        self, results: List[GenerationResult]
    ) -> List[GenerationResult]:
        """按品質排序結果"""

        ranked = sorted(results, key=lambda r: r.quality_score, reverse=True)

        print("🏆 品質排名:")
        for i, result in enumerate(ranked[:5]):  # 只顯示前 5 名
            print(f"  {i+1}. 任務 {result.task_id}: {result.quality_score:.3f}")

        return ranked

    def generate_quality_report(self, results: List[GenerationResult]) -> str:
        """生成品質報告"""

        if not results:
            return "無結果可分析"

        # 品質統計
        quality_scores = [r.quality_score for r in results if r.success]

        if not quality_scores:
            return "無成功結果可分析"

        avg_quality = statistics.mean(quality_scores)
        median_quality = statistics.median(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)
        std_quality = statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0

        # 生成時間統計
        generation_times = [r.generation_time for r in results if r.success]
        avg_time = statistics.mean(generation_times) if generation_times else 0

        # Token 統計
        token_counts = [r.token_count for r in results if r.success]
        avg_tokens = statistics.mean(token_counts) if token_counts else 0

        report = f"""
# 批次生成品質報告

## 整體統計
- **總任務數**: {len(results)}
- **成功任務數**: {len([r for r in results if r.success])}
- **成功率**: {len([r for r in results if r.success])/len(results)*100:.1f}%

## 品質分析
- **平均品質分數**: {avg_quality:.3f}
- **中位數品質分數**: {median_quality:.3f}
- **最高品質分數**: {max_quality:.3f}
- **最低品質分數**: {min_quality:.3f}
- **品質標準差**: {std_quality:.3f}

## 性能指標
- **平均生成時間**: {avg_time:.2f} 秒
- **平均 Token 數**: {avg_tokens:.0f}

## 品質分佈
"""

        # 品質分佈統計
        quality_ranges = [
            (0.9, 1.0, "優秀"),
            (0.8, 0.9, "良好"),
            (0.7, 0.8, "尚可"),
            (0.6, 0.7, "需改善"),
            (0.0, 0.6, "品質不佳"),
        ]

        for min_q, max_q, label in quality_ranges:
            count = len([q for q in quality_scores if min_q <= q < max_q])
            percentage = count / len(quality_scores) * 100
            report += f"- **{label}** ({min_q:.1f}-{max_q:.1f}): {count} 個 ({percentage:.1f}%)\n"

        # 最佳結果展示
        best_results = sorted(results, key=lambda r: r.quality_score, reverse=True)[:3]

        report += "\n## 最佳結果範例\n"
        for i, result in enumerate(best_results):
            if result.success:
                report += f"""
### 第 {i+1} 名 (品質分數: {result.quality_score:.3f})
**提示詞**: {result.prompt[:100]}...
**生成內容**: {result.generated_text[:200]}...
**生成時間**: {result.generation_time:.2f} 秒
"""

        return report


def main():
    """主要執行函數"""
    print("⚡ TGW Batch Generation & Quality Control Tool")
    print("=" * 60)

    # 初始化批次生成器
    generator = TGWBatchGenerator(max_concurrent=2)  # 降低並行數避免過載

    print("🔧 建立範例生成任務...")

    # 建立多個測試任務
    test_prompts = [
        "請寫一篇關於機器學習基礎概念的技術文章，包含監督學習和無監督學習的差異。",
        "設計一個 Python 函數來計算費波納契數列，要求包含完整的註解和錯誤處理。",
        "分析當前人工智慧發展的三個主要趨勢，並說明對未來社會的影響。",
        "創作一個科幻短故事，背景設定在 2050 年的智慧城市。",
        "撰寫一份專案管理最佳實務指南，適用於中小型軟體開發團隊。",
    ]

    # 建立不同參數組合的任務
    parameter_variations = [
        {"temperature": 0.3, "top_p": 0.8, "max_new_tokens": 400},  # 保守參數
        {"temperature": 0.7, "top_p": 0.9, "max_new_tokens": 500},  # 平衡參數
        {"temperature": 0.9, "top_p": 0.95, "max_new_tokens": 600},  # 創意參數
    ]

    all_tasks = []

    for i, prompt in enumerate(test_prompts):
        # 為每個提示詞建立多個變化版本
        variations = generator.create_content_variations(
            base_prompt=prompt,
            variation_params=parameter_variations,
            variation_names=["保守風格", "平衡風格", "創意風格"],
        )

        # 添加元數據
        for j, task in enumerate(variations):
            task.metadata.update(
                {"prompt_category": f"category_{i+1}", "variation_index": j}
            )
            task.priority = 3 - j  # 保守風格優先級最高

        all_tasks.extend(variations)

    print(f"📋 已建立 {len(all_tasks)} 個生成任務")

    # 執行批次生成
    results = generator.batch_generate(
        tasks=all_tasks, quality_threshold=0.6, max_retries=1
    )

    # 分析結果
    print("\n📊 結果分析:")
    print(f"成功生成: {len(results['successful'])} 個")
    print(f"失敗: {len(results['failed'])} 個")
    print(f"品質不佳: {len(results['low_quality'])} 個")

    if results["successful"]:
        # 品質篩選和排序
        high_quality = generator.filter_results_by_quality(
            results["successful"], min_quality=0.7
        )

        ranked_results = generator.rank_results_by_quality(results["successful"])

        # 生成品質報告
        quality_report = generator.generate_quality_report(results["all"])

        # 儲存品質報告
        timestamp = int(time.time())
        report_path = generator.results_dir / f"quality_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(quality_report)

        print(f"\n📄 品質報告已儲存: {report_path}")

        # 顯示摘要
        print("\n📈 品質報告摘要:")
        print(
            quality_report[:500] + "..."
            if len(quality_report) > 500
            else quality_report
        )

    print(f"\n✅ 批次生成完成！所有結果儲存在: {generator.results_dir}")


if __name__ == "__main__":
    main()
