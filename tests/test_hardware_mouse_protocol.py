from __future__ import annotations

from collections import deque
from unittest.mock import patch, MagicMock
import threading
import time

import pytest

from src.heartopia_painter.hardware_mouse import (
    HardwareMouse,
    HardwareMouseConfig,
    HardwareMouseError,
)


class FakeSerial:
    def __init__(self, startup, command_responses):
        self.startup = deque(response.encode("utf-8") + b"\n" for response in startup)
        self.command_responses = {
            command: deque(response.encode("utf-8") + b"\n" for response in responses)
            for command, responses in command_responses.items()
        }
        self.responses = deque()
        self.writes = []
        self.timeout = 1.0
        self.closed = False

    @property
    def in_waiting(self):
        return len(self.startup) + len(self.responses)

    def write(self, payload):
        self.writes.append(payload)
        command = payload.decode("utf-8").strip()
        self.responses.extend(self.command_responses.get(command, ()))

    def readline(self):
        if self.startup:
            return self.startup.popleft()
        return self.responses.popleft() if self.responses else b""

    def close(self):
        self.closed = True


def test_connect_drains_startup_messages_before_handshake():
    """Test that startup messages are drained before performing handshake."""
    fake = FakeSerial(
        ["READY", "VERSION:1.1.0", "Extra startup line"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        assert mouse.connect() is True
        assert mouse.connected is True
        assert mouse.device_version == "1.1.0 (2026-07-14)"
        # Verify startup messages were consumed
        assert len(fake.startup) == 0
        mouse.disconnect()

    assert fake.closed is True


def test_connect_sets_device_port_before_connected_flag():
    """Test that device_port is set before connected flag to avoid race conditions."""
    fake = FakeSerial(
        ["READY", "VERSION:1.1.0"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        assert mouse.connect() is True
        assert mouse.device_port == "COM6"
        assert mouse.connected is True
        mouse.disconnect()

    assert fake.closed is True


def test_ping_handshake_validates_firmware():
    """Test that ping handshake properly validates the firmware is present."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        assert mouse.connect() is True
        assert mouse.device_type == "Arduino/ESP32"
        mouse.disconnect()

    # Verify ping was sent during connection
    assert b"P\n" in fake.writes
    assert fake.closed is True


def test_version_command_consumes_payload_and_ok():
    """Test that V command properly consumes both payload and OK response."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        assert mouse.connect() is True
        assert mouse.device_version == "1.1.0 (2026-07-14)"
        # Verify both lines were consumed
        assert len(fake.responses) == 0
        mouse.disconnect()

    assert fake.closed is True


def test_status_command_returns_parsed_dict():
    """Test that S command returns properly parsed status dictionary."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "S": ["STATUS:commands=10,moves=5,clicks=2,delay=1000us", "OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        status = mouse.get_status()
        assert status == {
            "commands": 10,
            "moves": 5,
            "clicks": 2,
            "delay": 1000,
        }
        mouse.disconnect()

    assert fake.closed is True


def test_move_command_sends_correct_format():
    """Test that move commands use M,dx,dy format."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "M,100,-50": ["OK"],
            "M,-25,75": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.move(100, -50) is True
        assert mouse.move(-25, 75) is True
        mouse.disconnect()

    assert b"M,100,-50\n" in fake.writes
    assert b"M,-25,75\n" in fake.writes
    assert fake.closed is True


def test_click_command_increments_statistics():
    """Test that click command increments the click counter."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "C": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        initial_clicks = mouse.total_clicks
        assert mouse.click() is True
        assert mouse.total_clicks == initial_clicks + 1
        mouse.disconnect()

    assert b"C\n" in fake.writes
    assert fake.closed is True


def test_connect_failure_on_ping_resets_connected_flag():
    """Test that connection failure during ping resets the connected flag."""
    fake = FakeSerial(
        ["READY"],
        {},  # No responses, ping will fail
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        with pytest.raises(HardwareMouseError, match="did not respond to ping"):
            mouse.connect()

    assert mouse.connected is False
    assert mouse.serial is None
    assert fake.closed is True


def test_connect_failure_cleans_up_serial_port():
    """Test that connection failure properly cleans up the serial port."""
    fake = FakeSerial(["READY"], {})

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        try:
            mouse.connect()
        except HardwareMouseError:
            pass

    assert mouse.serial is None
    assert mouse.connected is False
    assert fake.closed is True


def test_multiple_commands_maintain_acknowledgement_sync():
    """Test that multiple commands properly maintain sync with acknowledgements."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "M,10,0": ["OK"],
            "M,0,10": ["OK"],
            "C": ["OK"],
            "M,-10,-10": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.move(10, 0) is True
        assert mouse.move(0, 10) is True
        assert mouse.click() is True
        assert mouse.move(-10, -10) is True
        mouse.disconnect()

    expected_commands = [b"P\n", b"V\n", b"M,10,0\n", b"M,0,10\n", b"C\n", b"M,-10,-10\n"]
    assert fake.writes == expected_commands
    assert fake.closed is True


def test_auto_detect_accepts_esp32_usb_serial_description():
    """Test that auto-detection recognizes ESP32 devices."""
    class Port:
        device = "COM7"
        description = "USB JTAG/serial debug unit"
        manufacturer = "Espressif Systems"
        vid = None
        pid = None

    with patch(
        "src.heartopia_painter.hardware_mouse.serial.tools.list_ports.comports",
        return_value=[Port()],
    ):
        mouse = HardwareMouse(HardwareMouseConfig())
        assert mouse._auto_detect_port() == "COM7"


def test_auto_detect_accepts_arduino_leonardo():
    """Test that auto-detection recognizes Arduino Leonardo by VID/PID."""
    class Port:
        device = "COM3"
        description = "Arduino Leonardo"
        manufacturer = "Arduino LLC"
        vid = 0x2341
        pid = 0x8036

    with patch(
        "src.heartopia_painter.hardware_mouse.serial.tools.list_ports.comports",
        return_value=[Port()],
    ):
        mouse = HardwareMouse(HardwareMouseConfig())
        assert mouse._auto_detect_port() == "COM3"


def test_auto_detect_accepts_sparkfun_pro_micro():
    """Test that auto-detection recognizes SparkFun Pro Micro."""
    class Port:
        device = "COM4"
        description = "SparkFun Pro Micro"
        manufacturer = "SparkFun"
        vid = 0x1B4F
        pid = 0x9205

    with patch(
        "src.heartopia_painter.hardware_mouse.serial.tools.list_ports.comports",
        return_value=[Port()],
    ):
        mouse = HardwareMouse(HardwareMouseConfig())
        assert mouse._auto_detect_port() == "COM4"


def test_context_manager_connects_and_disconnects():
    """Test that context manager properly connects and disconnects."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "M,50,50": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        with HardwareMouse(HardwareMouseConfig(port="COM6")) as mouse:
            assert mouse.connected is True
            assert mouse.move(50, 50) is True

    # After exiting context, should be disconnected
    assert fake.closed is True


def test_press_release_commands():
    """Test that press and release commands work correctly."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "D": ["OK"],
            "U": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.press() is True
        assert mouse.release() is True
        mouse.disconnect()

    assert b"D\n" in fake.writes
    assert b"U\n" in fake.writes
    assert fake.closed is True


def test_wait_command():
    """Test that wait command sends correct format."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "W,500": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.wait(500) is True
        mouse.disconnect()

    assert b"W,500\n" in fake.writes
    assert fake.closed is True


def test_set_min_delay_command():
    """Test that set_min_delay command sends correct format."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "SETDELAY,1000": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.set_min_delay(1000) is True
        mouse.disconnect()

    assert b"SETDELAY,1000\n" in fake.writes
    assert fake.closed is True


def test_smooth_move_command():
    """Test that smooth move command sends correct format."""
    fake = FakeSerial(
        ["READY"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "MS,100,50,20": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        mouse.connect()
        assert mouse.move_smooth(100, 50, steps=20) is True
        mouse.disconnect()

    assert b"MS,100,50,20\n" in fake.writes
    assert fake.closed is True
