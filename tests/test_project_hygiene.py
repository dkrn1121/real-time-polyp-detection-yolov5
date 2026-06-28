import importlib
import inspect
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ProjectHygieneTests(unittest.TestCase):
    def test_download_dataset_uses_environment_api_key(self):
        source = (ROOT / "download_dataset_fixed.py").read_text(encoding="utf-8")

        self.assertIn("ROBOFLOW_API_KEY", source)
        self.assertIsNone(re.search(r"api_key\s*=\s*['\"][^'\"]+['\"]", source))

    def test_benchmark_module_exposes_reusable_metrics_helpers(self):
        benchmark = importlib.import_module("benchmark_fps")

        self.assertTrue(hasattr(benchmark, "compute_speed_summary"))
        summary = benchmark.compute_speed_summary(frame_count=253, elapsed_seconds=9.0524)

        self.assertAlmostEqual(summary["avg_ms_per_frame"], 35.7802, places=3)
        self.assertAlmostEqual(summary["fps"], 27.948, places=3)

    def test_benchmark_has_no_import_time_model_loading(self):
        benchmark = importlib.import_module("benchmark_fps")
        source = inspect.getsource(benchmark)

        self.assertIn("if __name__ == \"__main__\":", source)
        import_safe_prefix = source.split("def run_benchmark", 1)[0]
        self.assertNotIn("YOLO(", import_safe_prefix)


if __name__ == "__main__":
    unittest.main()
