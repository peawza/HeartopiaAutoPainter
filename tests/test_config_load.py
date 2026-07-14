"""Test config loading to debug checkbox issue."""
import sys
sys.path.insert(0, 'src')

from heartopia_painter.config import load_mouse_config, load_config, default_config_path

print("=" * 60)
print("Testing Config Loading")
print("=" * 60)

# Test mouse_config.json
print("\n1. Loading mouse_config.json...")
try:
    mouse_config = load_mouse_config()
    
    print(f"   ✓ Loaded successfully")
    print(f"   enable_fatigue: {mouse_config.enable_fatigue}")
    print(f"   enable_breaks: {mouse_config.enable_breaks}")
    print(f"   enable_mistakes: {mouse_config.enable_mistakes}")
    print(f"   arduino_port: {mouse_config.arduino_port}")
    
    # Test attribute access (like in app.py)
    enable_fatigue = getattr(mouse_config, 'enable_fatigue', True)
    enable_breaks = getattr(mouse_config, 'enable_breaks', True)
    enable_mistakes = getattr(mouse_config, 'enable_mistakes', True)
    
    print(f"\n   Using getattr():")
    print(f"   enable_fatigue: {enable_fatigue}")
    print(f"   enable_breaks: {enable_breaks}")
    print(f"   enable_mistakes: {enable_mistakes}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test config.json
print("\n2. Loading config.json...")
try:
    config_path = default_config_path()
    cfg = load_config(config_path)
    
    print(f"   ✓ Loaded successfully")
    print(f"   use_advanced_delays: {cfg.use_advanced_delays}")
    print(f"   use_hardware_mouse: {cfg.use_hardware_mouse}")
    print(f"   hardware_mouse_port: {cfg.hardware_mouse_port}")
    print(f"   delay_profile: {cfg.delay_profile}")
    print(f"   enable_position_jitter: {cfg.enable_position_jitter}")
    print(f"   enable_micro_pauses: {cfg.enable_micro_pauses}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
