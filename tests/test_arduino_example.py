from __future__ import annotations

from unittest.mock import patch

import main
from example_arduino_connection import connect_with_retry


def test_main_dispatches_arduino_example_without_starting_gui():
    with patch("example_arduino_connection.run_example", return_value=0) as run_example:
        result = main.main(
            [
                "--arduino-example",
                "6",
                "--port",
                "COM6",
                "--baudrate",
                "9600",
                "--confirm-input",
            ]
        )

    assert result == 0
    run_example.assert_called_once_with(
        6,
        port="COM6",
        baudrate=9600,
        confirm_input=True,
    )


def test_retry_uses_exponential_backoff_and_cleans_failed_connections():
    instances = []
    sleeps = []

    class FakeMouse:
        def __init__(self, config):
            self.config = config
            self.connect_calls = 0
            self.disconnected = False
            instances.append(self)

        def connect(self):
            self.connect_calls += 1
            if len(instances) < 3:
                raise RuntimeError("not ready")

        def disconnect(self):
            self.disconnected = True

    connected = connect_with_retry(
        "COM6",
        attempts=3,
        mouse_factory=FakeMouse,
        sleep_fn=sleeps.append,
    )

    assert connected is instances[2]
    assert sleeps == [0.5, 1.0]
    assert instances[0].disconnected is True
    assert instances[1].disconnected is True
    assert instances[2].disconnected is False
