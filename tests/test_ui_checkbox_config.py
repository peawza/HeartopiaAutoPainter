import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6 import QtWidgets

from heartopia_painter.app import HumanizationOverrides, MainWindow


class TestUiCheckboxConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_checkboxes_follow_config_files(self):
        original_cwd = Path.cwd()
        temp_dir = tempfile.TemporaryDirectory()

        try:
            os.chdir(temp_dir.name)

            for enabled in (True, False):
                with self.subTest(enabled=enabled):
                    Path("config.json").write_text(
                        json.dumps(
                            {
                                "use_advanced_delays": enabled,
                                "use_hardware_mouse": enabled,
                                "enable_position_jitter": enabled,
                                "enable_micro_pauses": enabled,
                                "bucket_fill_enabled": enabled,
                                "bucket_fill_regions_enabled": enabled,
                            }
                        ),
                        encoding="utf-8",
                    )
                    Path("mouse_config.json").write_text(
                        json.dumps(
                            {
                                "enable_micro_pause": enabled,
                                "click_randomness_px": 3 if enabled else 0,
                                "enable_fatigue": enabled,
                                "enable_breaks": enabled,
                                "enable_mistakes": enabled,
                            }
                        ),
                        encoding="utf-8",
                    )

                    window = MainWindow()
                    self.assertEqual(window.chk_enhanced_timing.isChecked(), enabled)
                    self.assertEqual(window.chk_hardware_mouse.isChecked(), enabled)
                    self.assertEqual(window.chk_position_jitter.isChecked(), enabled)
                    self.assertEqual(window.chk_micro_pauses.isChecked(), enabled)
                    self.assertEqual(window.chk_fatigue.isChecked(), enabled)
                    self.assertEqual(window.chk_breaks.isChecked(), enabled)
                    self.assertEqual(window.chk_mistakes.isChecked(), enabled)
                    self.assertEqual(window.chk_bucket_fill.isChecked(), enabled)
                    self.assertEqual(window.chk_bucket_regions.isChecked(), enabled)

                    # Accessing the control verifies that Qt still owns the timing group.
                    self.assertIsInstance(window.spin_move.value(), int)

                    window.close()
                    window.deleteLater()
                    self.app.processEvents()
        finally:
            os.chdir(original_cwd)
            temp_dir.cleanup()

    def test_paint_mode_selection_updates_config(self):
        window = MainWindow()
        try:
            window.cbo_paint_mode.setCurrentIndex(1)
            self.assertEqual(window._cfg.paint_mode, "color")

            window.cbo_paint_mode.setCurrentIndex(0)
            self.assertEqual(window._cfg.paint_mode, "row")
        finally:
            window.close()
            window.deleteLater()
            self.app.processEvents()

    def test_humanization_overrides_are_session_only(self):
        original_cwd = Path.cwd()
        temp_dir = tempfile.TemporaryDirectory()

        try:
            os.chdir(temp_dir.name)
            original_config = {
                "use_advanced_delays": False,
                "delay_profile": "fast",
                "enable_position_jitter": False,
                "enable_micro_pauses": False,
            }
            Path("config.json").write_text(json.dumps(original_config), encoding="utf-8")
            Path("mouse_config.json").write_text(
                json.dumps({"enable_micro_pause": False, "click_randomness_px": 0}),
                encoding="utf-8",
            )

            window = MainWindow(
                humanization_overrides=HumanizationOverrides(
                    use_advanced_delays=True,
                    delay_profile="careful",
                    enable_position_jitter=True,
                    enable_micro_pauses=True,
                )
            )
            try:
                self.assertTrue(window._cfg.use_advanced_delays)
                self.assertEqual(window._cfg.delay_profile, "careful")
                self.assertTrue(window._cfg.enable_position_jitter)
                self.assertTrue(window._cfg.enable_micro_pauses)

                self.assertTrue(window.chk_enhanced_timing.isChecked())
                self.assertEqual(window.cbo_delay_profile.currentText(), "Careful")
                self.assertTrue(window.chk_position_jitter.isChecked())
                self.assertTrue(window.chk_micro_pauses.isChecked())

                saved_config = json.loads(Path("config.json").read_text(encoding="utf-8"))
                self.assertEqual(saved_config, original_config)
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()
        finally:
            os.chdir(original_cwd)
            temp_dir.cleanup()

    def test_hardware_input_guard_blocks_missing_port(self):
        window = MainWindow()
        try:
            window._cfg.use_hardware_mouse = True
            window._cfg.hardware_mouse_port = None

            with patch("heartopia_painter.app.QtWidgets.QMessageBox.warning") as warning_mock:
                allowed = window._confirm_hardware_input_guard("Painting")

            self.assertFalse(allowed)
            self.assertEqual(warning_mock.call_count, 1)
            self.assertIn("Hardware input blocked", warning_mock.call_args.args)
        finally:
            window.close()
            window.deleteLater()
            self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
