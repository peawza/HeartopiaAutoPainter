#!/usr/bin/env python3
"""
Test UI config loading - check what gets loaded into UI
"""

import json
from pathlib import Path

def main():
    # Load config.json
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("=" * 60)
        print("config.json contents:")
        print("=" * 60)
        
        # Enhanced timing settings
        print("\n[Enhanced Timing Settings]")
        print(f"  use_advanced_delays: {config.get('use_advanced_delays', 'NOT FOUND')}")
        print(f"  use_hardware_mouse: {config.get('use_hardware_mouse', 'NOT FOUND')}")
        print(f"  hardware_mouse_port: {config.get('hardware_mouse_port', 'NOT FOUND')}")
        print(f"  delay_profile: {config.get('delay_profile', 'NOT FOUND')}")
        print(f"  enable_position_jitter: {config.get('enable_position_jitter', 'NOT FOUND')}")
        print(f"  enable_micro_pauses: {config.get('enable_micro_pauses', 'NOT FOUND')}")
    else:
        print("❌ config.json NOT FOUND!")
    
    # Load mouse_config.json
    mouse_config_path = Path("mouse_config.json")
    if mouse_config_path.exists():
        with open(mouse_config_path, 'r', encoding='utf-8') as f:
            mouse_config = json.load(f)
        print("\n" + "=" * 60)
        print("mouse_config.json contents:")
        print("=" * 60)
        
        # Human-like behavior settings
        print("\n[Human-Like Behavior Settings]")
        print(f"  arduino_port: {mouse_config.get('arduino_port', 'NOT FOUND')}")
        print(f"  click_randomness_px: {mouse_config.get('click_randomness_px', 'NOT FOUND')}")
        print(f"  enable_micro_pause: {mouse_config.get('enable_micro_pause', 'NOT FOUND')}")
        print(f"  enable_fatigue: {mouse_config.get('enable_fatigue', 'NOT FOUND')}")
        print(f"  enable_breaks: {mouse_config.get('enable_breaks', 'NOT FOUND')}")
        print(f"  enable_mistakes: {mouse_config.get('enable_mistakes', 'NOT FOUND')}")
    else:
        print("\n❌ mouse_config.json NOT FOUND!")
    
    print("\n" + "=" * 60)
    print("What SHOULD be loaded in UI:")
    print("=" * 60)
    print("\n[checkboxes that should be checked]:")
    if config_path.exists():
        print(f"  ☐ Enhanced Timing: {config.get('use_advanced_delays', False)}")
        print(f"  ☐ Hardware Mouse: {config.get('use_hardware_mouse', False)}")
        print(f"  ☐ Position Jitter: {config.get('enable_position_jitter', True)}")
        print(f"  ☐ Micro Pauses: {config.get('enable_micro_pauses', True)}")
    
    if mouse_config_path.exists():
        print(f"  ☐ Fatigue: {mouse_config.get('enable_fatigue', True)}")
        print(f"  ☐ Breaks: {mouse_config.get('enable_breaks', True)}")
        print(f"  ☐ Mistakes: {mouse_config.get('enable_mistakes', True)}")
    
    print("\n[ComboBox/TextBox values]:")
    if config_path.exists():
        print(f"  Profile: {config.get('delay_profile', 'default')}")
        print(f"  Port: {config.get('hardware_mouse_port', mouse_config.get('arduino_port', 'NOT SET'))}")

if __name__ == "__main__":
    main()
