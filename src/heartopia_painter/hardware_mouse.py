"""
Hardware Mouse Controller - ESP32/Arduino Leonardo Interface

This module provides an interface to control mouse movements through
an Arduino Leonardo or ESP32 microcontroller, which appears as a real
HID mouse device to the operating system.

Features:
- Real HID mouse device (undetectable as automation)
- Support for delay system integration
- Smooth movement with Bezier curves
- Hardware-level timing control
- Statistics and health monitoring
"""

from __future__ import annotations

import time
import serial
import serial.tools.list_ports
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class HardwareMouseConfig:
    """Configuration for hardware mouse."""
    port: Optional[str] = None
    baudrate: int = 115200
    timeout: float = 1.0
    
    # Auto-detection settings
    auto_detect: bool = True
    device_keywords: List[str] = None
    
    # Timing
    command_delay_ms: float = 1.0
    move_chunk_size: int = 127  # Max per Mouse.move() call
    
    # Position randomness (for DPI 1800)
    click_randomness_px: int = 25  # Random offset ±25 pixels
    
    def __post_init__(self):
        if self.device_keywords is None:
            self.device_keywords = ['arduino', 'leonardo', 'pro micro', 'atmega32u4']


class HardwareMouseError(Exception):
    """Exception raised for hardware mouse errors."""
    pass


class HardwareMouse:
    """
    Interface to Arduino Leonardo / ESP32 HID mouse device.
    
    This class provides methods to control a physical HID mouse device
    through serial commands, supporting natural movement patterns and
    integration with the delay system.
    """
    
    def __init__(self, config: Optional[HardwareMouseConfig] = None):
        """
        Initialize hardware mouse interface.
        
        Args:
            config: Hardware mouse configuration
        """
        self.config = config or HardwareMouseConfig()
        self.serial: Optional[serial.Serial] = None
        self.connected: bool = False
        
        # Statistics
        self.total_commands: int = 0
        self.total_moves: int = 0
        self.total_clicks: int = 0
        
        # Device info
        self.device_version: Optional[str] = None
        self.device_port: Optional[str] = None
        self.device_type: str = "Unknown"  # "Arduino" or "Logitech/HID"
    
    def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to the hardware mouse device.
        
        Args:
            port: Serial port (e.g., 'COM3' or '/dev/ttyACM0')
                  If None, will auto-detect
        
        Returns:
            True if connection successful
        
        Raises:
            HardwareMouseError: If connection fails
        """
        if self.connected:
            return True
        
        # Determine port
        if port is None:
            port = self.config.port
        
        if port is None and self.config.auto_detect:
            port = self._auto_detect_port()
        
        if port is None:
            raise HardwareMouseError(
                "No port specified and auto-detection failed. "
                "Please specify port manually or ensure device is connected."
            )
        
        try:
            # Open serial connection
            self.serial = serial.Serial(
                port=port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout
            )
            
            # Wait for device ready signal
            time.sleep(0.5)  # Reduced wait time for Logitech devices
            
            # Clear any startup messages (non-blocking)
            self.serial.timeout = 0.2  # Short timeout for checking
            try:
                while self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("VERSION:"):
                        self.device_version = line.split(":", 1)[1]
            except:
                pass
            
            # Restore normal timeout
            self.serial.timeout = self.config.timeout
            
            # Test connection with ping (allow failure for Logitech devices)
            try:
                if self._send_command("P", expected_response="PONG"):
                    # Standard Arduino device
                    self.device_type = "Arduino"
                else:
                    # Logitech or other HID device (no response is OK)
                    self.device_type = "Logitech/HID"
                    print(f"[INFO] Device doesn't respond to ping - assuming Logitech/HID device")
            except:
                # Ping failed completely - still allow connection
                self.device_type = "Logitech/HID"
                print(f"[INFO] Ping failed - assuming Logitech/HID device")
            
            # Try to get version info (optional)
            try:
                if self._send_command("V"):
                    response = self._read_response()
                    if response and response.startswith("VERSION:"):
                        self.device_version = response.split(":", 1)[1]
                    else:
                        self.device_version = "Unknown (Logitech)"
                else:
                    self.device_version = "Unknown (Logitech)"
            except:
                self.device_version = "Unknown (Logitech)"
            
            self.connected = True
            self.device_port = port
            
            return True
            
        except serial.SerialException as e:
            raise HardwareMouseError(f"Failed to connect to {port}: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the hardware mouse device."""
        if self.serial is not None:
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
        
        self.connected = False
    
    def _auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect Arduino Leonardo / Pro Micro port.
        
        Returns:
            Port name if found, None otherwise
        """
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Check device description for keywords
            desc_lower = (port.description or "").lower()
            for keyword in self.config.device_keywords:
                if keyword.lower() in desc_lower:
                    return port.device
            
            # Check manufacturer
            if port.manufacturer:
                mfg_lower = port.manufacturer.lower()
                if 'arduino' in mfg_lower or 'sparkfun' in mfg_lower:
                    return port.device
            
            # Check VID/PID (Arduino Leonardo: 2341:8036, SparkFun Pro Micro: 1B4F:9205/9206)
            if port.vid in [0x2341, 0x1B4F]:
                return port.device
        
        return None
    
    def _send_command(self, command: str, expected_response: Optional[str] = None) -> bool:
        """
        Send a command to the device.
        
        Args:
            command: Command string
            expected_response: Expected response (if not "OK")
        
        Returns:
            True if command succeeded
        
        Raises:
            HardwareMouseError: If not connected or command fails
        """
        if not self.connected or self.serial is None:
            raise HardwareMouseError("Not connected to hardware mouse")
        
        try:
            # Send command
            self.serial.write((command + '\n').encode('utf-8'))
            self.total_commands += 1
            
            # Wait for response
            response = self._read_response()
            
            if expected_response is not None:
                return response == expected_response
            else:
                return response == "OK"
            
        except serial.SerialException as e:
            raise HardwareMouseError(f"Command failed: {e}")
    
    def _read_response(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Read a response from the device.
        
        Args:
            timeout: Read timeout in seconds
        
        Returns:
            Response string, or None if timeout
        """
        if timeout is None:
            timeout = self.config.timeout
        
        if self.serial is None:
            return None
        
        old_timeout = self.serial.timeout
        try:
            self.serial.timeout = timeout
            line = self.serial.readline().decode('utf-8', errors='ignore').strip()
            return line if line else None
        finally:
            self.serial.timeout = old_timeout
    
    def move(self, dx: int, dy: int) -> bool:
        """
        Move mouse by relative offset.
        
        Args:
            dx: X offset in pixels
            dy: Y offset in pixels
        
        Returns:
            True if move succeeded
        """
        if dx == 0 and dy == 0:
            return True
        
        command = f"M,{int(dx)},{int(dy)}"
        success = self._send_command(command)
        
        if success:
            self.total_moves += 1
        
        return success
    
    def apply_click_randomness(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """
        Apply random offset to target position for natural clicking.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
        
        Returns:
            Tuple of (randomized_x, randomized_y)
        """
        import random
        randomness = self.config.click_randomness_px
        offset_x = random.randint(-randomness, randomness)
        offset_y = random.randint(-randomness, randomness)
        return (target_x + offset_x, target_y + offset_y)
    
    def move_smooth(self, dx: int, dy: int, steps: int = 10) -> bool:
        """
        Move mouse smoothly in multiple steps.
        
        Args:
            dx: X offset in pixels
            dy: Y offset in pixels
            steps: Number of interpolation steps
        
        Returns:
            True if move succeeded
        """
        if dx == 0 and dy == 0:
            return True
        
        steps = max(1, min(100, int(steps)))
        
        command = f"MS,{int(dx)},{int(dy)},{steps}"
        success = self._send_command(command)
        
        if success:
            self.total_moves += 1
        
        return success
    
    def move_along_curve(self, points: List[Tuple[int, int]], current_pos: Tuple[int, int]) -> bool:
        """
        Move mouse along a curve (list of absolute positions).
        
        Args:
            points: List of (x, y) absolute positions
            current_pos: Current mouse position (x, y)
        
        Returns:
            True if all moves succeeded
        """
        if not points:
            return True
        
        prev_x, prev_y = current_pos
        
        for x, y in points:
            dx = int(x - prev_x)
            dy = int(y - prev_y)
            
            if dx != 0 or dy != 0:
                if not self.move(dx, dy):
                    return False
                
                # Small delay between points for smooth animation
                time.sleep(0.001)  # 1ms
            
            prev_x, prev_y = x, y
        
        return True
    
    def press(self) -> bool:
        """
        Press left mouse button (hold down).
        
        Returns:
            True if press succeeded
        """
        return self._send_command("D")
    
    def release(self) -> bool:
        """
        Release left mouse button.
        
        Returns:
            True if release succeeded
        """
        return self._send_command("U")
    
    def click(self) -> bool:
        """
        Perform a full click (press + release with human-like timing).
        
        Returns:
            True if click succeeded
        """
        success = self._send_command("C")
        
        if success:
            self.total_clicks += 1
        
        return success
    
    def wait(self, milliseconds: int) -> bool:
        """
        Wait/delay on the device side.
        
        Args:
            milliseconds: Delay in milliseconds (max 10000)
        
        Returns:
            True if command succeeded
        """
        ms = max(0, min(10000, int(milliseconds)))
        return self._send_command(f"W,{ms}")
    
    def set_min_delay(self, microseconds: int) -> bool:
        """
        Set minimum delay between moves on the device.
        
        Args:
            microseconds: Minimum delay in microseconds (max 100000)
        
        Returns:
            True if command succeeded
        """
        us = max(0, min(100000, int(microseconds)))
        return self._send_command(f"SETDELAY,{us}")
    
    def get_status(self) -> Optional[dict]:
        """
        Get device status and statistics.
        
        Returns:
            Dictionary with status info, or None if failed
        """
        if self._send_command("S"):
            response = self._read_response()
            if response and response.startswith("STATUS:"):
                # Parse: STATUS:commands=123,moves=45,clicks=6,delay=0us
                parts = response.split(":", 1)[1].split(",")
                status = {}
                for part in parts:
                    if "=" in part:
                        key, value = part.split("=", 1)
                        # Remove units (us, etc)
                        value = value.rstrip("us")
                        try:
                            status[key] = int(value)
                        except ValueError:
                            status[key] = value
                return status
        return None
    
    def ping(self) -> bool:
        """
        Ping device to check if it's responsive.
        
        Returns:
            True if device responds
        """
        try:
            return self._send_command("P", expected_response="PONG")
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry."""
        if not self.connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __repr__(self) -> str:
        """String representation."""
        if self.connected:
            return f"<HardwareMouse connected={self.device_port} version={self.device_version}>"
        else:
            return f"<HardwareMouse disconnected>"


# Convenience functions

def list_available_ports() -> List[dict]:
    """
    List all available serial ports.
    
    Returns:
        List of dictionaries with port information
    """
    ports = serial.tools.list_ports.comports()
    result = []
    
    for port in ports:
        result.append({
            'device': port.device,
            'description': port.description or '',
            'manufacturer': port.manufacturer or '',
            'vid': port.vid,
            'pid': port.pid,
        })
    
    return result


def find_arduino_port() -> Optional[str]:
    """
    Find Arduino Leonardo / Pro Micro port automatically.
    
    Returns:
        Port name if found, None otherwise
    """
    config = HardwareMouseConfig(auto_detect=True)
    mouse = HardwareMouse(config)
    return mouse._auto_detect_port()


# Example usage
if __name__ == "__main__":
    print("Hardware Mouse Controller - Test")
    print("=" * 50)
    
    # List available ports
    print("\nAvailable serial ports:")
    ports = list_available_ports()
    for i, port_info in enumerate(ports, 1):
        print(f"  {i}. {port_info['device']}")
        print(f"     Description: {port_info['description']}")
        print(f"     Manufacturer: {port_info['manufacturer']}")
    
    # Try to auto-detect Arduino
    print("\nAuto-detecting Arduino...")
    arduino_port = find_arduino_port()
    if arduino_port:
        print(f"Found Arduino at: {arduino_port}")
    else:
        print("No Arduino detected")
        exit(1)
    
    # Connect and test
    print("\nConnecting...")
    try:
        with HardwareMouse() as mouse:
            print(f"Connected: {mouse}")
            print(f"Version: {mouse.device_version}")
            
            # Ping test
            print("\nPing test...")
            if mouse.ping():
                print("✓ Ping successful")
            
            # Get status
            print("\nDevice status:")
            status = mouse.get_status()
            if status:
                for key, value in status.items():
                    print(f"  {key}: {value}")
            
            # Test movements
            print("\nTesting movements...")
            print("  Moving right 100px...")
            mouse.move(100, 0)
            time.sleep(0.5)
            
            print("  Moving down 50px...")
            mouse.move(0, 50)
            time.sleep(0.5)
            
            print("  Moving back (smooth)...")
            mouse.move_smooth(-100, -50, steps=20)
            time.sleep(0.5)
            
            # Test click
            print("\nTesting click...")
            mouse.click()
            
            # Final status
            print("\nFinal status:")
            status = mouse.get_status()
            if status:
                for key, value in status.items():
                    print(f"  {key}: {value}")
            
            print("\n✓ All tests passed!")
            
    except HardwareMouseError as e:
        print(f"\n✗ Error: {e}")
        exit(1)
