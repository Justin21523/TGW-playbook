# stages/stage3-default-notebook/prompt_engineering_tool.py
"""
TGW Prompt Engineering Tool
智能提示詞工程和範本管理工具

功能：
- 提示詞範本管理
- Token 效率分析
- A/B 測試自動化
- 品質評估指標
"""

import json
import os
import re
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptTemplate:
    """提示詞範本類別"""

    name: str
    category: str
    template: str
    variables: List[str]
    description: str
    tags: List[str]
    optimal_params: Dict[str, float]
    created_at: str


class TGWPromptEngineer:
    """TGW 提示詞工程師"""

    def __init__(
        self,
        api_base: str = "http://localhost:5000",
        templates_dir: str = "./configs/prompts",
        results_dir: str = "./results",
    ):
        self.api_base = api_base
        self.templates_dir = Path(templates_dir)
        self.results_dir = Path(results_dir)

        # 建立目錄
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # 載入範本
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, PromptTemplate]:
        """載入所有提示詞範本"""
        templates = {}

        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    template = PromptTemplate(**data)
                    templates[template.name] = template
            except Exception as e:
                print(f"⚠️ 無法載入範本 {template_file}: {e}")

        return templates

    def create_template(
        self,
        name: str,
        category: str,
        template: str,
        description: str,
        tags: List[str] = None,
        optimal_params: Dict[str, float] = None,
    ) -> PromptTemplate:
        """建立新的提示詞範本"""

        # 自動識別變數
        variables = re.findall(r"\{([^}]+)\}", template)

        # 預設參數
        if optimal_params is None:
            optimal_params = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "repetition_penalty": 1.1,
            }

        if tags is None:
            tags = []

        # 建立範本物件
        prompt_template = PromptTemplate(
            name=name,
            category=category,
            template=template,
            variables=variables,
            description=description,
            tags=tags,
            optimal_params=optimal_params,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        # 儲存範本
        self.save_template(prompt_template)
        self.templates[name] = prompt_template

        return prompt_template

    def save_template(self, template: PromptTemplate):
        """儲存範本到檔案"""
        filename = f"{template.category}_{template.name}.json"
        filepath = self.templates_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(template.__dict__, f, ensure_ascii=False, indent=2)

        print(f"✅ 範本已儲存: {filepath}")

    def fill_template(self, template_name: str, variables: Dict[str, str]) -> str:
        """填入變數生成最終提示詞"""
        if template_name not in self.templates:
            raise ValueError(f"範本 '{template_name}' 不存在")

        template = self.templates[template_name]
        prompt = template.template

        # 替換變數
        for var, value in variables.items():
            prompt = prompt.replace(f"{{{var}}}", value)

        return prompt

    def analyze_tokens(self, text: str) -> Dict:
        """分析文本的 token 資訊"""
        try:
            response = requests.post(
                f"{self.api_base}/v1/internal/tokenize",
                json={"text": text},
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "token_count": len(data.get("tokens", [])),
                    "tokens": data.get("tokens", []),
                    "token_ids": data.get("token_ids", []),
                    "efficiency_score": len(text)
                    / len(data.get("tokens", [1])),  # 字符/token 比率
                }
            else:
                print(f"⚠️ Token 分析失敗: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ Token 分析錯誤: {e}")
            return {}

    def generate_text(
        self, prompt: str, params: Dict[str, any] = None, stream: bool = False
    ) -> Dict:
        """生成文本"""

        default_params = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_new_tokens": 512,
            "repetition_penalty": 1.1,
            "stream": stream,
        }

        if params:
            default_params.update(params)

        try:
            response = requests.post(
                f"{self.api_base}/v1/completions",
                json={"prompt": prompt, **default_params},
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ 生成失敗: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ 生成錯誤: {e}")
            return {}

    def ab_test(
        self,
        prompts: List[str],
        test_name: str,
        params: Dict[str, any] = None,
        iterations: int = 3,
    ) -> Dict:
        """A/B 測試不同提示詞的效果"""

        results = {
            "test_name": test_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "prompts": [],
            "comparison": {},
        }

        print(f"🧪 開始 A/B 測試: {test_name}")

        for i, prompt in enumerate(prompts):
            prompt_results = {
                "id": f"prompt_{i+1}",
                "prompt": prompt,
                "token_analysis": self.analyze_tokens(prompt),
                "generations": [],
            }

            print(f"  測試提示詞 {i+1}/{len(prompts)}")

            # 多次生成測試
            for iteration in range(iterations):
                generation = self.generate_text(prompt, params)
                if generation:
                    prompt_results["generations"].append(
                        {
                            "iteration": iteration + 1,
                            "text": generation.get("choices", [{}])[0].get("text", ""),
                            "usage": generation.get("usage", {}),
                            "finish_reason": generation.get("choices", [{}])[0].get(
                                "finish_reason", ""
                            ),
                        }
                    )

            results["prompts"].append(prompt_results)

        # 生成比較報告
        results["comparison"] = self._analyze_ab_results(results["prompts"])

        # 儲存結果
        self._save_ab_results(results)

        return results

    def _analyze_ab_results(self, prompt_results: List[Dict]) -> Dict:
        """分析 A/B 測試結果"""
        comparison = {
            "token_efficiency": {},
            "generation_quality": {},
            "consistency": {},
            "recommendation": "",
        }

        for result in prompt_results:
            prompt_id = result["id"]

            # Token 效率分析
            token_info = result["token_analysis"]
            comparison["token_efficiency"][prompt_id] = {
                "token_count": token_info.get("token_count", 0),
                "efficiency_score": token_info.get("efficiency_score", 0),
            }

            # 生成品質分析
            generations = result["generations"]
            if generations:
                avg_length = sum(len(gen["text"]) for gen in generations) / len(
                    generations
                )
                completion_rate = sum(
                    1 for gen in generations if gen["finish_reason"] == "stop"
                ) / len(generations)

                comparison["generation_quality"][prompt_id] = {
                    "avg_output_length": avg_length,
                    "completion_rate": completion_rate,
                    "generation_count": len(generations),
                }

        # 生成建議
        best_prompt = max(
            comparison["token_efficiency"].keys(),
            key=lambda x: comparison["generation_quality"][x]["completion_rate"],
        )

        comparison["recommendation"] = f"建議使用 {best_prompt}，具有最佳的完成率"

        return comparison

    def _save_ab_results(self, results: Dict):
        """儲存 A/B 測試結果"""
        filename = f"ab_test_{results['test_name']}_{int(time.time())}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"📊 測試結果已儲存: {filepath}")

    def optimize_prompt(
        self, base_prompt: str, optimization_goals: List[str], test_iterations: int = 5
    ) -> Dict:
        """智能提示詞最佳化"""

        print(f"🔧 開始提示詞最佳化...")

        # 基礎分析
        base_analysis = self.analyze_tokens(base_prompt)

        # 生成最佳化建議
        optimizations = []

        if "token_efficiency" in optimization_goals:
            optimizations.append(self._suggest_token_optimization(base_prompt))

        if "clarity" in optimization_goals:
            optimizations.append(self._suggest_clarity_optimization(base_prompt))

        if "specificity" in optimization_goals:
            optimizations.append(self._suggest_specificity_optimization(base_prompt))

        # 測試最佳化版本
        optimization_results = []

        for opt in optimizations:
            if opt["optimized_prompt"]:
                test_result = self.ab_test(
                    [base_prompt, opt["optimized_prompt"]],
                    f"optimization_{opt['type']}",
                    iterations=test_iterations,
                )
                optimization_results.append(
                    {
                        "type": opt["type"],
                        "suggestion": opt["suggestion"],
                        "test_result": test_result,
                    }
                )

        return {
            "base_prompt": base_prompt,
            "base_analysis": base_analysis,
            "optimization_goals": optimization_goals,
            "optimizations": optimization_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _suggest_token_optimization(self, prompt: str) -> Dict:
        """建議 token 最佳化"""
        # 簡單的最佳化邏輯 - 移除冗餘詞彙
        optimized = re.sub(r"\b(請|麻煩|能否|可以)\b", "", prompt)
        optimized = re.sub(r"\s+", " ", optimized).strip()

        return {
            "type": "token_efficiency",
            "suggestion": "移除冗餘詞彙以提高 token 效率",
            "optimized_prompt": optimized if optimized != prompt else None,
        }

    def _suggest_clarity_optimization(self, prompt: str) -> Dict:
        """建議清晰度最佳化"""
        # 添加結構化要求
        if "：" not in prompt and ":" not in prompt:
            optimized = f"{prompt}\n\n請以清楚的結構回應，包含：\n1. 主要內容\n2. 具體範例\n3. 總結"
        else:
            optimized = None

        return {
            "type": "clarity",
            "suggestion": "添加結構化要求以提高回應清晰度",
            "optimized_prompt": optimized,
        }

    def _suggest_specificity_optimization(self, prompt: str) -> Dict:
        """建議具體性最佳化"""
        # 添加具體的輸出要求
        if "字數" not in prompt and "長度" not in prompt:
            optimized = f"{prompt}\n\n要求：回應長度約 200-400 字，包含具體範例。"
        else:
            optimized = None

        return {
            "type": "specificity",
            "suggestion": "添加具體的輸出長度和格式要求",
            "optimized_prompt": optimized,
        }

    def list_templates(self, category: str = None) -> List[str]:
        """列出所有範本"""
        if category:
            return [
                name
                for name, template in self.templates.items()
                if template.category == category
            ]
        else:
            return list(self.templates.keys())

    def search_templates(self, query: str) -> List[str]:
        """搜尋範本"""
        results = []
        query = query.lower()

        for name, template in self.templates.items():
            if (
                query in name.lower()
                or query in template.description.lower()
                or any(query in tag.lower() for tag in template.tags)
            ):
                results.append(name)

        return results


def main():
    """主要執行函數"""
    print("🚀 TGW Prompt Engineering Tool")
    print("=" * 50)

    # 初始化工具
    engineer = TGWPromptEngineer()

    # 建立範例範本
    print("📝 建立範例範本...")

    # 技術文檔範本
    engineer.create_template(
        name="api_documentation",
        category="technical",
        template="""請為以下 API 端點生成完整文檔：

端點：{endpoint_url}
方法：{http_method}
功能：{description}

請包含：
1. 端點描述
2. 請求參數（必填/選填）
3. 請求範例
4. 回應格式
5. 錯誤代碼說明

格式：Markdown，包含程式碼區塊""",
        description="生成 API 技術文檔的標準範本",
        tags=["technical", "api", "documentation"],
        optimal_params={"temperature": 0.3, "top_p": 0.8, "repetition_penalty": 1.05},
    )

    # 創意寫作範本
    engineer.create_template(
        name="creative_writing",
        category="creative",
        template="""創作一個{genre}故事：

背景設定：{setting}
主角：{protagonist}
衝突：{conflict}
字數：{word_count}字

要求：
1. 引人入勝的開頭
2. 生動的角色描寫
3. 緊湊的情節發展
4. 符合{genre}類型特色""",
        description="創意寫作和故事創作範本",
        tags=["creative", "writing", "story"],
        optimal_params={"temperature": 0.8, "top_p": 0.95, "repetition_penalty": 1.1},
    )

    print("✅ 範例範本建立完成")
    print(f"📂 範本儲存位置: {engineer.templates_dir}")
    print(f"📊 結果儲存位置: {engineer.results_dir}")


if __name__ == "__main__":
    main()
