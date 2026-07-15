import argparse
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Heartopia Painter launcher")
    parser.add_argument(
        "--arduino-example",
        type=int,
        choices=range(1, 7),
        help="run an Arduino connection example (1-6) without starting the GUI",
    )
    parser.add_argument("--port", help="serial port for an Arduino example, e.g. COM6")
    parser.add_argument("--baudrate", type=int, default=115200, help="serial baud rate")
    parser.add_argument(
        "--confirm-input",
        action="store_true",
        help="allow examples that move or click the physical mouse",
    )
    return parser


def _run_gui() -> None:
    try:
        from heartopia_painter.app import run
    except ModuleNotFoundError as e:
        missing = getattr(e, "name", None)
        if missing in {"PySide6", "pillow", "PIL", "mss", "pynput", "pyautogui"} or (
            isinstance(missing, str) and missing.startswith("PySide6")
        ):
            sys.stderr.write(
                "ขาด Python dependencies\n\n"
                "โดยทั่วไปหมายถึงคุณกำลังรันด้วย Python interpreter ที่ผิด (ไม่ใช่ venv ของโปรเจค)\n\n"
                "แก้ไข:\n"
                "  1) เปิดใช้งาน venv: .\\.venv\\Scripts\\Activate.ps1\n"
                "  2) ติดตั้ง deps:     python -m pip install -r requirements.txt\n"
                "  3) รัน:              python main.py\n\n"
                "หรือรันโดยตรงด้วย venv python:\n"
                "  .\\.venv\\Scripts\\python.exe main.py\n\n"
                "https://beer-studio.com"
            )
            raise SystemExit(1)
        raise

    run()


def main(argv=None) -> int:
    parser = _build_parser()
    args, extra = parser.parse_known_args(argv)

    if args.arduino_example is None:
        _run_gui()
        return 0

    if extra:
        parser.error(f"unrecognized arguments for Arduino example: {' '.join(extra)}")

    from example_arduino_connection import run_example

    return run_example(
        args.arduino_example,
        port=args.port,
        baudrate=args.baudrate,
        confirm_input=args.confirm_input,
    )


if __name__ == "__main__":
    raise SystemExit(main())
