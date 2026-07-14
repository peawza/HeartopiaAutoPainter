import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6 import QtWidgets

from heartopia_painter.app import MainWindow


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


if __name__ == "__main__":
    unittest.main()
