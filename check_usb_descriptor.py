#!/usr/bin/env python3
"""Read-only check for the Arduino serial interface USB descriptor."""

import sys

import serial.tools.list_ports


LOGITECH_VID = 0x046D
LOGITECH_PID = 0xC07D


def main() -> int:
    print("=" * 60)
    print("Arduino USB Descriptor Check")
    print("=" * 60)

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return 1

    found_logitech = False
    print("\nSerial devices found:\n" + "-" * 60)
    for port in ports:
        vid = getattr(port, "vid", None)
        pid = getattr(port, "pid", None)
        vid_text = f"{vid:04X}" if vid is not None else "????"
        pid_text = f"{pid:04X}" if pid is not None else "????"
        is_logitech = vid == LOGITECH_VID and pid == LOGITECH_PID
        found_logitech = found_logitech or is_logitech
        status = "LOGITECH DESCRIPTOR DETECTED" if is_logitech else ""
        print(f"{port.device}: {port.description or 'Unknown'}")
        print(f"  VID:PID = {vid_text}:{pid_text}  {status}")
        if port.manufacturer:
            print(f"  Manufacturer: {port.manufacturer}")

    print("\nSummary")
    if found_logitech:
        print("OK: VID 046D and PID C07D detected on a serial port.")
        print("The descriptor check passed; the firmware handshake is a separate step.")
        return 0

    print("Logitech VID/PID 046D:C07D was not detected.")
    print("If this is an unmodified Leonardo, its default is usually 2341:8036.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
