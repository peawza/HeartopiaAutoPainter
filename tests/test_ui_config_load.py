"""Test script to verify mouse_config.json loading in UI"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from heartopia_painter.config import load_mouse_config, default_mouse_config_path

print("=" * 60)
print("Test: mouse_config.json Loading")
print("=" * 60)

# Check file exists
config_path = default_mouse_config_path()
print(f"\n1. Config file path: {config_path}")
print(f"   Exists: {config_path.exists()}")

if not config_path.exists():
    print(f"   ❌ File not found!")
    sys.exit(1)

# Load config
print(f"\n2. Loading mouse_config.json...")
try:
    mouse_config = load_mouse_config()
    print(f"   ✓ Loaded successfully")
    
    # Print all relevant fields
    print(f"\n3. Configuration values:")
    print(f"   - arduino_port: {getattr(mouse_config, 'arduino_port', None)}")
    print(f"   - enable_micro_pause: {getattr(mouse_config, 'enable_micro_pause', None)}")
    print(f"   - enable_fatigue: {getattr(mouse_config, 'enable_fatigue', None)}")
    print(f"   - enable_breaks: {getattr(mouse_config, 'enable_breaks', None)}")
    print(f"   - enable_mistakes: {getattr(mouse_config, 'enable_mistakes', None)}")
    print(f"   - click_randomness_px: {getattr(mouse_config, 'click_randomness_px', None)}")
    
    # Check if UI would load correctly
    print(f"\n4. UI checkbox states (what would be loaded):")
    
    enable_position_jitter = getattr(mouse_config, 'click_randomness_px', 3) > 0
    print(f"   - Position Jitter: {enable_position_jitter}")
    print(f"   - Micro Pauses: {getattr(mouse_config, 'enable_micro_pause', True)}")
    print(f"   - Fatigue: {getattr(mouse_config, 'enable_fatigue', True)}")
    print(f"   - Breaks: {getattr(mouse_config, 'enable_breaks', True)}")
    print(f"   - Mistakes: {getattr(mouse_config, 'enable_mistakes', True)}")
    
    print(f"\n✅ All tests passed!")
    
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
