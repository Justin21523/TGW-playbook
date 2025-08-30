#!/usr/bin/env python3
"""
結果視覺化和報告生成系統
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class VisualizationEngine:
    """視覺化引擎"""

    def __init__(self, style: str = "seaborn-v0_8", figsize: tuple = (15, 10)):
        self.style = style
        self.figsize = figsize
        self.color_palette = {
            'primary': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#9b59b6',
            'secondary': '#95a5a6'
        }

    def create_quality_dashboard(self, results: Dict[str, Any], save_path: str = None):
        """建立品質分析儀表板"""

        if not results.get("successful_results"):
            print("沒有成功的結果可以視覺化")
            return

        plt.style.use(self.style)
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('TGW 批次處理品質分析儀表板', fontsize=16, fontweight='bold')

        # 準備資料
        successful = results["successful_results"]
        quality_scores = [r["quality_score"] for r in successful]
        generation_times = [r["generation_time"] for r in successful]

        # 1. 品質分數分佈直方圖
        axes[0, 0].hist(quality_scores, bins=20, color=self.color_palette['primary'], alpha=0.7)
        axes[0, 0].axvline(np.mean(quality_scores), color=self.color_palette['danger'],
                          linestyle='--', label=f'平均值: {np.mean(quality_scores):.3f}')
        axes[0, 0].set_title('品質分數分佈')
        axes[0, 0].set_xlabel('品質分數')
        axes[0, 0].set_ylabel('頻率')
        axes[0, 0].legend()

        # 2. 品質等級圓餅圖
        summary = results.get("summary", {})
        quality_dist = summary.get("quality_distribution", {})

        if quality_dist:
            labels = list(quality_dist.keys())
            sizes = list(quality_dist.values())
            colors = [self.color_palette['success'], self.color_palette['primary'],
                     self.color_palette['warning'], self.color_palette['danger']]

            axes[0, 1].pie(sizes, labels=labels, colors=colors[:len(sizes)],
                          autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('品質等級分佈')

        # 3. 生成時間散點圖
        axes[0, 2].scatter(range(len(generation_times)), generation_times,
                          c=quality_scores, cmap='viridis', alpha=0.6)
        axes[0, 2].set_title('生成時間 vs 品質分數')
        axes[0, 2].set_xlabel('任務序號')
        axes[0, 2].set_ylabel('生成時間 (秒)')
        colorbar = plt.colorbar(axes[0, 2].collections[0], ax=axes[0, 2])
        colorbar.set_label('品質分數')

        # 4. 品質分數箱線圖
        axes[1, 0].boxplot(quality_scores, patch_artist=True,
                          boxprops=dict(facecolor=self.color_palette['info'], alpha=0.7))
        axes[1, 0].set_title('品質分數分佈統計')
        axes[1, 0].set_ylabel('品質分數')

        # 5. 時間效率分析
        efficiency_scores = [q/max(t, 0.1) for q, t in zip(quality_scores, generation_times)]
        axes[1, 1].bar(range(len(efficiency_scores)), sorted(efficiency_scores, reverse=True),
                      color=self.color_palette['warning'])
        axes[1, 1].set_title('效率分數排名 (品質/時間)')
        axes[1, 1].set_xlabel('任務排名')
        axes[1, 1].set_ylabel('效率分數')

        # 6. 成功率和統計摘要
        stats_data = {
            '總任務數': summary.get('total_tasks', 0),
            '成功任務': summary.get('successful_count', 0),
            '失敗任務': summary.get('failed_count', 0),
            '成功率 (%)': summary.get('success_rate', 0),
            '平均品質': summary.get('average_quality_score', 0),
            '平均時間 (秒)': summary.get('average_generation_time', 0)
        }

        # 建立統計表格
        axes[1, 2].axis('tight')
        axes[1, 2].axis('off')

        table_data = [[key, f"{value:.3f}" if isinstance(value, float) and key != '成功率 (%)'
                      else f"{value:.1f}%" if key == '成功率 (%)'
                      else str(value)] for key, value in stats_data.items()]

        table = axes[1, 2].table(cellText=table_data,
                                colLabels=['指標', '數值'],
                                cellLoc='center',
                                loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        axes[1, 2].set_title('處理統計摘要')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"儀表板已儲存到: {save_path}")

        plt.show()

    def create_comparison_chart(self, comparison_data: List[Dict[str, Any]],
                               save_path: str = None):
        """建立比較圖表"""

        plt.style.use(self.style)
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle('參數組合效果比較', fontsize=16, fontweight='bold')

        # 準備資料
        names = [item['name'] for item in comparison_data]
        quality_scores = [item['avg_quality'] for item in comparison_data]
        generation_times = [item['avg_time'] for item in comparison_data]
        success_rates = [item['success_rate'] for item in comparison_data]

        colors = [self.color_palette['primary'], self.color_palette['success'],
                 self.color_palette['warning']][:len(names)]

        # 1. 品質分數比較
        axes[0, 0].bar(names, quality_scores, color=colors)
        axes[0, 0].set_title('平均品質分數比較')
        axes[0, 0].set_ylabel('品質分數')
        axes[0, 0].set_ylim(0, 1)

        # 2. 生成時間比較
        axes[0, 1].bar(names, generation_times, color=colors)
        axes[0, 1].set_title('平均生成時間比較')
        axes[0, 1].set_ylabel('時間 (秒)')

        # 3. 成功率比較
        axes[1, 0].bar(names, success_rates, color=colors)
        axes[1, 0].set_title('成功率比較')
        axes[1, 0].set_ylabel('成功率 (%)')
        axes[1, 0].set_ylim(0, 100)

        # 4. 綜合效率分數
        efficiency_scores = [q * s / max(t, 0.1) for q, s, t in
                           zip(quality_scores, [sr/100 for sr in success_rates], generation_times)]

        axes[1, 1].bar(names, efficiency_scores, color=colors)
        axes[1, 1].set_title('綜合效率分數')
        axes[1, 1].set_ylabel('效率分數')

        # 調整 x 軸標籤角度
        for ax in axes.flat:
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"比較圖表已儲存到: {save_path}")

        plt.show()

    def generate_trend_analysis(self, historical_data: List[Dict[str, Any]],
                               save_path: str = None):
        """生成趨勢分析圖"""

        if len(historical_data) < 2:
            print("需要至少兩組資料才能進行趨勢分析")
            return

        plt.style.use(self.style)
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle('歷史趨勢分析', fontsize=16, fontweight='bold')

        # 準備時間軸資料
        timestamps = [item['timestamp'] for item in historical_data]
        quality_trends = [item['summary']['average_quality_score'] for item in historical_data]
        time_trends = [item['summary']['average_generation_time'] for item in historical_data]
        success_trends = [item['summary']['success_rate'] for item in historical_data]

        # 1. 品質分數趨勢
        axes[0, 0].plot(timestamps, quality_trends, marker='o',
                       color=self.color_palette['primary'], linewidth=2)
        axes[0, 0].set_title('品質分數趨勢')
        axes[0, 0].set_ylabel('平均品質分數')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # 2. 生成時間趨勢
        axes[0, 1].plot(timestamps, time_trends, marker='s',
                       color=self.color_palette['warning'], linewidth=2)
        axes[0, 1].set_title('生成時間趨勢')
        axes[0, 1].set_ylabel('平均生成時間 (秒)')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. 成功率趨勢
        axes[1, 0].plot(timestamps, success_trends, marker='^',
                       color=self.color_palette['success'], linewidth=2)
        axes[1, 0].set_title('成功率趨勢')
        axes[1, 0].set_ylabel('成功率 (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # 4. 綜合改進指標
        baseline_quality = quality_trends[0]
        baseline_time = time_trends[0]

        improvement_scores = []
        for q, t in zip(quality_trends, time_trends):
            # 品質改進 + 時間效率改進
            quality_improvement = (q - baseline_quality) / max(baseline_quality, 0.1)
            time_improvement = (baseline_time - t) / max(baseline_time, 0.1)
            improvement_scores.append(quality_improvement + time_improvement)

        axes[1, 1].bar(range(len(improvement_scores)), improvement_scores,
                      color=[self.color_palette['success'] if score >= 0 else self.color_palette['danger']
                            for score in improvement_scores])
        axes[1, 1].set_title('相對改進指標')
        axes[1, 1].set_ylabel('改進分數')
        axes[1, 1].set_xlabel('測試輪次')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"趨勢分析圖已儲存到: {save_path}")

        plt.show()

class ReportGenerator:
    """報告生成器"""

    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "configs" / "templates"

    def generate_executive_summary(self, results: Dict[str, Any]) -> str:
        """生成執行摘要報告"""

        summary = results.get("summary", {})
        timestamp = results.get("timestamp", datetime.now().isoformat())

        report = f"""# TGW Stage 3 批次處理執行摘要

**生成時間**: {timestamp}
**分析版本**: Advanced Batch Processor v1.0

## 📊 關鍵指標

| 指標 | 數值 | 狀態 |
|------|------|------|
| 總任務數 | {summary.get('total_tasks', 0)} | - |
| 成功任務 | {summary.get('successful_count', 0)} | {'✅' if summary.get('success_rate', 0) >= 90 else '⚠️'} |
| 成功率 | {summary.get('success_rate', 0):.1f}% | {'優秀' if summary.get('success_rate', 0) >= 95 else '良好' if summary.get('success_rate', 0) >= 80 else '需改進'} |
| 平均品質分數 | {summary.get('average_quality_score', 0):.3f} | {'優秀' if summary.get('average_quality_score', 0) >= 0.8 else '良好' if summary.get('average_quality_score', 0) >= 0.6 else '需改進'} |
| 平均處理時間 | {summary.get('average_generation_time', 0):.2f} 秒 | {'快速' if summary.get('average_generation_time', 0) <= 5 else '適中' if summary.get('average_generation_time', 0) <= 10 else '較慢'} |

## 🎯 品質分析
"""

        # 品質分佈分析
        quality_dist = summary.get("quality_distribution", {})
        if quality_dist:
            total = sum(quality_dist.values())
            report += f"""
### 品質等級分佈

- **優秀** (≥0.8): {quality_dist.get('excellent', 0)} 個 ({quality_dist.get('excellent', 0)/total*100:.1f}%)
- **良好** (0.6-0.8): {quality_dist.get('good', 0)} 個 ({quality_dist.get('good', 0)/total*100:.1f}%)
- **可接受** (0.4-0.6): {quality_dist.get('acceptable', 0)} 個 ({quality_dist.get('acceptable', 0)/total*100:.1f}%)
- **需改進** (<0.4): {quality_dist.get('poor', 0)} 個 ({quality_dist.get('poor', 0)/total*100:.1f}%)
"""

        # 建議和下一步行動
        report += f"""
## 💡 關鍵洞察與建議

### 表現亮點
"""

        success_rate = summary.get('success_rate', 0)
        avg_quality = summary.get('average_quality_score', 0)
        avg_time = summary.get('average_generation_time', 0)

        if success_rate >= 95:
            report += "- 🎉 成功率優秀，系統穩定性佳\n"
        if avg_quality >= 0.8:
            report += "- ⭐ 生成品質優秀，參數調教有效\n"
        if avg_time <= 5:
            report += "- ⚡ 處理速度快，效率優異\n"

        report += """
### 改進建議
"""

        if success_rate < 90:
            report += "- 🔧 檢查 API 連接穩定性，優化錯誤處理機制\n"
        if avg_quality < 0.6:
            report += "- 📝 優化提示詞結構，增加具體要求和範例\n"
        if avg_time > 10:
            report += "- ⏱️ 考慮調整 max_new_tokens 參數或優化並行處理\n"

        report += f"""
### 下一步行動計畫

1. **短期 (1-2 週)**
   - 針對品質不佳的任務類型優化提示詞
   - 調整參數組合以提升整體表現
   - 建立更完善的品質評估標準

2. **中期 (1 個月)**
   - 實施 A/B 測試框架進行系統化優化
   - 建立歷史資料分析和趨勢監控
   - 開發自定義品質評估指標

3. **長期 (3 個月)**
   - 整合機器學習模型進行智能參數調優
   - 建立自動化品質改進流程
   - 擴展批次處理能力和規模

## 📈 技術指標

- **平均 Token 效率**: 預估 2.5+ 字符/token
- **並行處理能力**: {summary.get('total_tasks', 0)} 任務，最大並行度 3
- **品質控制**: 啟用自動重試機制
- **可靠性**: {success_rate:.1f}% 成功率

---

*本報告由 TGW Advanced Batch Processor 自動生成*
"""

        return report

    def save_report(self, report_content: str, output_path: str):
        """儲存報告"""

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"執行摘要報告已儲存到: {output_file}")

# 使用範例
if __name__ == "__main__":
    # 建立模擬資料進行測試
    sample_results = {
        "successful_results": [
            {"quality_score": 0.85, "generation_time": 3.2},
            {"quality_score": 0.72, "generation_time": 4.1},
            {"quality_score": 0.91, "generation_time": 2.8}
        ],
        "failed_results": [],
        "summary": {
            "total_tasks": 3,
            "successful_count": 3,
            "success_rate": 100.0,
            "average_quality_score": 0.826,
            "average_generation_time": 3.37,
            "quality_distribution": {
                "excellent": 2,
                "good": 1,
                "acceptable": 0,
                "poor": 0
            }
        },
        "timestamp": "2024-01-15 10:30:00"
    }

    # 測試視覺化
    viz_engine = VisualizationEngine()
    viz_engine.create_quality_dashboard(sample_results)

    # 測試報告生成
    report_gen = ReportGenerator()
    report = report_gen.generate_executive_summary(sample_results)
    print("生成的執行摘要:")
    print(report[:500] + "...")
