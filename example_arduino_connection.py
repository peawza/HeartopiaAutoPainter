"""Arduino/ESP32 serial connection examples.

Run directly with ``python example_arduino_connection.py --example 1`` or
through the application launcher with ``python main.py --arduino-example 1``.
Examples that move or click the physical mouse require ``--confirm-input`` or
an interactive confirmation.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Callable, Optional


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import serial

from heartopia_painter.hardware_mouse import (
    HardwareMouse,
    HardwareMouseConfig,
    HardwareMouseError,
    find_arduino_port,
    list_available_ports,
)


def _format_vid_pid(vid: Optional[int], pid: Optional[int]) -> str:
    if vid is None or pid is None:
        return "unknown"
    return f"{vid:04X}:{pid:04X}"


def _select_port(port: Optional[str]) -> Optional[str]:
    return port or find_arduino_port()


def inspect_ports() -> int:
    """List available serial ports and their reported USB identity."""
    ports = list_available_ports()
    if not ports:
        print("No serial ports found.")
        return 1

    for item in ports:
        print(
            f"{item['device']}: {item['description'] or 'Unknown'} | "
            f"manufacturer={item['manufacturer'] or 'Unknown'} | "
            f"VID:PID={_format_vid_pid(item['vid'], item['pid'])}"
        )
    return 0


def inspect_device_identity(port: Optional[str] = None) -> int:
    """Report the actual descriptor returned by the selected serial device."""
    ports = list_available_ports()
    if port:
        ports = [item for item in ports if item["device"].lower() == port.lower()]
    if not ports:
        print("The requested serial device was not found.")
        return 1

    for item in ports:
        print(f"Device: {item['device']}")
        print(f"Description: {item['description'] or 'Unknown'}")
        print(f"Manufacturer: {item['manufacturer'] or 'Unknown'}")
        print(f"VID:PID: {_format_vid_pid(item['vid'], item['pid'])}")
    return 0


class SimpleArduinoMouse:
    """Small direct-serial wrapper matching the Arduino firmware protocol."""

    def __init__(self, baudrate: int = 115200, timeout: float = 1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None

    def connect(self, port: str) -> bool:
        try:
            self.serial = serial.Serial(port, self.baudrate, timeout=self.timeout)
            time.sleep(0.5)
            self._drain_startup()
            if self._send("P") != "PONG":
                self.disconnect()
                return False
            return True
        except (serial.SerialException, HardwareMouseError):
            self.disconnect()
            raise

    def disconnect(self) -> None:
        if self.serial is not None:
            self.serial.close()
        self.serial = None

    def _drain_startup(self) -> None:
        if self.serial is None:
            return
        while self.serial.in_waiting:
            self.serial.readline()

    def _readline(self) -> Optional[str]:
        if self.serial is None:
            raise HardwareMouseError("Simple Arduino mouse is not connected")
        line = self.serial.readline().decode("utf-8", errors="replace").strip()
        return line or None

    def _send(self, command: str) -> Optional[str]:
        if self.serial is None:
            raise HardwareMouseError("Simple Arduino mouse is not connected")
        self.serial.write((command + "\n").encode("utf-8"))
        response = self._readline()
        if response is not None and response != "OK":
            acknowledgment = self._readline()
            if acknowledgment != "OK":
                return None
        return response

    def move_relative(self, dx: int, dy: int) -> bool:
        return self._send(f"M,{int(dx)},{int(dy)}") == "OK"

    def click(self) -> bool:
        return self._send("C") == "OK"

    def mouse_down(self) -> bool:
        return self._send("D") == "OK"

    def mouse_up(self) -> bool:
        return self._send("U") == "OK"

    def version(self) -> Optional[str]:
        response = self._send("V")
        return response.split(":", 1)[1] if response and response.startswith("VERSION:") else None


def _confirm_input(confirm_input: bool) -> bool:
    if confirm_input:
        return True
    if not sys.stdin.isatty():
        print("Input test skipped. Re-run with --confirm-input to allow mouse movement/clicks.")
        return False
    answer = input("This test moves and clicks the physical mouse. Continue? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def run_simple_connection(port: Optional[str], baudrate: int) -> int:
    selected = _select_port(port)
    if not selected:
        print("Arduino/ESP32 serial port was not found.")
        return 1
    mouse = SimpleArduinoMouse(baudrate=baudrate)
    try:
        if not mouse.connect(selected):
            print(f"Handshake failed on {selected}.")
            return 1
        print(f"Connected to {selected}; firmware={mouse.version() or 'unknown'}")
        return 0
    except (serial.SerialException, HardwareMouseError) as exc:
        print(f"Connection failed: {exc}")
        return 1
    finally:
        mouse.disconnect()


def run_complete_test(port: Optional[str], baudrate: int, confirm_input: bool) -> int:
    if not _confirm_input(confirm_input):
        return 0
    selected = _select_port(port)
    if not selected:
        print("Arduino/ESP32 serial port was not found.")
        return 1
    mouse = SimpleArduinoMouse(baudrate=baudrate)
    try:
        if not mouse.connect(selected):
            print(f"Handshake failed on {selected}.")
            return 1
        for dx, dy in ((100, 0), (0, 100), (-100, 0), (0, -100)):
            if not mouse.move_relative(dx, dy):
                return 1
            time.sleep(0.1)
        if not mouse.click() or not mouse.mouse_down():
            return 1
        time.sleep(0.5)
        if not mouse.mouse_up():
            return 1
        print("Connection, movement, click, and hold/release tests passed.")
        return 0
    except (serial.SerialException, HardwareMouseError) as exc:
        print(f"Complete test failed: {exc}")
        return 1
    finally:
        if mouse.serial is not None:
            try:
                mouse.mouse_up()
            except (serial.SerialException, HardwareMouseError):
                pass
        mouse.disconnect()


def run_real_hardware_mouse(port: Optional[str], baudrate: int) -> int:
    selected = _select_port(port)
    if not selected:
        print("Arduino/ESP32 serial port was not found.")
        return 1
    config = HardwareMouseConfig(port=selected, baudrate=baudrate)
    mouse = HardwareMouse(config)
    try:
        mouse.connect()
        print(f"Connected: {mouse}")
        print(f"Version: {mouse.device_version}")
        print(f"Status: {mouse.get_status() or 'unavailable'}")
        return 0
    except (serial.SerialException, HardwareMouseError) as exc:
        print(f"HardwareMouse test failed: {exc}")
        return 1
    finally:
        mouse.disconnect()


def connect_with_retry(
    port: str,
    baudrate: int = 115200,
    attempts: int = 3,
    initial_delay_s: float = 0.5,
    mouse_factory: Callable[..., HardwareMouse] = HardwareMouse,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> HardwareMouse:
    """Connect with bounded exponential backoff and deterministic cleanup."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    last_error: Optional[Exception] = None
    delay = initial_delay_s
    for attempt in range(1, attempts + 1):
        mouse = None
        try:
            mouse = mouse_factory(HardwareMouseConfig(port=port, baudrate=baudrate))
            mouse.connect()
            return mouse
        except Exception as exc:
            last_error = exc
            if mouse is not None:
                mouse.disconnect()
            if attempt < attempts:
                sleep_fn(delay)
                delay *= 2
    raise HardwareMouseError(f"Unable to connect to {port} after {attempts} attempts: {last_error}")


def run_retry_connection(port: Optional[str], baudrate: int) -> int:
    selected = _select_port(port)
    if not selected:
        print("Arduino/ESP32 serial port was not found.")
        return 1
    mouse = None
    try:
        mouse = connect_with_retry(selected, baudrate=baudrate)
        print(f"Connected after retry-capable handshake: {mouse}")
        return 0
    except (serial.SerialException, HardwareMouseError) as exc:
        print(f"Retry connection failed: {exc}")
        return 1
    finally:
        if mouse is not None:
            mouse.disconnect()


def run_example(
    example: int,
    port: Optional[str] = None,
    baudrate: int = 115200,
    confirm_input: bool = False,
) -> int:
    print(f"Running Arduino example {example}")
    if example == 1:
        return inspect_ports()
    if example == 2:
        return inspect_device_identity(port)
    if example == 3:
        return run_simple_connection(port, baudrate)
    if example == 4:
        return run_complete_test(port, baudrate, confirm_input)
    if example == 5:
        return run_real_hardware_mouse(port, baudrate)
    if example == 6:
        return run_retry_connection(port, baudrate)
    raise ValueError(f"Unsupported Arduino example: {example}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Arduino/ESP32 serial examples")
    parser.add_argument("--example", type=int, choices=range(1, 7), required=True)
    parser.add_argument("--port")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--confirm-input", action="store_true")
    return parser


if __name__ == "__main__":
    cli = _build_parser().parse_args()
    raise SystemExit(run_example(cli.example, cli.port, cli.baudrate, cli.confirm_input))
