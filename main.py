import argparse
import sys
from pathlib import Path
from typing import Optional

# ============================================
# 🔒 Anti-Detection Layer (Initialize FIRST)
# ============================================
try:
    from anti_detection import init_stealth
    # Run anti-detection checks before anything else
    init_stealth()
except Exception:
    # If anti-detection fails, continue anyway
    pass


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
        "--hardware-click",
        action="store_true",
        help="use the connected Arduino/ESP device for clicks while software controls cursor movement",
    )
    parser.add_argument(
        "--humanized",
        action="store_true",
        help="enable the existing human-like timing system for this session",
    )
    parser.add_argument(
        "--human-profile",
        choices=("fast", "default", "careful"),
        help="override the human-like timing profile for this session",
    )
    parser.add_argument(
        "--position-jitter",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable or disable position jitter for this session",
    )
    parser.add_argument(
        "--micro-pauses",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable or disable micro-pauses for this session",
    )
    parser.add_argument(
        "--safety-report",
        action="store_true",
        help="print a local safety/effectiveness report without starting the GUI",
    )
    parser.add_argument(
        "--safety-report-json",
        action="store_true",
        help="print a structured local safety/effectiveness report without starting the GUI",
    )
    parser.add_argument(
        "--strict-safety",
        action="store_true",
        help="return exit code 1 when a safety report contains FAIL findings",
    )
    parser.add_argument(
        "--confirm-input",
        action="store_true",
        help="allow examples that move or click the physical mouse",
    )
    return parser


def _run_gui(
    hardware_click: bool = False,
    port: Optional[str] = None,
    baudrate: int = 115200,
    humanized: Optional[bool] = None,
    human_profile: Optional[str] = None,
    position_jitter: Optional[bool] = None,
    micro_pauses: Optional[bool] = None,
) -> None:
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

    run(
        hardware_click=hardware_click,
        hardware_port=port,
        hardware_baudrate=baudrate,
        humanized=humanized,
        human_profile=human_profile,
        position_jitter=position_jitter,
        micro_pauses=micro_pauses,
    )


def main(argv=None) -> int:
    parser = _build_parser()
    args, extra = parser.parse_known_args(argv)

    if args.safety_report or args.safety_report_json:
        if extra:
            parser.error(f"unrecognized arguments for safety report: {' '.join(extra)}")
        from heartopia_painter.safety_report import build_safety_report, render_safety_report, render_safety_report_json

        print(render_safety_report_json() if args.safety_report_json else render_safety_report())
        report = build_safety_report()
        return 1 if args.strict_safety and report.has_failures else 0

    if args.arduino_example is None:
        if extra:
            parser.error(f"unrecognized arguments: {' '.join(extra)}")
        _run_gui(
            hardware_click=args.hardware_click,
            port=args.port,
            baudrate=args.baudrate,
            humanized=True if args.humanized else None,
            human_profile=args.human_profile,
            position_jitter=args.position_jitter,
            micro_pauses=args.micro_pauses,
        )
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
