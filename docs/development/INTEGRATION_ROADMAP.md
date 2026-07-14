# Integration Roadmap - Delay System + Hardware Mouse

## 📋 Overview

This document provides a step-by-step guide to integrate the delay system and hardware mouse into the existing `paint.py` module.

---

## 🎯 Integration Goals

1. ✅ **Completed**: Delay system implementation
2. ✅ **Completed**: Hardware mouse driver
3. ✅ **Completed**: Enhanced paint module
4. ⏳ **Next**: Update paint.py to use enhanced features
5. ⏳ **Next**: Update app.py UI configuration
6. ⏳ **Optional**: Add GUI controls

---

## 📝 Step-by-Step Integration

### Phase 1: Minimal Integration (Recommended First Step)

#### Step 1.1: Add Configuration Flag

Update `src/heartopia_painter/config.py`:

```python
@dataclass
class AppConfig:
    # ... existing fields ...
    
    # Enhanced features
    use_enhanced_paint: bool = False
    use_hardware_mouse: bool = False
    hardware_mouse_port: Optional[str] = None
```

#### Step 1.2: Update paint.py Imports

Add to top of `src/heartopia_painter/paint.py`:

```python
# Enhanced paint support (optional)
try:
    from .enhanced_paint import MouseController, enhanced_tap, enhanced_stroke
    from .delays import DelaySystem, create_default_delay_system
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    MouseController = None
    enhanced_tap = None
    enhanced_stroke = None
```

#### Step 1.3: Create Mouse Controller in paint_grid()

Add at the start of `paint_grid()` function:

```python
def paint_grid(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    get_pixel: Callable[[int, int], RGB],
    options: Optional[PainterOptions] = None,
    # ... other parameters ...
) -> None:
    """Paints a WxH pixel grid into a canvas rectangle."""
    
    if options is None:
        options = PainterOptions()
    
    # Create enhanced mouse controller if enabled
    mouse_controller = None
    if ENHANCED_AVAILABLE and getattr(cfg, 'use_enhanced_paint', False):
        delay_system = create_default_delay_system()
        mouse_controller = MouseController(
            use_hardware=getattr(cfg, 'use_hardware_mouse', False),
            delay_system=delay_system
        )
    
    # ... rest of function ...
```

#### Step 1.4: Replace _tap() Calls (Gradual)

Replace existing `_tap()` calls with enhanced version when mouse_controller exists:

```python
# OLD CODE:
def _tap(pos: Point, opts: PainterOptions, extra_delay_s: float = 0.0):
    pyautogui.moveTo(pos[0], pos[1], duration=max(0.0, float(opts.move_duration_s)))
    pyautogui.mouseDown(button="left")
    time.sleep(max(0.0, float(opts.mouse_down_s)))
    pyautogui.mouseUp(button="left")
    time.sleep(max(0.0, float(opts.after_click_delay_s) + float(extra_delay_s)))

# NEW CODE:
def _tap(pos: Point, opts: PainterOptions, extra_delay_s: float = 0.0,
         mouse_ctrl: Optional[MouseController] = None):
    if mouse_ctrl is not None and ENHANCED_AVAILABLE:
        # Use enhanced tap with natural movement
        enhanced_tap(pos, mouse_ctrl)
        if extra_delay_s > 0:
            mouse_ctrl.delay_system.interruptible_sleep(extra_delay_s)
    else:
        # Original PyAutoGUI code
        pyautogui.moveTo(pos[0], pos[1], duration=max(0.0, float(opts.move_duration_s)))
        pyautogui.mouseDown(button="left")
        time.sleep(max(0.0, float(opts.mouse_down_s)))
        pyautogui.mouseUp(button="left")
        time.sleep(max(0.0, float(opts.after_click_delay_s) + float(extra_delay_s)))
```

---

### Phase 2: Full Integration

#### Step 2.1: Update All Movement Functions

Replace all mouse movement code with enhanced versions:

**Function: _cell_center()**
```python
def _cell_center(
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    x: int,
    y: int,
    apply_jitter: bool = False,
    delay_system: Optional[DelaySystem] = None
) -> Point:
    """Calculate cell center with optional jitter."""
    x0, y0, w, h = canvas_rect
    cell_w = w / grid_w
    cell_h = h / grid_h
    cx = int(x0 + (x + 0.5) * cell_w)
    cy = int(y0 + (y + 0.5) * cell_h)
    
    if apply_jitter and delay_system is not None:
        cx, cy = delay_system.apply_position_jitter(cx, cy)
    
    return (cx, cy)
```

**Function: _stroke() - Enhanced Version**
```python
def _stroke(
    points: List[Point],
    opts: PainterOptions,
    mouse_ctrl: Optional[MouseController] = None,
    should_stop: Optional[Callable[[], bool]] = None
) -> None:
    """Execute stroke with optional enhancement."""
    if mouse_ctrl is not None and ENHANCED_AVAILABLE:
        # Use enhanced stroke
        enhanced_stroke(points, mouse_ctrl, should_stop)
    else:
        # Original code
        if not points:
            return
        # ... original implementation ...
```

#### Step 2.2: Add Delay System to PainterOptions

Update `paint.py`:

```python
@dataclass
class PainterOptions:
    move_duration_s: float = 0.015
    mouse_down_s: float = 0.01
    after_click_delay_s: float = 0.03
    panel_open_delay_s: float = 0.06
    shade_select_delay_s: float = 0.03
    row_delay_s: float = 0.05

    enable_drag_strokes: bool = False
    drag_step_duration_s: float = 0.005
    after_drag_delay_s: float = 0.01
    
    # Enhanced features
    use_enhanced: bool = False
    delay_system: Optional[DelaySystem] = None
    mouse_controller: Optional[MouseController] = None
```

---

### Phase 3: GUI Integration (Optional)

#### Step 3.1: Add UI Tab in app.py

Add new tab for enhanced features:

```python
# In MainWindow._build_ui()

tab_enhanced = QtWidgets.QWidget()
tab_enhanced_layout = QtWidgets.QVBoxLayout(tab_enhanced)
tabs.addTab(tab_enhanced, "Enhanced Features")

# Enhanced features group
enhanced_group = QtWidgets.QGroupBox("Enhanced Paint & Hardware Mouse")
enhanced_layout = QtWidgets.QVBoxLayout(enhanced_group)

# Enable enhanced paint
self.chk_enhanced = QtWidgets.QCheckBox("Enable Enhanced Paint (Delay System)")
enhanced_layout.addWidget(self.chk_enhanced)

# Enable hardware mouse
self.chk_hardware = QtWidgets.QCheckBox("Enable Hardware Mouse (ESP32/Arduino)")
enhanced_layout.addWidget(self.chk_hardware)

# Hardware mouse port
row_port = QtWidgets.QHBoxLayout()
row_port.addWidget(QtWidgets.QLabel("Port:"))
self.txt_port = QtWidgets.QLineEdit()
self.txt_port.setPlaceholderText("Auto-detect (leave empty)")
row_port.addWidget(self.txt_port)
self.btn_test_hw = QtWidgets.QPushButton("Test Connection")
row_port.addWidget(self.btn_test_hw)
enhanced_layout.addWidget(row_port)

tab_enhanced_layout.addWidget(enhanced_group)
```

#### Step 3.2: Add Configuration Persistence

```python
# In _sync_timing_ui_from_cfg()
self.chk_enhanced.blockSignals(True)
self.chk_hardware.blockSignals(True)
self.txt_port.blockSignals(True)

self.chk_enhanced.setChecked(bool(getattr(self._cfg, "use_enhanced_paint", False)))
self.chk_hardware.setChecked(bool(getattr(self._cfg, "use_hardware_mouse", False)))
self.txt_port.setText(str(getattr(self._cfg, "hardware_mouse_port", "") or ""))

self.chk_enhanced.blockSignals(False)
self.chk_hardware.blockSignals(False)
self.txt_port.blockSignals(False)

# Connect signals
self.chk_enhanced.stateChanged.connect(lambda: self._on_enhanced_changed())
self.chk_hardware.stateChanged.connect(lambda: self._on_enhanced_changed())
self.txt_port.textChanged.connect(lambda: self._on_enhanced_changed())
self.btn_test_hw.clicked.connect(self._on_test_hardware)
```

#### Step 3.3: Add Test Hardware Button Handler

```python
def _on_test_hardware(self):
    """Test hardware mouse connection."""
    if not ENHANCED_AVAILABLE:
        QtWidgets.QMessageBox.warning(
            self,
            "Not Available",
            "Enhanced features not available. Check installation."
        )
        return
    
    port = self.txt_port.text().strip() or None
    
    try:
        from heartopia_painter.hardware_mouse import HardwareMouse, HardwareMouseConfig
        
        config = HardwareMouseConfig(port=port if port else None)
        mouse = HardwareMouse(config)
        mouse.connect()
        
        # Test ping
        if mouse.ping():
            QtWidgets.QMessageBox.information(
                self,
                "Connection Successful",
                f"Hardware mouse connected!\n\n"
                f"Port: {mouse.device_port}\n"
                f"Version: {mouse.device_version}\n\n"
                f"Test movements will now execute..."
            )
            
            # Test movement
            mouse.move(50, 0)
            time.sleep(0.5)
            mouse.move(-50, 0)
            
            QtWidgets.QMessageBox.information(
                self,
                "Test Complete",
                "Hardware mouse test completed successfully!"
            )
        
        mouse.disconnect()
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            self,
            "Connection Failed",
            f"Failed to connect to hardware mouse:\n\n{e}\n\n"
            f"Make sure:\n"
            f"1. Arduino is connected via USB\n"
            f"2. Firmware is uploaded\n"
            f"3. No other program is using the port"
        )
```

---

## 🧪 Testing Strategy

### Test 1: Basic Integration (No Hardware)

```python
# test_integration.py
from heartopia_painter.config import AppConfig
from heartopia_painter.enhanced_paint import MouseController
from heartopia_painter.delays import create_default_delay_system

# Create config
cfg = AppConfig()
cfg.use_enhanced_paint = True
cfg.use_hardware_mouse = False

# Create mouse controller
ds = create_default_delay_system()
mouse = MouseController(use_hardware=False, delay_system=ds)

# Test movement
print("Testing enhanced movement...")
current = mouse.get_current_position()
target = (current[0] + 100, current[1] + 50)
mouse.move_along_curve(current, target)
print("✓ Movement test passed")

# Test click
print("Testing enhanced click...")
mouse.click()
print("✓ Click test passed")
```

### Test 2: Hardware Mouse Integration

```python
# test_hardware_integration.py
from heartopia_painter.enhanced_paint import MouseController
from heartopia_painter.delays import create_default_delay_system

# Create mouse controller with hardware
ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

print(f"Hardware mouse: {mouse.hardware_mouse}")

# Test natural movement
print("Testing natural curved movement...")
current = mouse.get_current_position()
target = (current[0] + 200, current[1] + 100)
mouse.move_along_curve(current, target)
print("✓ Movement complete")

# Test click
print("Testing click...")
mouse.click()
print("✓ Click complete")

mouse.disconnect()
```

### Test 3: Full Paint Integration

```python
# test_paint_integration.py
from heartopia_painter.config import AppConfig
from heartopia_painter.paint import paint_grid, PainterOptions
from heartopia_painter.enhanced_paint import MouseController
from heartopia_painter.delays import create_default_delay_system

# Setup
cfg = AppConfig()
cfg.use_enhanced_paint = True
cfg.use_hardware_mouse = True  # Or False

canvas_rect = (100, 100, 300, 300)
grid_w, grid_h = 10, 10

def get_pixel(x, y):
    return (255, 0, 0)  # Red

# Create options with enhancement
ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

options = PainterOptions(
    use_enhanced=True,
    delay_system=ds,
    mouse_controller=mouse
)

# Paint (would need to update paint_grid to accept these options)
print("Starting enhanced paint test...")
# paint_grid(cfg, canvas_rect, grid_w, grid_h, get_pixel, options)
print("✓ Paint test complete")
```

---

## 📊 Migration Checklist

### Code Changes
- [ ] Update `config.py` - add enhanced feature flags
- [ ] Update `paint.py` - add enhanced imports
- [ ] Update `paint.py` - create MouseController
- [ ] Update `_tap()` - support enhanced mode
- [ ] Update `_stroke()` - support enhanced mode
- [ ] Update `PainterOptions` - add delay system fields
- [ ] Update `app.py` - add GUI controls (optional)
- [ ] Update `app.py` - add configuration sync

### Testing
- [ ] Test delay system alone
- [ ] Test hardware mouse alone
- [ ] Test enhanced paint without hardware
- [ ] Test enhanced paint with hardware
- [ ] Test full paint operation
- [ ] Test pause/resume with ESC
- [ ] Test all timing profiles

### Documentation
- [ ] Update README.md - mention enhanced features
- [ ] Create user guide for hardware setup
- [ ] Add troubleshooting section
- [ ] Document configuration options

---

## 🎯 Recommended Approach

### Week 1: Foundation
1. ✅ Implement delay system (DONE)
2. ✅ Implement hardware mouse driver (DONE)
3. ✅ Create enhanced_paint module (DONE)
4. ✅ Write documentation (DONE)

### Week 2: Integration
1. Add configuration flags to config.py
2. Update paint.py with optional enhanced support
3. Test with existing paint operations
4. Fix any issues

### Week 3: Testing & Polish
1. Extensive testing with hardware mouse
2. Test all timing profiles
3. Test pause/resume functionality
4. Performance optimization

### Week 4: GUI & Documentation
1. Add GUI controls (optional)
2. Update user documentation
3. Create tutorial videos
4. Release!

---

## 🚨 Important Notes

### Backward Compatibility

All changes should be **backward compatible**:

```python
# OLD CODE (still works):
pyautogui.moveTo(x, y)
pyautogui.click()

# NEW CODE (enhanced, optional):
if mouse_controller:
    mouse_controller.move_to(x, y)
    mouse_controller.click()
else:
    pyautogui.moveTo(x, y)
    pyautogui.click()
```

### Gradual Migration

You don't need to replace everything at once:

1. **Phase 1**: Add support, keep it disabled by default
2. **Phase 2**: Test with small features
3. **Phase 3**: Gradually enable for more operations
4. **Phase 4**: Make it default (with fallback)

### Error Handling

Always provide fallback to PyAutoGUI:

```python
try:
    mouse = MouseController(use_hardware=True)
except Exception as e:
    print(f"Hardware mouse failed: {e}")
    print("Falling back to PyAutoGUI...")
    mouse = MouseController(use_hardware=False)
```

---

## 📚 Resources

- **Delay System**: `DELAY_SYSTEM_README.md`
- **Hardware Mouse**: `ESP32_INTEGRATION_GUIDE.md`
- **Quick Start**: `DELAY_QUICKSTART.md`
- **Examples**: `test_delays.py`, `analyze_timing.py`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`

---

## ✅ Success Criteria

Integration is complete when:

1. ✅ Delay system works independently
2. ✅ Hardware mouse works independently
3. ✅ Enhanced paint module works
4. ⏳ Paint operations use enhanced features (when enabled)
5. ⏳ Configuration saved/loaded correctly
6. ⏳ GUI controls work (if implemented)
7. ⏳ All tests pass
8. ⏳ Documentation complete

---

**Version**: 1.0  
**Last Updated**: 2026-07-14  
**Status**: Ready for Integration

**Next Step**: Follow Phase 1 (Minimal Integration) to start!
