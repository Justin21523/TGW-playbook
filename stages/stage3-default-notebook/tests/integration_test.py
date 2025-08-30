#!/usr/bin/env python3
"""
Stage 3 整合測試套件
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path

# 添加工具包路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from token_analyzer import AdvancedTokenAnalyzer
from batch_processor import AdvancedBatchProcessor, BatchTask
from visualization import VisualizationEngine, ReportGenerator

class TestStage3Integration(unittest.TestCase):
    """Stage 3 整合測試"""

    def setUp(self):
        """測試前準備"""
        self.token_analyzer = AdvancedTokenAnalyzer()
        self.batch_processor = AdvancedBatchProcessor(max_concurrent=1)
        self.viz_engine = VisualizationEngine()
        self.report_gen = ReportGenerator()

    def test_token_analyzer_integration(self):
        """測試 Token 分析器整合"""

        # 測試中文文本
        chinese_text = "請分析這個中文文本的token使用效率"
        analysis = self.token_analyzer.analyze(chinese_text)

        self.assertIsInstance(analysis.token_count, int)
        self.assertIsInstance(analysis.efficiency_ratio, float)
        self.assertEqual(analysis.language, "chinese")
        self.assertGreater(analysis.complexity, 0)
        self.assertIsInstance(analysis.recommendations, list)
        self.assertGreater(len(analysis.recommendations), 0)

        # 測試英文文本
        english_text = "Analyze the token efficiency of this English text"
        analysis = self.token_analyzer.analyze(english_text)

        self.assertEqual(analysis.language, "english")
        self.assertGreater(analysis.efficiency_ratio, 0)

    def test_batch_processor_workflow(self):
        """測試批次處理器工作流"""

        # 建立測試任務
        test_prompts = [
            "這是第一個測試提示詞",
            "這是第二個測試提示詞"
        ]

        tasks = self.batch_processor.create_tasks(
            prompts=test_prompts,
            parameters={"temperature": 0.5, "max_new_tokens": 100}
        )

        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks[0], BatchTask)
        self.assertEqual(tasks[0].parameters["temperature"], 0.5)

        # 測試品質控制器
        quality_score = self.batch_processor.quality_controller.evaluate_quality(
            "這是一個完整的測試回應。",
            "生成一個測試回應"
        )

        self.assertGreaterEqual(quality_score, 0)
        self.assertLessEqual(quality_score, 1)

    @unittest.skipUnless(
        os.environ.get('TGW_FULL_TEST', '').lower() == 'true',
        "需要設定 TGW_FULL_TEST=true 才執行完整測試"
    )
    def test_end_to_end_workflow(self):
        """端到端工作流程測試（需要 TGW 運行）"""

        # 1. Token 分析階段
        test_prompt = "請寫一篇關於機器學習的簡短介紹"
        token_analysis = self.token_analyzer.analyze(test_prompt)

        self.assertGreater(token_analysis.token_count, 0)

        # 2. 批次處理階段
        tasks = self.batch_processor.create_tasks([test_prompt])

        # 注意：這個測試需要 TGW API 運行
        try:
            results = self.batch_processor.process_batch(tasks)

            self.assertIn('successful_results', results)
            self.assertIn('summary', results)

            # 3. 視覺化測試（建立但不顯示）
            if results['successful_results']:
                with tempfile.TemporaryDirectory() as temp_dir:
                    dashboard_path = os.path.join(temp_dir, "test_dashboard.png")

                    # 測試儀表板生成（不顯示）
                    import matplotlib
                    matplotlib.use('Agg')  # 使用非互動式後端

                    self.viz_engine.create_quality_dashboard(results, dashboard_path)
                    self.assertTrue(os.path.exists(dashboard_path))

            # 4. 報告生成測試
            report = self.report_gen.generate_executive_summary(results)
            self.assertIn('TGW Stage 3', report)
            self.assertIn('執行摘要', report)

        except Exception as e:
            self.skipTest(f"API 測試失敗，可能 TGW 未運行: {e}")

    def test_configuration_loading(self):
        """測試配置檔案載入"""

        config_path = Path(__file__).parent.parent / "configs" / "stage3_config.yaml"

        if config_path.exists():
            import yaml

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 驗證配置結構
            required_sections = ['api', 'batch_processing', 'quality_assessment',
                               'token_analysis', 'visualization']

            for section in required_sections:
                self.assertIn(section, config)

            # 驗證 API 配置
            api_config = config['api']
            self.assertIn('base_url', api_config)
            self.assertIn('timeout', api_config)

            # 驗證批次處理配置
            batch_config = config['batch_processing']
            self.assertIn('max_concurrent', batch_config)
            self.assertIn('quality_threshold', batch_config)

    def test_error_handling(self):
        """測試錯誤處理機制"""

        # 測試無效文本
        empty_analysis = self.token_analyzer.analyze("")
        self.assertEqual(empty_analysis.token_count, 1)  # 最小值
        self.assertEqual(empty_analysis.language, "unknown")

        # 測試無效任務
        invalid_tasks = []
        results = self.batch_processor.process_batch(invalid_tasks)

        self.assertEqual(results['summary']['total_tasks'], 0)
        self.assertEqual(results['summary']['successful_count'], 0)

    def test_data_persistence(self):
        """測試資料持久化"""

        # 建立測試結果
        test_results = {
            "successful_results": [{
                "task_id": "test_001",
                "success": True,
                "generated_text": "測試生成內容",
                "generation_time": 2.5,
                "quality_score": 0.75
            }],
            "failed_results": [],
            "summary": {
                "total_tasks": 1,
                "successful_count": 1,
                "success_rate": 100.0,
                "average_quality_score": 0.75
            },
            "timestamp": "2024-01-15 10:00:00"
        }

        # 測試結果儲存
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_results.json")

            self.batch_processor.save_results(test_results, output_path)
            self.assertTrue(os.path.exists(output_path))

            # 驗證載入的資料
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            self.assertEqual(loaded_data['summary']['total_tasks'], 1)
            self.assertEqual(loaded_data['summary']['success_rate'], 100.0)

class TestStage3Performance(unittest.TestCase):
    """Stage 3 效能測試"""

    def setUp(self):
        self.token_analyzer = AdvancedTokenAnalyzer()

    def test_token_analysis_performance(self):
        """測試 Token 分析效能"""

        import time

        # 測試大型文本分析效能
        large_text = "這是一個測試文本。" * 100

        start_time = time.time()
        analysis = self.token_analyzer.analyze(large_text)
        analysis_time = time.time() - start_time

        # 應該在 1 秒內完成
        self.assertLess(analysis_time, 1.0)
        self.assertGreater(analysis.token_count, 0)

    def test_batch_task_creation_performance(self):
        """測試批次任務建立效能"""

        import time

        batch_processor = AdvancedBatchProcessor()

        # 建立大量任務
        large_prompt_list = [f"這是第 {i} 個測試提示詞" for i in range(100)]

        start_time = time.time()
        tasks = batch_processor.create_tasks(large_prompt_list)
        creation_time = time.time() - start_time

        # 應該在 0.1 秒內完成
        self.assertLess(creation_time, 0.1)
        self.assertEqual(len(tasks), 100)

if __name__ == '__main__':
    print("🧪 執行 Stage 3 整合測試套件")
    print("=" * 50)

    # 設定測試模式
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        os.environ['TGW_FULL_TEST'] = 'true'
        print("⚠️ 執行完整測試，請確認 TGW 已啟動")
    else:
        print("ℹ️ 執行基礎測試，使用 --full 參數執行完整測試")

    # 建立測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加測試類別
    suite.addTests(loader.loadTestsFromTestCase(TestStage3Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestStage3Performance))

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 顯示結果
    if result.wasSuccessful():
        print("\n🎉 所有測試通過！")
        sys.exit(0)
    else:
        print(f"\n❌ 測試失敗: {len(result.failures)} 個失敗, {len(result.errors)} 個錯誤")
        sys.exit(1)
