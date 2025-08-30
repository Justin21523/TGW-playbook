#!/usr/bin/env python3
"""
高級批次處理系統
支援並行處理、品質控制和結果分析
"""

import asyncio
import aiohttp
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BatchTask:
    """批次任務定義"""
    id: str
    prompt: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = None
    priority: int = 1

@dataclass
class BatchResult:
    """批次處理結果"""
    task_id: str
    success: bool
    generated_text: str
    generation_time: float
    quality_score: float
    error_message: str = ""
    metadata: Dict[str, Any] = None

class QualityController:
    """品質控制器"""

    def __init__(self, min_quality: float = 0.6):
        self.min_quality = min_quality

    def evaluate_quality(self, text: str, prompt: str) -> float:
        """評估生成內容品質"""
        if not text or not text.strip():
            return 0.0

        # 基本品質指標
        length_score = min(1.0, len(text) / max(len(prompt) * 2, 100))

        # 完整性檢查
        has_ending = text.strip().endswith(('.', '!', '?', '。', '！', '？'))
        completeness_score = 1.0 if has_ending else 0.7

        # 相關性簡單檢查（關鍵詞重疊）
        prompt_words = set(prompt.lower().split())
        text_words = set(text.lower().split())
        common_words = {'的', '是', '在', '有', 'the', 'is', 'are', 'and'}

        prompt_words -= common_words
        relevance_score = len(prompt_words & text_words) / max(len(prompt_words), 1)

        # 綜合品質分數
        overall_quality = (
            length_score * 0.3 +
            completeness_score * 0.3 +
            relevance_score * 0.4
        )

        return min(1.0, overall_quality)

    def should_retry(self, quality_score: float) -> bool:
        """判斷是否需要重試"""
        return quality_score < self.min_quality

class AdvancedBatchProcessor:
    """高級批次處理器"""

    def __init__(self,
                 api_base: str = "http://localhost:5000",
                 max_concurrent: int = 3,
                 max_retries: int = 2):
        self.api_base = api_base
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.quality_controller = QualityController()
        self.results = []

    def create_tasks(self,
                    prompts: List[str],
                    parameters: Dict[str, Any] = None,
                    metadata_list: List[Dict[str, Any]] = None) -> List[BatchTask]:
        """建立批次任務清單"""

        if parameters is None:
            parameters = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 512
            }

        tasks = []
        for i, prompt in enumerate(prompts):
            task_id = f"task_{i+1:03d}_{int(time.time())}"
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}

            task = BatchTask(
                id=task_id,
                prompt=prompt,
                parameters=parameters.copy(),
                metadata=metadata
            )
            tasks.append(task)

        return tasks

    def process_batch(self, tasks: List[BatchTask]) -> Dict[str, Any]:
        """處理批次任務"""

        logger.info(f"開始處理 {len(tasks)} 個批次任務...")

        # 按優先級排序
        tasks.sort(key=lambda t: t.priority, reverse=True)

        successful_results = []
        failed_results = []
        retry_queue = []

        # 第一輪處理
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 提交所有任務
            future_to_task = {
                executor.submit(self._process_single_task, task): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]

                try:
                    result = future.result()

                    if result.success:
                        # 檢查品質
                        quality_score = self.quality_controller.evaluate_quality(
                            result.generated_text, task.prompt
                        )
                        result.quality_score = quality_score

                        if self.quality_controller.should_retry(quality_score):
                            logger.info(f"任務 {task.id} 品質不佳 ({quality_score:.3f})，加入重試佇列")
                            retry_queue.append(task)
                        else:
                            successful_results.append(result)
                            logger.info(f"任務 {task.id} 處理成功，品質: {quality_score:.3f}")
                    else:
                        failed_results.append(result)
                        logger.warning(f"任務 {task.id} 處理失敗: {result.error_message}")

                except Exception as e:
                    logger.error(f"任務 {task.id} 執行異常: {e}")
                    failed_results.append(BatchResult(
                        task_id=task.id,
                        success=False,
                        generated_text="",
                        generation_time=0.0,
                        quality_score=0.0,
                        error_message=str(e)
                    ))

        # 處理重試佇列
        if retry_queue and self.max_retries > 0:
            logger.info(f"重試 {len(retry_queue)} 個品質不佳的任務...")
            retry_results = self._handle_retries(retry_queue)
            successful_results.extend(retry_results)

        # 生成統計摘要
        summary = self._generate_summary(successful_results, failed_results)

        return {
            "successful_results": successful_results,
            "failed_results": failed_results,
            "summary": summary,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _process_single_task(self, task: BatchTask) -> BatchResult:
        """處理單個任務"""

        start_time = time.time()

        try:
            import requests

            response = requests.post(
                f"{self.api_base}/v1/completions",
                json={
                    "prompt": task.prompt,
                    **task.parameters
                },
                timeout=60
            )

            generation_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("choices", [{}])[0].get("text", "")

                return BatchResult(
                    task_id=task.id,
                    success=True,
                    generated_text=generated_text,
                    generation_time=generation_time,
                    quality_score=0.0,  # 將在後續計算
                    metadata=task.metadata
                )
            else:
                return BatchResult(
                    task_id=task.id,
                    success=False,
                    generated_text="",
                    generation_time=generation_time,
                    quality_score=0.0,
                    error_message=f"API 錯誤: {response.status_code}",
                    metadata=task.metadata
                )

        except Exception as e:
            generation_time = time.time() - start_time
            return BatchResult(
                task_id=task.id,
                success=False,
                generated_text="",
                generation_time=generation_time,
                quality_score=0.0,
                error_message=str(e),
                metadata=task.metadata
            )

    def _handle_retries(self, retry_tasks: List[BatchTask]) -> List[BatchResult]:
        """處理重試任務"""

        retry_results = []

        # 調整參數進行重試
        for task in retry_tasks:
            # 降低 temperature 以提高一致性
            task.parameters["temperature"] = max(0.3, task.parameters.get("temperature", 0.7) - 0.2)

            result = self._process_single_task(task)

            if result.success:
                quality_score = self.quality_controller.evaluate_quality(
                    result.generated_text, task.prompt
                )
                result.quality_score = quality_score

                if quality_score >= self.quality_controller.min_quality:
                    retry_results.append(result)
                    logger.info(f"重試任務 {task.id} 成功，品質: {quality_score:.3f}")
                else:
                    logger.warning(f"重試任務 {task.id} 仍品質不佳: {quality_score:.3f}")

        return retry_results

    def _generate_summary(self,
                         successful: List[BatchResult],
                         failed: List[BatchResult]) -> Dict[str, Any]:
        """生成處理摘要"""

        total_tasks = len(successful) + len(failed)

        if successful:
            avg_time = statistics.mean([r.generation_time for r in successful])
            avg_quality = statistics.mean([r.quality_score for r in successful])

            quality_distribution = {
                "excellent": len([r for r in successful if r.quality_score >= 0.8]),
                "good": len([r for r in successful if 0.6 <= r.quality_score < 0.8]),
                "acceptable": len([r for r in successful if 0.4 <= r.quality_score < 0.6]),
                "poor": len([r for r in successful if r.quality_score < 0.4])
            }
        else:
            avg_time = 0
            avg_quality = 0
            quality_distribution = {}

        return {
            "total_tasks": total_tasks,
            "successful_count": len(successful),
            "failed_count": len(failed),
            "success_rate": len(successful) / total_tasks * 100 if total_tasks > 0 else 0,
            "average_generation_time": round(avg_time, 2),
            "average_quality_score": round(avg_quality, 3),
            "quality_distribution": quality_distribution
        }


def save_results(self, results: Dict[str, Any], output_path: str):
        """儲存處理結果"""

        # 轉換 dataclass 為 dict
        serializable_results = {
            "successful_results": [asdict(r) for r in results["successful_results"]],
            "failed_results": [asdict(r) for r in results["failed_results"]],
            "summary": results["summary"],
            "timestamp": results["timestamp"]
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

        logger.info(f"結果已儲存到: {output_file}")

# 使用範例和測試
if __name__ == "__main__":
    processor = AdvancedBatchProcessor(max_concurrent=2)

    # 建立測試任務
    test_prompts = [
        "解釋什麼是機器學習",
        "寫一個 Python 函數計算階乘",
        "描述永續發展的重要性"
    ]

    tasks = processor.create_tasks(
        prompts=test_prompts,
        parameters={"temperature": 0.7, "max_new_tokens": 300}
    )

    # 處理批次
    results = processor.process_batch(tasks)

    # 顯示結果摘要
    summary = results["summary"]
    print(f"批次處理完成:")
    print(f"  成功: {summary['successful_count']}")
    print(f"  失敗: {summary['failed_count']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")
    print(f"  平均品質: {summary['average_quality_score']:.3f}")
