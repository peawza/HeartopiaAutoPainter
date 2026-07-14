import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6 import QtCore, QtWidgets

from heartopia_painter.app import MainWindow
from heartopia_painter.overlay import RectSelectOverlay


class TestCanvasFixedSize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_canvas_size_parser(self):
        self.assertEqual(MainWindow._parse_canvas_size("661x659"), (661, 659))
        self.assertEqual(MainWindow._parse_canvas_size(" 661 × 659 "), (661, 659))
        self.assertIsNone(MainWindow._parse_canvas_size("661"))
        self.assertIsNone(MainWindow._parse_canvas_size("0x659"))

    def test_fixed_overlay_keeps_native_pixel_size_in_each_drag_direction(self):
        overlay = RectSelectOverlay(fixed_size=(661, 659))
        overlay._drag_start = QtCore.QPoint(200, 200)

        for drag_end in (QtCore.QPoint(300, 300), QtCore.QPoint(100, 100)):
            with self.subTest(drag_end=drag_end):
                overlay._drag_end = drag_end
                rect = overlay._current_rect()
                self.assertIsNotNone(rect)
                native = overlay._current_native_rect()
                self.assertIsNotNone(native)
                self.assertEqual((native.width(), native.height()), (661, 659))

        overlay.close()
        overlay.deleteLater()
        self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
