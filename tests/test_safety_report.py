import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import main as launcher
from heartopia_painter.safety_report import build_safety_report, render_safety_report, render_safety_report_json


class TempCwd:
    def __enter__(self):
        self.original_cwd = Path.cwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        return Path(self.temp_dir.name)

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()


class TestSafetyReport(unittest.TestCase):
    def test_report_is_read_only_and_includes_actions_and_weighted_effectiveness(self):
        with TempCwd() as temp_dir:
            config = {
                "use_hardware_mouse": True,
                "hardware_mouse_port": "COM6",
                "use_advanced_delays": True,
                "delay_profile": "careful",
                "enable_position_jitter": True,
                "enable_micro_pauses": True,
                "verify_rows": True,
                "verify_max_passes": 6,
            }
            mouse_config = {"arduino_port": "COM4"}
            (temp_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
            (temp_dir / "mouse_config.json").write_text(json.dumps(mouse_config), encoding="utf-8")

            report = render_safety_report()

            self.assertIn("Action:", report)
            self.assertIn("Effectiveness Assessment:", report)
            self.assertIn("Overall weighted defensive effectiveness:", report)
            self.assertIn("Hardware mouse is enabled on COM6", report)
            self.assertIn("not an anti-detection or bypass report", report)
            self.assertIn("does not claim the program is undetectable", report)
            self.assertEqual(json.loads((temp_dir / "config.json").read_text(encoding="utf-8")), config)
            self.assertEqual(json.loads((temp_dir / "mouse_config.json").read_text(encoding="utf-8")), mouse_config)

    def test_json_report_has_stable_schema(self):
        with TempCwd():
            data = json.loads(render_safety_report_json())

        self.assertIn("findings", data)
        self.assertIn("scores", data)
        self.assertIn("total", data)
        self.assertIn("maximum", data)
        self.assertIn("has_failures", data)
        self.assertIn("boundary", data)
        self.assertIn("recommended_action", data["findings"][0])
        self.assertIn("weight", data["scores"][0])

    def test_malformed_config_fails_without_crashing(self):
        with TempCwd() as temp_dir:
            (temp_dir / "config.json").write_text("{broken json", encoding="utf-8")

            report = build_safety_report()

        self.assertTrue(report.has_failures)
        self.assertTrue(any(f.status == "FAIL" and f.category == "Config Integrity" for f in report.findings))

    def test_hardware_enabled_without_configured_port_fails(self):
        with TempCwd() as temp_dir:
            (temp_dir / "config.json").write_text(json.dumps({"use_hardware_mouse": True}), encoding="utf-8")
            (temp_dir / "mouse_config.json").write_text(json.dumps({}), encoding="utf-8")

            report = build_safety_report()

        self.assertTrue(report.has_failures)
        self.assertTrue(any(f.status == "FAIL" and f.category == "Hardware Input" for f in report.findings))

    def test_main_safety_report_outputs_text_without_gui(self):
        with patch("main._run_gui") as run_gui_mock, patch("sys.stdout", new_callable=StringIO) as stdout:
            result = launcher.main(["--safety-report"])

        self.assertEqual(result, 0)
        run_gui_mock.assert_not_called()
        self.assertIn("Heartopia Auto Painter - Safety Report", stdout.getvalue())
        self.assertIn("Effectiveness Assessment:", stdout.getvalue())

    def test_main_safety_report_json_outputs_json_without_gui(self):
        with patch("main._run_gui") as run_gui_mock, patch("sys.stdout", new_callable=StringIO) as stdout:
            result = launcher.main(["--safety-report-json"])

        self.assertEqual(result, 0)
        run_gui_mock.assert_not_called()
        self.assertIn("findings", json.loads(stdout.getvalue()))

    def test_strict_safety_returns_one_on_failure(self):
        with TempCwd() as temp_dir:
            (temp_dir / "config.json").write_text("{broken json", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO):
                result = launcher.main(["--safety-report", "--strict-safety"])

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
