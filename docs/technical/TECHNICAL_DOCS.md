# Heartopia Auto-Painter - Technical Documentation

## Overview

Automated pixel art painting system for Heartopia game using computer vision and mouse automation.

## Architecture

### Core Modules

#### 1. `app.py` - Main GUI Application
- **Framework**: PySide6 (Qt)
- **Purpose**: Main window, user interaction, session management
- **Key Classes**:
  - `MainWindow`: Primary GUI controller
  - `WorkerSignals`: Thread-safe communication between painter and UI

#### 2. `image_processing.py` - Image Handler
- **Functions**:
  - `load_and_resize_to_grid()`: Converts images to pixel grid
  - `PixelGrid`: Stores downsampled image data
- **Algorithm**: Nearest-neighbor or area-average sampling

#### 3. `paint.py` - Painting Engine
- **Core Functions**:
  - `paint_grid()`: Main painting orchestrator
  - `_paint_grid_by_color()`: Color-grouped painting mode
  - `_bucket_fill_canvas_with_shade()`: Fast fill for large areas
  - `_verify_and_repair_row()`: Pixel verification system

#### 4. `capture.py` - UI Capture
- Captures mouse clicks for button/color positions
- Uses `pynput` for global mouse hooks

#### 5. `screen.py` - Screen Sampling
- `get_screen_pixel_rgb()`: Reads screen pixels for verification
- Cross-platform screen capture (MSS library)

#### 6. `overlay.py` - Visual Overlays
- `RectSelectOverlay`: Canvas selection tool
- `MarkersOverlay`: Color position display
- `StatusOverlay`: In-game progress display

#### 7. `config.py` - Configuration
- Persistent JSON storage for user settings
- Color palette management
- Timing parameters

## Painting Algorithms

### Paint-by-Row Mode
```
for each row:
  for each pixel in row:
    find horizontal runs of same color
    paint run (stroke or clicks)
  verify row and repaint mismatches
```

**Pros**: Predictable order, good for streaming  
**Cons**: More palette switches

### Paint-by-Color Mode
```
group all pixels by shade
for each shade (sorted by frequency):
  select shade once
  paint all pixels of that shade
  verify and repair mismatches
```

**Pros**: Minimal palette switches, faster for complex images  
**Cons**: Less predictable paint order

### Bucket Fill Optimization
1. **Base Fill**: Fill entire canvas with most-used color
2. **Region Fill**: 
   - Find connected regions (flood fill)
   - Paint outline pixels
   - Verify outline integrity
   - Bucket fill interior
   - Spill detection and recovery

## Verification System

### Purpose
Corrects missed/incorrect pixels due to game lag or UI issues.

### Mechanism
```python
for pass in range(max_passes):
  for each pixel:
    sample = get_screen_pixel_rgb(pixel_position)
    if distance(sample, expected) > tolerance:
      add to mismatch list
  if no mismatches:
    return success
  repaint mismatches
return failure if max_passes exceeded
```

### Streaming Verification
Verifies pixels with a lag (e.g., 10 cells behind) while painting continues, reducing end-of-pass delays.

### Auto-Recovery
Prevents infinite loops when verification fails (UI state mismatch, window moved, etc.).

## Timing Parameters

| Parameter | Purpose | Typical Value |
|-----------|---------|---------------|
| `move_duration_s` | Mouse move speed | 0.015s |
| `mouse_down_s` | Click hold time | 0.01s |
| `after_click_delay_s` | Post-click settle | 0.03s |
| `panel_open_delay_s` | Palette panel delay | 0.06s |
| `shade_select_delay_s` | Color select delay | 0.03s |
| `row_delay_s` | Inter-row pause | 0.05s |
| `verify_tolerance` | RGB distance threshold | 35 |
| `verify_settle_s` | Render settle time | 0.05s |

## Color Matching

### Algorithm
```python
def find_best_match(target_rgb, palette):
  best = None
  min_distance = infinity
  for color in palette:
    for shade in color.shades:
      distance = sqrt((r1-r2)² + (g1-g2)² + (b1-b2)²)
      if distance < min_distance:
        min_distance = distance
        best = (color, shade)
  return best
```

Uses **Euclidean distance** in RGB space. Future optimization: KD-tree for O(log n) lookup.

## Performance Optimizations

### Current
- Match result caching (dict lookup)
- Horizontal stroke optimization
- Bucket fill for large monochrome areas
- Region fill with outline verification
- Streaming verification (parallel verify/paint)

### Potential
- Multi-threaded image preprocessing
- GPU-accelerated color matching
- Predictive verification (ML-based failure detection)
- Adaptive timing based on success rate

## Configuration Storage

### File: `~/.config/heartopia-painter/config.json`

```json
{
  "main_colors": [
    {
      "name": "Red",
      "pos": [100, 200],
      "rgb": [255, 0, 0],
      "shades": [...]
    }
  ],
  "shades_panel_button_pos": [50, 50],
  "move_duration_s": 0.015,
  "verify_rows": true,
  "paint_mode": "color"
}
```

## Thread Safety

### Worker Thread Pattern
```python
def paint_worker():
  try:
    paint_grid(...)
    signals.finished.emit()
  except Exception as e:
    signals.error.emit(str(e))

# UI thread connects signals
signals.finished.connect(on_done, Qt.QueuedConnection)
```

All UI updates use queued signals to ensure thread safety.

## Error Handling

### Categories
1. **Configuration Errors**: Missing buttons, colors → User prompt
2. **Runtime Errors**: Game window moved, UI changed → Auto-recovery or pause
3. **Verification Failures**: Max passes exceeded → Configurable: skip or abort

### Fail-Safe
- `pyautogui.FAILSAFE = True`: Move mouse to corner to abort
- ESC key global hook for user pause

## UI Components

### Main Tab
- Image loader
- Canvas preset selector (1:1, 16:9, 9:16, T-shirt)
- Canvas region picker
- Paint/Resume/Stop/Erase controls

### Config Tab
- Color setup wizard
- Button position capture
- Palette management

### Timing Tab
- Timing sliders
- Verification toggles
- Drag stroke enable

## Dependencies

| Library | Purpose |
|---------|---------|
| PySide6 | GUI framework |
| Pillow | Image processing |
| pyautogui | Mouse automation |
| pynput | Global input hooks |
| mss | Screen capture |

## Paint Session State

### Pause/Resume System
```python
_paint_session_sig = (image_path, grid_size, canvas_rect, ...)
_paint_done = set()  # completed (x,y) coords
_paint_paused = bool
```

Resume validates session signature hasn't changed, then skips completed pixels.

## Canvas Presets

| Preset | Sizes |
|--------|-------|
| 1:1 | 30×30, 50×50, 100×100, 150×150 |
| 16:9 | 30×18, 50×28, 100×56, 150×84 |
| 9:16 | 18×30, 28×50, 56×100, 84×150 |
| T-shirt | Front/Back: 64×80, Sleeves: 64×48 |

## Known Issues & Limitations

1. **DPI Scaling**: May affect coordinate mapping on high-DPI displays
2. **Game Updates**: UI changes can break captured button positions
3. **Performance**: Large canvases (150×150) take 15-45 minutes
4. **Color Accuracy**: RGB sampling can vary with lighting/effects in game
5. **Window Focus**: Requires game window to remain focused

## Future Enhancements

- [ ] Dithering support for gradients
- [ ] Multi-layer painting
- [ ] Pattern/stamp tools
- [ ] Collaborative painting (multi-account)
- [ ] OCR-based UI detection (position-independent)
- [ ] Web-based remote control
- [ ] Paint preview simulation

## Code Metrics

- **Total Lines**: ~4,500
- **Main Module**: `paint.py` (~1,800 lines)
- **Average Function**: 50 lines
- **Cyclomatic Complexity**: High in `paint_grid()` (>20)

## Testing

Currently manual testing only. Recommended:
- Unit tests for color matching
- Integration tests for paint algorithms (mock canvas)
- UI automation tests with pytest-qt

## License & Credits

Original: [PckyDev/Heartopia-Image-Painter](https://github.com/PckyDev/Heartopia-Image-Painter)  
Modified by: Nozeed ([Beer-Studio](https://beer-studio.com))

---

**Last Updated**: 2026-03-04  
**Version**: 1.0
