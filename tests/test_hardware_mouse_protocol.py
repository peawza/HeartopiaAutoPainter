from __future__ import annotations

from collections import deque
from unittest.mock import patch

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


def test_connect_and_payload_commands_consume_trailing_acknowledgements():
    fake = FakeSerial(
        ["READY", "VERSION:1.1.0"],
        {
            "P": ["PONG", "OK"],
            "V": ["VERSION:1.1.0 (2026-07-14)", "OK"],
            "S": ["STATUS:commands=4,moves=1,clicks=0,delay=0us", "OK"],
            "M,5,-2": ["OK"],
        },
    )

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        assert mouse.connect() is True
        assert mouse.connected is True
        assert mouse.device_type == "Arduino/ESP32"
        assert mouse.device_version == "1.1.0 (2026-07-14)"
        assert mouse.ping() is True
        assert mouse.get_status() == {
            "commands": 4,
            "moves": 1,
            "clicks": 0,
            "delay": 0,
        }
        assert mouse.move(5, -2) is True
        mouse.disconnect()

    assert fake.writes == [b"P\n", b"V\n", b"P\n", b"S\n", b"M,5,-2\n"]
    assert fake.closed is True


def test_connect_failure_closes_serial_and_resets_state():
    fake = FakeSerial(["READY", "VERSION:1.1.0"], {})

    with patch("src.heartopia_painter.hardware_mouse.serial.Serial", return_value=fake), patch(
        "src.heartopia_painter.hardware_mouse.time.sleep"
    ):
        mouse = HardwareMouse(HardwareMouseConfig(port="COM6"))
        with pytest.raises(HardwareMouseError, match="did not respond to ping"):
            mouse.connect()

    assert mouse.connected is False
    assert mouse.serial is None
    assert fake.closed is True


def test_auto_detect_accepts_esp32_usb_serial_description():
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
