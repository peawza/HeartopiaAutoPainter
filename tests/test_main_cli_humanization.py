import sys
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main as launcher


class TestMainCliHumanization(unittest.TestCase):
    @patch("main._run_gui")
    def test_humanized_profile_passes_session_overrides(self, run_gui_mock):
        result = launcher.main(["--humanized", "--human-profile", "careful"])

        self.assertEqual(result, 0)
        run_gui_mock.assert_called_once_with(
            hardware_click=False,
            port=None,
            baudrate=115200,
            humanized=True,
            human_profile="careful",
            position_jitter=None,
            micro_pauses=None,
        )

    @patch("main._run_gui")
    def test_boolean_humanization_flags_resolve(self, run_gui_mock):
        result = launcher.main(["--position-jitter", "--no-micro-pauses"])

        self.assertEqual(result, 0)
        run_gui_mock.assert_called_once_with(
            hardware_click=False,
            port=None,
            baudrate=115200,
            humanized=None,
            human_profile=None,
            position_jitter=True,
            micro_pauses=False,
        )

    def test_invalid_human_profile_is_rejected(self):
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as cm:
                launcher.main(["--human-profile", "turbo"])

        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
