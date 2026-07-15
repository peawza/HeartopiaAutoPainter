import serial
import time

print("Opening COM6...")
ser = serial.Serial('COM6', 115200, timeout=2)
print("Connected!")

print("Waiting for Arduino to reset...")
time.sleep(2)

print("\nReading startup messages:")
while ser.in_waiting > 0:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(f"  {line}")

print("\nSending PING (P command)...")
ser.write(b'P\n')
time.sleep(0.2)

print("Response:")
while ser.in_waiting > 0:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(f"  {line}")

ser.close()
print("\nDone!")
