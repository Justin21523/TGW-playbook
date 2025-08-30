#!/usr/bin/env python3
"""
進階 Token 分析器
提供詳細的 tokenization 分析和最佳化建議
"""

import re
import json
import time
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TokenAnalysis:
    """Token 分析結果資料類別"""
    text: str
    token_count: int
    char_count: int
    efficiency_ratio: float
    language: str
    complexity: float
    quality_indicators: Dict[str, float]
    recommendations: List[str]

class AdvancedTokenAnalyzer:
    """進階 Token 分析器"""

    def __init__(self, api_base: str = "http://localhost:5000"):
        self.api_base = api_base
        self.session = requests.Session()

    def analyze(self, text: str) -> TokenAnalysis:
        """執行完整的 Token 分析"""

        # 基本資訊
        char_count = len(text)
        token_count = self._get_token_count(text)
        efficiency_ratio = char_count / max(token_count, 1)

        # 語言檢測
        language = self._detect_language(text)

        # 複雜度計算
        complexity = self._calculate_complexity(text)

        # 品質指標
        quality_indicators = self._assess_quality_indicators(text)

        # 生成建議
        recommendations = self._generate_recommendations(
            efficiency_ratio, complexity, quality_indicators
        )

        return TokenAnalysis(
            text=text,
            token_count=token_count,
            char_count=char_count,
            efficiency_ratio=round(efficiency_ratio, 3),
            language=language,
            complexity=round(complexity, 3),
            quality_indicators=quality_indicators,
            recommendations=recommendations
        )

    def _get_token_count(self, text: str) -> int:
        """獲取 Token 數量"""
        try:
            response = self.session.post(
                f"{self.api_base}/v1/internal/tokenize",
                json={"text": text},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return len(data.get("tokens", []))
            else:
                # 如果 API 不可用，使用估算
                return self._estimate_tokens(text)

        except Exception:
            return self._estimate_tokens(text)

    def _estimate_tokens(self, text: str) -> int:
        """估算 Token 數量"""
        # 基於語言特性的估算公式
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        numbers = len(re.findall(r'\d+', text))

        # 中文字符大約 1.5 tokens，英文詞彙大約 1.3 tokens
        estimated = chinese_chars * 1.5 + english_words * 1.3 + numbers * 0.8

        return max(int(estimated), 1)

    def _detect_language(self, text: str) -> str:
        """檢測主要語言"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.sub(r'\s', '', text))

        if total_chars == 0:
            return "unknown"

        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars

        if chinese_ratio > 0.4:
            return "chinese"
        elif english_ratio > 0.6:
            return "english"
        else:
            return "mixed"

    def _calculate_complexity(self, text: str) -> float:
        """計算文本複雜度"""
        if not text:
            return 0.0

        # 詞彙多樣性
        words = text.split()
        vocab_diversity = len(set(words)) / max(len(words), 1)

        # 句子長度變異
        sentences = re.split(r'[.!?。！？]', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]

        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            length_variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            length_complexity = min(1.0, length_variance / 100)
        else:
            length_complexity = 0

        # 標點符號複雜度
        punctuation_density = len(re.findall(r'[^\w\s]', text)) / max(len(text), 1)

        # 綜合複雜度分數
        complexity = (
            vocab_diversity * 0.4 +
            length_complexity * 0.3 +
            punctuation_density * 0.3
        )

        return min(1.0, complexity)

    def _assess_quality_indicators(self, text: str) -> Dict[str, float]:
        """評估品質指標"""
        indicators = {}

        # 結構性指標
        has_structure = any(indicator in text for indicator in ['：', ':', '1.', '2.', '•', '-'])
        indicators['structure'] = 1.0 if has_structure else 0.3

        # 具體性指標
        specificity_words = ['具體', '詳細', '範例', '步驟', '方法', '包含', '要求']
        specificity_count = sum(1 for word in specificity_words if word in text)
        indicators['specificity'] = min(1.0, specificity_count / 3)

        # 完整性指標
        has_requirements = any(req in text for req in ['要求', '需要', '必須', '應該'])
        has_format = any(fmt in text for fmt in ['格式', '樣式', '形式'])
        indicators['completeness'] = (has_requirements + has_format) / 2

        return indicators

    def _generate_recommendations(self,
                                efficiency: float,
                                complexity: float,
                                quality: Dict[str, float]) -> List[str]:
        """生成最佳化建議"""
        recommendations = []

        # 效率建議
        if efficiency < 2.0:
            recommendations.append("建議移除冗餘詞彙以提高 token 效率")
            recommendations.append("考慮使用更精簡的表達方式")
        elif efficiency > 4.0:
            recommendations.append("可以適當增加具體要求以提高指導性")

        # 複雜度建議
        if complexity < 0.3:
            recommendations.append("可以增加結構化要求提高提示詞品質")
        elif complexity > 0.8:
            recommendations.append("建議簡化表達以提高可讀性")

        # 品質建議
        if quality.get('structure', 0) < 0.5:
            recommendations.append("建議添加編號或列表來組織內容")

        if quality.get('specificity', 0) < 0.5:
            recommendations.append("增加具體的輸出要求和範例")

        return recommendations if recommendations else ["提示詞品質良好，建議保持現有風格"]

# 使用範例
if __name__ == "__main__":
    analyzer = AdvancedTokenAnalyzer()

    sample_text = "請寫一份關於人工智慧發展的報告"
    analysis = analyzer.analyze(sample_text)

    print("Token 分析結果:")
    print(f"  Token 數量: {analysis.token_count}")
    print(f"  效率比率: {analysis.efficiency_ratio}")
    print(f"  語言類型: {analysis.language}")
    print(f"  複雜度: {analysis.complexity}")
    print(f"  建議: {analysis.recommendations[0]}")
