#!/usr/bin/env python3
"""Simple test for COM6"""

import serial
import time

print("Opening COM6...")
try:
    ser = serial.Serial('COM6', 115200, timeout=1)
    print("OK - Port opened")
    
    print("Waiting 1 sec...")
    time.sleep(1)
    
    print("Checking for data...")
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print(f"Got data: {data}")
    else:
        print("No data")
    
    print("Sending 'P\\n'...")
    ser.write(b'P\n')
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response: {response}")
    else:
        print("No response")
    
    ser.close()
    print("Done")
    
except Exception as e:
    print(f"Error: {e}")
