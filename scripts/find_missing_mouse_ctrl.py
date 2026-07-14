#!/usr/bin/env python3
"""
Script to find _tap() and _select_shade() calls that are missing mouse_controller parameter.
This helps complete Step 9 of integration.
"""

import re
from pathlib import Path

def find_missing_param():
    paint_py = Path("src/heartopia_painter/paint.py")
    
    if not paint_py.exists():
        print(f"❌ File not found: {paint_py}")
        return
    
    content = paint_py.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Patterns to find calls without mouse_controller parameter
    tap_pattern = r'_tap\([^)]+\)(?!.*mouse_controller)'
    select_shade_pattern = r'_select_shade\([^)]+\)(?!.*mouse_controller)'
    
    print("=" * 80)
    print("🔍 Finding _tap() calls WITHOUT mouse_controller parameter")
    print("=" * 80)
    
    tap_count = 0
    for i, line in enumerate(lines, start=1):
        # Skip function definitions
        if 'def _tap(' in line:
            continue
        
        # Find _tap() calls
        if '_tap(' in line and 'mouse_controller' not in line:
            tap_count += 1
            context_start = max(0, i-2)
            context_end = min(len(lines), i+2)
            print(f"\n📍 Line {i}:")
            for j in range(context_start, context_end):
                marker = ">>> " if j == i-1 else "    "
                print(f"{marker}{j+1:4d} | {lines[j]}")
    
    print("\n" + "=" * 80)
    print(f"🔍 Finding _select_shade() calls WITHOUT mouse_controller parameter")
    print("=" * 80)
    
    select_count = 0
    for i, line in enumerate(lines, start=1):
        # Skip function definitions
        if 'def _select_shade(' in line:
            continue
        
        # Find _select_shade() calls
        if '_select_shade(' in line and 'mouse_controller' not in line:
            select_count += 1
            context_start = max(0, i-2)
            context_end = min(len(lines), i+2)
            print(f"\n📍 Line {i}:")
            for j in range(context_start, context_end):
                marker = ">>> " if j == i-1 else "    "
                print(f"{marker}{j+1:4d} | {lines[j]}")
    
    print("\n" + "=" * 80)
    print(f"📊 Summary")
    print("=" * 80)
    print(f"_tap() calls missing mouse_controller: {tap_count}")
    print(f"_select_shade() calls missing mouse_controller: {select_count}")
    print(f"Total to fix: {tap_count + select_count}")
    print("=" * 80)

if __name__ == "__main__":
    find_missing_param()
