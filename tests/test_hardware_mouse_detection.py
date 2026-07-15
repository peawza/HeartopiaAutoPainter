import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, "src")

from heartopia_painter.hardware_mouse import HardwareMouse, HardwareMouseConfig


def make_port(device, vid, pid, description="USB Serial Device", manufacturer=None):
    return SimpleNamespace(
        device=device,
        vid=vid,
        pid=pid,
        description=description,
        manufacturer=manufacturer,
    )


def test_auto_detects_standard_leonardo():
    """Test auto-detection of standard Arduino Leonardo."""
    port = make_port("COM7", 0x2341, 0x8036, "Arduino Leonardo", "Arduino LLC")
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM7"


def test_auto_detects_sparkfun_pro_micro():
    """Test auto-detection of SparkFun Pro Micro."""
    port = make_port("COM8", 0x1B4F, 0x9205, "SparkFun Pro Micro", "SparkFun")
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM8"


def test_auto_detects_esp32_by_manufacturer():
    """Test auto-detection of ESP32 by Espressif manufacturer."""
    port = make_port("COM9", 0x303A, 0x1001, "USB JTAG/serial debug unit", "Espressif Systems")
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM9"


def test_auto_detects_by_description_keyword():
    """Test auto-detection by description keyword match."""
    port = make_port("COM10", None, None, "Arduino Leonardo (COM10)", None)
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM10"


def test_does_not_detect_unsupported_device():
    """Test that unsupported devices are not detected."""
    port = make_port("COM5", 0x0000, 0x0000, "Some Other Device", "Other Manufacturer")
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() is None

