from __future__ import annotations

from collections import deque
import random
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

import pyautogui

from .config import AppConfig, MainColor, ShadeButton
from .screen import get_screen_pixel_rgb

# Optional enhanced features (delay system + hardware mouse)
if TYPE_CHECKING:
    from .delays import DelaySystem
    from .enhanced_paint import MouseController

Point = Tuple[int, int]
HARDWARE_STROKE_CHUNK_MIN_POINTS = 2
HARDWARE_STROKE_CHUNK_MAX_POINTS = 5
HARDWARE_STROKE_CHUNK_PAUSE_MIN_S = 0.040
HARDWARE_STROKE_CHUNK_PAUSE_MAX_S = 0.120
RGB = Tuple[int, int, int]
COLOR_CLICK_RANDOMNESS_PX = 10
GLOBAL_BUTTON_RANDOMNESS_PX = 5
CLICK_DELAY_MIN_S = 0.250
CLICK_DELAY_MAX_S = 0.350
CLICK_HOLD_MIN_S = 0.030
CLICK_HOLD_MAX_S = 0.050
_last_color_click_positions: Dict[Point, Point] = {}


def _randomize_color_click_pos(pos: Point) -> Point:
    """Return a non-repeating point within +/-10px of a color button."""
    base = (int(pos[0]), int(pos[1]))
    previous = _last_color_click_positions.get(base)
    limit = COLOR_CLICK_RANDOMNESS_PX

    for _ in range(8):
        candidate = (
            base[0] + random.randint(-limit, limit),
            base[1] + random.randint(-limit, limit),
        )
        if candidate != previous:
            _last_color_click_positions[base] = candidate
            return candidate

    # A deterministic in-range fallback guarantees progress even when a
    # patched RNG or an unlikely random streak repeats the previous point.
    fallback = (base[0] + 1, base[1])
    if fallback == previous:
        fallback = (base[0] - 1, base[1])
    _last_color_click_positions[base] = fallback
    return fallback


def _randomize_global_button_pos(pos: Point) -> Point:
    """Return a temporary randomized position for a global UI button click."""
    x, y = pos
    return (
        int(x + random.randint(-GLOBAL_BUTTON_RANDOMNESS_PX, GLOBAL_BUTTON_RANDOMNESS_PX)),
        int(y + random.randint(-GLOBAL_BUTTON_RANDOMNESS_PX, GLOBAL_BUTTON_RANDOMNESS_PX)),
    )


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

    # Enhanced features (optional - requires delays.py + enhanced_paint.py)
    use_enhanced_timing: bool = False
    use_hardware_mouse: bool = False
    hardware_click_only: bool = False
    hardware_mouse_port: Optional[str] = None
    hardware_mouse_baudrate: int = 115200
    delay_profile: str = "default"  # "fast", "default", "careful"
    enable_position_jitter: bool = False
    enable_micro_pauses: bool = True
    hardware_disconnect_cb: Optional[Callable[[str], None]] = None


def _random_click_hold_s() -> float:
    return random.uniform(CLICK_HOLD_MIN_S, CLICK_HOLD_MAX_S)


def _random_click_delay_s(extra_delay_s: float = 0.0) -> float:
    return random.uniform(CLICK_DELAY_MIN_S, CLICK_DELAY_MAX_S) + max(0.0, float(extra_delay_s))


def _click_target(pos: Point, options: "PainterOptions", randomizer) -> Point:
    """Apply the button-specific bounded offset in every mouse mode."""
    return randomizer(pos)


def interpolate_points(start: Point, end: Point, steps: int) -> List[Point]:
    """Return evenly sampled integer points including both stroke endpoints."""
    count = max(1, int(steps))
    x0, y0 = start
    x1, y1 = end
    return [
        (int(round(x0 + (x1 - x0) * i / count)), int(round(y0 + (y1 - y0) * i / count)))
        for i in range(1, count + 1)
    ]


def _tap(
    pos: Point,
    opts: PainterOptions,
    extra_delay_s: float = 0.0,
    mouse_controller: Optional["MouseController"] = None,
):
    """Tap at position with optional enhanced timing/hardware mouse.
    
    Args:
        pos: (x, y) screen coordinates
        opts: timing options
        extra_delay_s: additional delay after click
        mouse_controller: optional MouseController for enhanced features
    """
    # Enhanced mode: use MouseController if provided
    if mouse_controller is not None:
        try:
            from .enhanced_paint import enhanced_tap
            enhanced_tap(
                mouse_controller,
                pos,
                hold_duration=float(opts.mouse_down_s),
                extra_delay=float(extra_delay_s),
            )
            return
        except Exception:
            # Never switch to software input after a hardware disconnect.
            if bool(getattr(mouse_controller, "use_hardware", False)) or bool(
                getattr(mouse_controller, "use_hardware_click", False)
            ):
                raise
    
    # Standard mode: PyAutoGUI
    pyautogui.moveTo(pos[0], pos[1], duration=max(0.0, float(opts.move_duration_s)))
    pyautogui.mouseDown(button="left")
    time.sleep(_random_click_hold_s())
    pyautogui.mouseUp(button="left")
    time.sleep(_random_click_delay_s(extra_delay_s))


def _stroke(
    points: List[Point],
    opts: PainterOptions,
    should_stop: Optional[Callable[[], bool]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Draw stroke through points with optional enhanced timing/hardware mouse.
    
    Args:
        points: list of (x, y) coordinates to drag through
        opts: timing options
        should_stop: optional callback to check if operation should stop
        mouse_controller: optional MouseController for enhanced features
    """
    if not points:
        return
    
    # Enhanced mode: use MouseController if provided
    if mouse_controller is not None:
        try:
            from .enhanced_paint import enhanced_stroke
            enhanced_stroke(
                points,
                mouse_controller,
                substeps_per_cell=6,
                should_stop=should_stop,
            )
            return
        except Exception:
            # Never switch to software input after a hardware disconnect.
            if bool(getattr(mouse_controller, "use_hardware", False)):
                raise
    
    # Standard mode: try pynput first, fallback to PyAutoGUI
    # Some games respond better to a lower-level mouse controller than PyAutoGUI.
    try:
        from pynput.mouse import Button, Controller  # type: ignore

        mouse = Controller()
        mouse.position = points[0]
        mouse.press(Button.left)
        time.sleep(_random_click_hold_s())

        step = max(0.0, float(opts.drag_step_duration_s))
        substeps_per_cell = 6

        for target in points[1:]:
            if should_stop and should_stop():
                break
            x0, y0 = mouse.position
            x1, y1 = target
            dx = x1 - x0
            dy = y1 - y0

            # Interpolate a few micro-moves per cell so the game receives
            # continuous mouse-move events while the button is held.
            for mx, my in interpolate_points((x0, y0), (x1, y1), substeps_per_cell):
                if should_stop and should_stop():
                    break
                mouse.position = (mx, my)
                if step > 0:
                    time.sleep(step / max(1, int(substeps_per_cell)))

        mouse.release(Button.left)
        time.sleep(_random_click_delay_s(float(opts.after_drag_delay_s)))
        return
    except Exception:
        # Fallback: PyAutoGUI drag
        pass

    pyautogui.moveTo(points[0][0], points[0][1], duration=max(0.0, float(opts.move_duration_s)))
    pyautogui.mouseDown(button="left")
    time.sleep(_random_click_hold_s())
    try:
        step = max(0.0, float(opts.drag_step_duration_s))
        substeps_per_cell = 6
        curx, cury = points[0]
        for px, py in points[1:]:
            if should_stop and should_stop():
                return
            dx = px - curx
            dy = py - cury
            for mx, my in interpolate_points((curx, cury), (px, py), substeps_per_cell):
                if should_stop and should_stop():
                    return
                pyautogui.moveTo(mx, my, duration=0)
                if step > 0:
                    time.sleep(step / max(1, int(substeps_per_cell)))
            curx, cury = px, py
    finally:
        pyautogui.mouseUp(button="left")
    time.sleep(_random_click_delay_s(float(opts.after_drag_delay_s)))


def _rapid_click_stroke(
    points: List[Point],
    opts: PainterOptions,
    should_stop: Optional[Callable[[], bool]] = None,
    on_point: Optional[Callable[[int], None]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Fast, reliable stroke: click every point in a run with reduced delays.

    This is a fallback when true drag-painting doesn't register in-game.
    We reuse the drag timing knobs as stroke timing:
    - drag_step_duration_s: delay between clicks within the stroke
    - after_drag_delay_s: delay after the stroke finishes
    
    Args:
        points: list of (x, y) coordinates to click
        opts: timing options
        should_stop: optional callback to check if operation should stop
        on_point: optional callback called after each point is painted
        mouse_controller: optional MouseController for enhanced features
    """

    if not points:
        return

    # A real hardware mouse must keep the button held while traversing the
    # run.  Clicking each point independently lets the game coalesce/drop
    # input (the common 3-pixels-on/1-pixel-missing pattern).  Keep the click
    # fallback for software and hardware-click-only modes.
    if mouse_controller is not None and getattr(mouse_controller, "use_hardware", False) is True:
        from .enhanced_paint import enhanced_stroke

        chunks = _split_hardware_stroke_chunks(points)
        point_index = 0
        for chunk_index, chunk in enumerate(chunks):
            if should_stop and should_stop():
                return

            # A one-point remainder is intentionally handled as a precise
            # press/release stroke. Larger chunks keep the button held while
            # visiting every point, then release before the next curved travel.
            completed = enhanced_stroke(
                chunk,
                mouse_controller,
                should_stop=should_stop,
                post_delay=False,
            )
            if not completed:
                return

            if on_point:
                for idx in range(point_index, point_index + len(chunk)):
                    try:
                        on_point(idx)
                    except Exception:
                        pass
            point_index += len(chunk)

            if chunk_index < len(chunks) - 1:
                pause_s = random.uniform(
                    HARDWARE_STROKE_CHUNK_PAUSE_MIN_S,
                    HARDWARE_STROKE_CHUNK_PAUSE_MAX_S,
                )
                if not _interruptible_sleep(pause_s, should_stop):
                    return
        return

    per_click_delay = max(0.0, float(opts.drag_step_duration_s))
    after_stroke_delay = max(0.0, float(opts.after_drag_delay_s))

    for idx, (px, py) in enumerate(points):
        if should_stop and should_stop():
            return
        # Use _tap with mouse_controller if provided
        _tap((px, py), opts, extra_delay_s=0.0, mouse_controller=mouse_controller)
        if per_click_delay > 0:
            time.sleep(per_click_delay)
        if on_point:
            try:
                on_point(idx)
            except Exception:
                pass

    if after_stroke_delay > 0:
        time.sleep(after_stroke_delay)


def _split_hardware_stroke_chunks(
    points: List[Point],
    randint: Optional[Callable[[int, int], int]] = None,
) -> List[List[Point]]:
    """Split a contiguous run into ordered random 2-5 point strokes.

    The final remainder may contain one point. Passing ``randint`` keeps the
    helper deterministic in tests without changing runtime randomness.
    """
    choose_size = randint or random.randint
    chunks: List[List[Point]] = []
    start = 0
    while start < len(points):
        requested = int(
            choose_size(
                HARDWARE_STROKE_CHUNK_MIN_POINTS,
                HARDWARE_STROKE_CHUNK_MAX_POINTS,
            )
        )
        chunk_size = max(
            HARDWARE_STROKE_CHUNK_MIN_POINTS,
            min(HARDWARE_STROKE_CHUNK_MAX_POINTS, requested),
        )
        end = min(len(points), start + chunk_size)
        chunks.append(points[start:end])
        start = end
    return chunks


def _interruptible_sleep(duration_s: float, should_stop: Optional[Callable[[], bool]] = None) -> bool:
    """Sleep in small increments so ESC/pause can interrupt quickly.

    Returns False if interrupted by should_stop(), True if the full sleep elapsed.
    """

    try:
        dur = max(0.0, float(duration_s))
    except Exception:
        dur = 0.0

    end = time.time() + dur
    while True:
        if should_stop and should_stop():
            return False
        now = time.time()
        if now >= end:
            return True
        time.sleep(min(0.02, max(0.0, end - now)))


# Back-compat: some older call sites used the misspelling.
_interruptable_sleep = _interruptible_sleep


def erase_canvas(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    options: PainterOptions,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Erase the whole canvas quickly.

    Workflow:
    - Select eraser tool
    - Click thickness-up 5x (assumes that reaches 10x10)
    - Sweep horizontal bands across the canvas
    """

    if cfg.eraser_tool_button_pos is None or cfg.eraser_thickness_up_button_pos is None:
        raise RuntimeError(
            "Eraser configuration missing. Set 'eraser tool button' and 'eraser thickness + button' first."
        )

    if grid_w <= 0 or grid_h <= 0:
        raise RuntimeError("Invalid grid size.")

    def stop() -> bool:
        return bool(should_stop and should_stop())

    if status_cb:
        try:
            status_cb("Selecting eraser tool…")
        except Exception:
            pass
    _tap(_click_target(cfg.eraser_tool_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)
    if stop():
        return

    if status_cb:
        try:
            status_cb("Setting eraser size (5x)…")
        except Exception:
            pass
    for _ in range(5):
        if stop():
            return
        _tap(_click_target(cfg.eraser_thickness_up_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    if status_cb:
        try:
            status_cb("Erasing canvas…")
        except Exception:
            pass

    # Erase-specific click timing: much faster than paint, but keep a tiny
    # non-zero hold so games register the click.
    erase_click_opts = PainterOptions(
        move_duration_s=0.0,
        mouse_down_s=max(0.006, min(0.02, float(options.mouse_down_s))),
        after_click_delay_s=max(0.0, min(0.01, float(options.after_click_delay_s))),
        panel_open_delay_s=float(options.panel_open_delay_s),
        shade_select_delay_s=float(options.shade_select_delay_s),
        row_delay_s=float(options.row_delay_s),
        enable_drag_strokes=False,
        drag_step_duration_s=float(options.drag_step_duration_s),
        after_drag_delay_s=float(options.after_drag_delay_s),
    )

    # Periodic micro-pauses help avoid the game/UI dropping fast click bursts.
    taps = 0
    burst_pause_every = 30
    burst_pause_s = 0.02

    # Erase should always be click-based (no stroke-neighbors/drag strokes),
    # since drag can fail to register in some UI states.
    step = 10
    y_step = 10

    for band_idx, y0 in enumerate(range(0, grid_h, y_step)):
        if stop():
            return

        # Aim for the middle of the vertical band.
        y = min(grid_h - 1, y0 + y_step // 2)

        if status_cb and (y0 % max(1, y_step * 4) == 0):
            try:
                status_cb(f"Erasing… row {y0+1}/{grid_h}")
            except Exception:
                pass

        # Click-based erase, fast but reliable: step by 10 cells.
        # Use a snake pattern so the cursor doesn't waste time jumping back.
        xs = list(range(0, grid_w, step))
        if (grid_w - 1) not in xs:
            xs.append(grid_w - 1)
        if (band_idx % 2) == 1:
            xs = list(reversed(xs))

        for x in xs:
            if stop():
                return
            pt = _cell_center(canvas_rect, grid_w, grid_h, int(x), int(y))
            _tap(pt, erase_click_opts, mouse_controller=mouse_controller)
            taps += 1
            if (taps % burst_pause_every) == 0:
                _interruptible_sleep(burst_pause_s, should_stop)


def _find_best_match(rgb: RGB, cfg: AppConfig) -> Optional[Tuple[MainColor, ShadeButton]]:
    # Naive: choose closest shade across all colors.
    # Later: speed up with caching / KD-tree.
    best = None
    best_dist = None

    def dist2(a: RGB, b: RGB) -> int:
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2

    for mc in cfg.main_colors:
        for sh in mc.shades:
            d = dist2(rgb, sh.rgb)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (mc, sh)
    return best


def count_paintable_pixels(
    cfg: AppConfig,
    grid_w: int,
    grid_h: int,
    get_pixel: Callable[[int, int], RGB],
    skip: Optional[Callable[[int, int], bool]] = None,
) -> int:
    """Count cells that can be mapped to a configured shade."""

    if grid_w <= 0 or grid_h <= 0:
        return 0
    match_cache: Dict[RGB, Optional[Tuple[MainColor, ShadeButton]]] = {}
    total = 0
    for y in range(grid_h):
        for x in range(grid_w):
            if skip is not None and skip(x, y):
                continue
            rgb = get_pixel(x, y)
            if rgb in match_cache:
                match = match_cache[rgb]
            else:
                match = _find_best_match(rgb, cfg)
                match_cache[rgb] = match
            if match is not None:
                total += 1
    return total


def _dist2(a: RGB, b: RGB) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _sleep_with_stop(duration_s: float, should_stop: Optional[Callable[[], bool]] = None) -> bool:
    """Sleep in small chunks so stop/pause can interrupt quickly.

    Returns False if interrupted by should_stop.
    """

    d = max(0.0, float(duration_s))
    if d <= 0:
        return True
    end = time.perf_counter() + d
    while True:
        if should_stop and should_stop():
            return False
        now = time.perf_counter()
        if now >= end:
            return True
        time.sleep(min(0.02, max(0.0, end - now)))


def _maybe_emit_verify(
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]],
    pt: Optional[Tuple[int, int]],
    idx: int,
    every: int = 10,
) -> None:
    if verify_cb is None:
        return
    if every <= 1 or (idx % every) == 0:
        try:
            verify_cb(pt)
        except Exception:
            pass


def _create_mouse_controller(opts: PainterOptions) -> Optional["MouseController"]:
    """Create MouseController with DelaySystem and MouseConfig if enhanced features are enabled.
    
    Returns None if enhanced features are disabled or unavailable.
    """
    if not opts.use_enhanced_timing and not opts.use_hardware_mouse and not opts.hardware_click_only:
        return None
    
    try:
        from .delays import DelayConfig, DelaySystem
        from .enhanced_paint import MouseController
        from .config import load_mouse_config
        
        # Load mouse configuration
        mouse_config = load_mouse_config()
        
        # Create delay system with mouse config
        # Use a precision movement profile: dense steps, no curve/jitter
        # randomness, and stable per-step timing.
        precision_config = DelayConfig(
            steps=100,
            step_variance=0,
            bezier_control_randomness=0.0,
            timing_jitter=0.0,
            speed_variation=0.0,
        )
        delay_system = DelaySystem(config=precision_config, mouse_config=mouse_config)
        
        # Set optional features from opts (for backward compatibility)
        delay_system.enable_position_jitter = opts.enable_position_jitter
        delay_system.enable_micro_pauses = opts.enable_micro_pauses

        if opts.hardware_click_only:
            port = opts.hardware_mouse_port or mouse_config.arduino_port
            if not port:
                raise RuntimeError("Hardware click is enabled but no serial port is configured")

            from .hardware_mouse import HardwareMouse, HardwareMouseConfig

            hardware_click = HardwareMouse(
                HardwareMouseConfig(
                    port=port,
                    baudrate=int(opts.hardware_mouse_baudrate),
                    on_disconnect=opts.hardware_disconnect_cb,
                )
            )
            hardware_click.connect()
            # Cursor movement remains software-controlled. Disable only the
            # enhanced position jitter so the click target remains exact.
            delay_system.enable_position_jitter = False
            return MouseController(
                use_hardware=False,
                hardware_click=hardware_click,
                delay_system=delay_system,
                fallback_to_software=False,
            )

        if opts.use_hardware_mouse:
            port = opts.hardware_mouse_port or mouse_config.arduino_port
            if not port:
                raise RuntimeError("Hardware Mouse is enabled but no serial port is configured")
            from .hardware_mouse import HardwareMouseConfig
            hw_config = HardwareMouseConfig(
                port=port,
                baudrate=int(opts.hardware_mouse_baudrate),
                click_randomness_px=mouse_config.click_randomness_px,
                on_disconnect=opts.hardware_disconnect_cb,
            )
            return MouseController(
                use_hardware=True,
                hardware_config=hw_config,
                delay_system=delay_system,
                fallback_to_software=False,
            )
        
        # Create mouse controller (hardware or software)
        port = opts.hardware_mouse_port or mouse_config.arduino_port
        if opts.use_hardware_mouse and port:
            try:
                from .hardware_mouse import HardwareMouse, HardwareMouseConfig
                hw_config = HardwareMouseConfig(
                    port=port,
                    click_randomness_px=mouse_config.click_randomness_px
                )
                hardware_mouse = HardwareMouse(config=hw_config)
                hardware_mouse.connect()
                mouse_controller = MouseController(
                    delay_system=delay_system,
                    mouse_driver=hardware_mouse,
                    use_bezier_movement=True,
                )
                
                # Print session info
                print(f"[INFO] Hardware Mouse enabled on {port}")
                print(f"[INFO] Click randomness: ±{mouse_config.click_randomness_px}px")
                if mouse_config.enable_mistakes:
                    print(f"[INFO] Mistake simulation: {mouse_config.mistake_probability*100:.1f}% chance")
                if mouse_config.enable_breaks:
                    print(f"[INFO] Breaks enabled: every {mouse_config.break_min_actions}-{mouse_config.break_max_actions} actions")
                if mouse_config.enable_fatigue:
                    print(f"[INFO] Fatigue simulation: {mouse_config.fatigue_slowdown_per_100_actions*100:.1f}% per 100 actions")
                print(f"[INFO] Session limit: {mouse_config.session_time_limit_hours} hours")
                
                return mouse_controller
            except Exception as e:
                # Fallback to software mouse if hardware fails
                import sys
                print(f"[WARNING] Hardware mouse failed ({e}), using software mouse", file=sys.stderr)
        
        # Software mouse (PyAutoGUI wrapper)
        return MouseController(use_hardware=False, delay_system=delay_system)
    
    except Exception as e:
        # Enhanced features not available
        import sys
        print(f"[WARNING] Failed to create mouse controller: {e}", file=sys.stderr)
        if opts.use_hardware_mouse or opts.hardware_click_only:
            raise
        return None


def _ui_sanity_check_at(
    pos: Point,
    expected_rgb: RGB,
    tol: int,
) -> bool:
    """Return True if the screen pixel at pos is close to expected_rgb.

    Used to detect when the game window/UI has moved (captured button coords no
    longer line up), which otherwise causes endless repaint attempts.
    """

    try:
        actual = get_screen_pixel_rgb(int(pos[0]), int(pos[1]))
    except Exception:
        return False
    tol2 = max(0, int(tol)) ** 2
    return _dist2(actual, expected_rgb) <= tol2


def _cell_center(canvas_rect: Tuple[int, int, int, int], grid_w: int, grid_h: int, x: int, y: int) -> Point:
    x0, y0, w, h = canvas_rect
    cell_w = w / grid_w
    cell_h = h / grid_h
    cx = int(x0 + (x + 0.5) * cell_w)
    cy = int(y0 + (y + 0.5) * cell_h)
    return (cx, cy)


def _select_shade(
    cfg: AppConfig,
    options: PainterOptions,
    main: MainColor,
    shade: ShadeButton,
    last_main: Optional[MainColor],
    last_shade: Optional[ShadeButton],
    in_shades_panel: bool,
    mouse_controller: Optional["MouseController"] = None,
) -> Tuple[Optional[MainColor], Optional[ShadeButton], bool]:
    if cfg.shades_panel_button_pos is None or cfg.back_button_pos is None:
        raise RuntimeError("Color configuration incomplete. Set shades panel + back button positions first.")

    # Sanity tolerance for UI sampling (button pixel colors can vary slightly).
    ui_tol = max(60, int(getattr(cfg, "verify_tolerance", 35)))

    # Select main if needed
    if last_main is None or main.name != last_main.name:
        # Defensive: ALWAYS attempt to return to the main palette before
        # selecting a main color. Our in_shades_panel flag can get out of sync
        # if a Back click didn't register, which causes main-color clicks to hit
        # the wrong UI and can create verification loops.
        _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)
        in_shades_panel = False
        _tap(_randomize_color_click_pos(main.pos), options, mouse_controller=mouse_controller)
        _tap(_click_target(cfg.shades_panel_button_pos, options, _randomize_global_button_pos), options, extra_delay_s=options.panel_open_delay_s, mouse_controller=mouse_controller)
        in_shades_panel = True
        last_main = main
        last_shade = None

    if not in_shades_panel:
        _tap(_click_target(cfg.shades_panel_button_pos, options, _randomize_global_button_pos), options, extra_delay_s=options.panel_open_delay_s, mouse_controller=mouse_controller)
        in_shades_panel = True

    # NOTE: We intentionally do NOT hard-fail based on sampling shade.pos.
    # Shade button pixels can vary due to hover/selection highlights and UI
    # effects, which can produce false positives even when the window is aligned.
    # We'll rely on repaint verification to correct missed clicks.

    if last_shade is None or shade.pos != last_shade.pos:
        _tap(
            _randomize_color_click_pos(shade.pos),
            options,
            extra_delay_s=options.shade_select_delay_s,
            mouse_controller=mouse_controller,
        )
        # Extra tap helps when the first click doesn't register.
        _tap(
            _randomize_color_click_pos(shade.pos),
            options,
            extra_delay_s=0.0,
            mouse_controller=mouse_controller,
        )
        last_shade = shade

    return last_main, last_shade, in_shades_panel


def _bucket_fill_canvas_with_shade(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    main: MainColor,
    shade: ShadeButton,
    options: PainterOptions,
    should_stop: Optional[Callable[[], bool]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Bucket fill the entire canvas with the given shade.

    Requires captured tool buttons: paint tool + bucket tool.
    """

    if cfg.paint_tool_button_pos is None or cfg.bucket_tool_button_pos is None:
        raise RuntimeError(
            "Bucket fill is enabled but tool button positions are not set. "
            "Capture 'paint tool button' and 'bucket tool button' first."
        )

    # Ensure we're in a consistent UI state while picking the shade.
    _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    last_main: Optional[MainColor] = None
    last_shade: Optional[ShadeButton] = None
    in_shades_panel = False
    last_main, last_shade, in_shades_panel = _select_shade(
        cfg=cfg,
        options=options,
        main=main,
        shade=shade,
        last_main=last_main,
        last_shade=last_shade,
        in_shades_panel=in_shades_panel,
        mouse_controller=mouse_controller,
    )
    if in_shades_panel:
        _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    if should_stop and should_stop():
        return

    # Switch to bucket tool and fill inside the canvas.
    _tap(_click_target(cfg.bucket_tool_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    x0, y0, w, h = canvas_rect
    # Click near the center of the canvas to fill it.
    fill_pt = (int(x0 + w * 0.5), int(y0 + h * 0.5))
    _tap(fill_pt, options, mouse_controller=mouse_controller)

    # Switch back to paint tool so subsequent pixel painting works as expected.
    _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    # Tiny settle helps some games register the fill.
    settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))
    if settle_s > 0:
        time.sleep(settle_s)


def _paint_coord_runs(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    coords: List[Tuple[int, int]],
    options: PainterOptions,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Paint an arbitrary set of coords (assumes correct shade already selected)."""

    if not coords:
        return

    x0, y0, w, h = canvas_rect
    cell_w = w / grid_w
    cell_h = h / grid_h

    coords.sort(key=lambda xy: (xy[1], xy[0]))
    i = 0
    while i < len(coords):
        if should_stop and should_stop():
            return
        x, y = coords[i]
        run = [(x, y)]
        j = i + 1
        while j < len(coords):
            nx, ny = coords[j]
            if ny != y or nx != run[-1][0] + 1:
                break
            run.append((nx, ny))
            j += 1

        pts: List[Point] = []
        for rx, ry in run:
            cx = int(x0 + (rx + 0.5) * cell_w)
            cy = int(y0 + (ry + 0.5) * cell_h)
            pts.append((cx, cy))

        if options.enable_drag_strokes and len(pts) >= 2:
            if progress_cb:
                def _on_point(idx: int) -> None:
                    try:
                        rx, ry = run[idx]
                    except Exception:
                        return
                    progress_cb(int(rx), int(ry))

                _rapid_click_stroke(pts, options, should_stop=should_stop, on_point=_on_point, mouse_controller=mouse_controller)
            else:
                _rapid_click_stroke(pts, options, should_stop=should_stop, mouse_controller=mouse_controller)
        else:
            for (rx, ry), p in zip(run, pts):
                if should_stop and should_stop():
                    return
                _tap(p, options, mouse_controller=mouse_controller)
                if progress_cb:
                    progress_cb(int(rx), int(ry))

        i = j


def _verify_outline_then_repair(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    outline_coords: List[Tuple[int, int]],
    expected_rgb: Optional[RGB],
    avoid_rgb: Optional[RGB],
    options: PainterOptions,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]] = None,
    max_passes_override: Optional[int] = None,
    local_base_rgb: Optional[Callable[[int, int], Optional[RGB]]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> bool:
    """Verify outline pixels are painted correctly; repaint misses if needed.

    Returns True when the outline verifies within max passes.
    Returns False if it never converges (caller should skip bucket-fill).
    """

    if not outline_coords:
        return True

    # For region bucket-fill spill safety, it's often more reliable to verify that
    # outline pixels are NOT the base fill color, rather than requiring an exact
    # match to the target shade (games can alter displayed RGB).
    if expected_rgb is None and avoid_rgb is None:
        return True

    tol = int(getattr(cfg, "verify_tolerance", 35))
    tol2 = max(0, tol) ** 2
    # When verifying that outline pixels are NOT the base fill color, we want
    # a stricter "base similarity" threshold; otherwise a large verify tolerance
    # can cause false failures if the outline shade is somewhat close to the base.
    base_tol = max(8, int(tol * 0.5))
    base_tol2 = max(0, base_tol) ** 2
    settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))
    # Outline verification is just for spill safety; keep it bounded.
    max_passes = max(1, min(5, int(getattr(cfg, "verify_max_passes", 10))))
    if max_passes_override is not None:
        try:
            max_passes = max(1, int(max_passes_override))
        except Exception:
            pass

    coords = list(outline_coords)
    coords.sort(key=lambda xy: (xy[1], xy[0]))

    for _pass in range(max_passes):
        if should_stop and should_stop():
            return False
        if settle_s > 0:
            if not _sleep_with_stop(settle_s, should_stop=should_stop):
                return False

        if status_cb is not None:
            try:
                if avoid_rgb is not None:
                    status_cb(f"Verifying outline vs base… pass {_pass+1}/{max_passes}")
                else:
                    status_cb(f"Verifying outline… pass {_pass+1}/{max_passes}")
            except Exception:
                pass

        mism: List[Tuple[int, int]] = []
        for i, (x, y) in enumerate(coords):
            if should_stop and should_stop():
                return False
            cx, cy = _cell_center(canvas_rect, grid_w, grid_h, x, y)
            _maybe_emit_verify(verify_cb, (x, y), i, every=8)
            actual = get_screen_pixel_rgb(cx, cy)

            if avoid_rgb is not None:
                base_ref = None
                if local_base_rgb is not None:
                    try:
                        base_ref = local_base_rgb(int(x), int(y))
                    except Exception:
                        base_ref = None
                if base_ref is None:
                    base_ref = avoid_rgb
                # Primary goal: outline should not look like base.
                # If expected_rgb is provided too, use it to disambiguate when the
                # outline shade is close to the base shade (avoid false mismatches).
                # Hole detection must always consider the global base.
                # Local base sampling can be polluted if the nearest "outside"
                # neighbor is already painted, which would otherwise mask holes.
                looks_like_base = False
                try:
                    looks_like_base = looks_like_base or (_dist2(actual, avoid_rgb) <= base_tol2)
                except Exception:
                    pass
                try:
                    if base_ref is not None:
                        looks_like_base = looks_like_base or (_dist2(actual, base_ref) <= base_tol2)
                except Exception:
                    pass
                if expected_rgb is not None:
                    looks_like_expected = _dist2(actual, expected_rgb) <= tol2
                    if looks_like_base and (not looks_like_expected):
                        mism.append((x, y))
                else:
                    if looks_like_base:
                        mism.append((x, y))
            else:
                # Fallback: mismatch if pixel doesn't match expected.
                if expected_rgb is None:
                    continue
                if _dist2(actual, expected_rgb) > tol2:
                    mism.append((x, y))

        if not mism:
            _maybe_emit_verify(verify_cb, None, 0, every=1)
            return True

        # Repaint just the mismatched outline pixels.
        # Use reliable click taps (double-tap) rather than strokes.
        try:
            if cfg.paint_tool_button_pos is not None:
                _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)
        except Exception:
            pass
        for x, y in mism:
            if should_stop and should_stop():
                return False
            cx, cy = _cell_center(canvas_rect, grid_w, grid_h, int(x), int(y))
            _tap((cx, cy), options, mouse_controller=mouse_controller)
            _tap((cx, cy), options, extra_delay_s=0.01, mouse_controller=mouse_controller)

    _maybe_emit_verify(verify_cb, None, 0, every=1)
    return False


def _verify_and_repair_row(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    y: int,
    row_expected: List[Optional[Tuple[MainColor, ShadeButton]]],
    options: PainterOptions,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    tol = int(getattr(cfg, "verify_tolerance", 35))
    tol2 = max(0, tol) ** 2
    max_passes = max(1, int(getattr(cfg, "verify_max_passes", 10)))
    settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))

    prev_mismatch_n: Optional[int] = None
    stagnant_passes = 0

    for _pass in range(max_passes):
        if should_stop and should_stop():
            return
        if settle_s > 0:
            if not _sleep_with_stop(settle_s, should_stop=should_stop):
                return

        if status_cb is not None:
            try:
                status_cb(f"Verifying row {y+1}/{grid_h}… pass {_pass+1}/{max_passes}")
            except Exception:
                pass

        # Collect mismatches grouped by shade
        groups: Dict[Tuple[str, Point], Tuple[MainColor, ShadeButton, List[int]]] = {}
        for x in range(grid_w):
            if should_stop and should_stop():
                return
            exp = row_expected[x] if x < len(row_expected) else None
            if exp is None:
                continue
            main, shade = exp

            cx, cy = _cell_center(canvas_rect, grid_w, grid_h, x, y)
            _maybe_emit_verify(verify_cb, (x, y), x, every=6)
            actual = get_screen_pixel_rgb(cx, cy)
            if _dist2(actual, shade.rgb) <= tol2:
                continue
            key = (main.name, shade.pos)
            if key not in groups:
                groups[key] = (main, shade, [])
            groups[key][2].append(x)

        if not groups:
            _maybe_emit_verify(verify_cb, None, 0, every=1)
            return

        mismatch_n = sum(len(t[2]) for t in groups.values())
        if prev_mismatch_n is not None:
            if mismatch_n >= prev_mismatch_n:
                stagnant_passes += 1
            else:
                stagnant_passes = 0
        prev_mismatch_n = mismatch_n

        if stagnant_passes >= max(1, int(getattr(cfg, "verify_auto_recover_after_passes", 2))) and bool(
            getattr(cfg, "verify_auto_recover_loops", False)
        ):
            if status_cb is not None:
                try:
                    status_cb("Verify loop detected; resyncing UI and continuing…")
                except Exception:
                    pass
            # Resync palette state.
            try:
                _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
                _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
            except Exception:
                pass
            _maybe_emit_verify(verify_cb, None, 0, every=1)
            return

        # Repaint mismatches, minimizing palette switches.
        last_main: Optional[MainColor] = None
        last_shade: Optional[ShadeButton] = None
        in_shades_panel = False

        ordered = sorted(groups.values(), key=lambda t: (-len(t[2]), t[0].name, t[1].pos[0], t[1].pos[1]))
        for main, shade, xs in ordered:
            if should_stop and should_stop():
                return

            last_main, last_shade, in_shades_panel = _select_shade(
                cfg,
                options,
                main,
                shade,
                last_main,
                last_shade,
                in_shades_panel,
                mouse_controller=mouse_controller,
            )

            xs.sort()
            # Break into contiguous runs so we can use the fast stroke option.
            run: List[int] = []
            for x in xs:
                if not run or x == run[-1] + 1:
                    run.append(x)
                    continue
                pts = [_cell_center(canvas_rect, grid_w, grid_h, rx, y) for rx in run]
                if options.enable_drag_strokes and len(pts) >= 2:
                    _rapid_click_stroke(pts, options, should_stop=should_stop, mouse_controller=mouse_controller)
                else:
                    for p in pts:
                        if should_stop and should_stop():
                            return
                        _tap(p, options, mouse_controller=mouse_controller)
                if progress_cb:
                    for rx in run:
                        progress_cb(rx, y)
                run = [x]

            if run:
                pts = [_cell_center(canvas_rect, grid_w, grid_h, rx, y) for rx in run]
                if options.enable_drag_strokes and len(pts) >= 2:
                    _rapid_click_stroke(pts, options, should_stop=should_stop, mouse_controller=mouse_controller)
                else:
                    for p in pts:
                        if should_stop and should_stop():
                            return
                        _tap(p, options, mouse_controller=mouse_controller)
                if progress_cb:
                    for rx in run:
                        progress_cb(rx, y)

        if in_shades_panel:
            _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_controller)

    _maybe_emit_verify(verify_cb, None, 0, every=1)

    # If we get here, verification never converged.
    if bool(getattr(cfg, "verify_auto_recover_loops", False)):
        if status_cb is not None:
            try:
                status_cb("Verify did not converge; skipping and continuing…")
            except Exception:
                pass
        _maybe_emit_verify(verify_cb, None, 0, every=1)
        try:
            _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
        except Exception:
            pass
        return

    raise RuntimeError(
        f"Row verification failed (row {y+1}/{grid_h}). "
        f"Try increasing Verify tolerance or timing, or disable verification."
    )


def _verify_and_repair_color_group(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    main: MainColor,
    shade: ShadeButton,
    coords: List[Tuple[int, int]],
    options: PainterOptions,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> None:
    """Verify/repaint a single shade group after painting it.

    This is used by Paint-by-Color to keep the initial pass fast and then
    correct any missed pixels per color.
    """

    tol = int(getattr(cfg, "verify_tolerance", 35))
    tol2 = max(0, tol) ** 2
    max_passes = max(1, int(getattr(cfg, "verify_max_passes", 10)))
    settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))

    coords_sorted = sorted(coords, key=lambda xy: (xy[1], xy[0]))

    for _pass in range(max_passes):
        if should_stop and should_stop():
            return
        if settle_s > 0:
            if not _sleep_with_stop(settle_s, should_stop=should_stop):
                return

        if status_cb is not None:
            try:
                status_cb(
                    f"Verifying color '{main.name}/{shade.name}'… pass {_pass+1}/{max_passes}"
                )
            except Exception:
                pass

        mismatches: List[Tuple[int, int]] = []
        for i, (x, y) in enumerate(coords_sorted):
            if should_stop and should_stop():
                return
            cx, cy = _cell_center(canvas_rect, grid_w, grid_h, x, y)
            _maybe_emit_verify(verify_cb, (x, y), i, every=10)
            actual = get_screen_pixel_rgb(cx, cy)
            if _dist2(actual, shade.rgb) > tol2:
                mismatches.append((x, y))

        if not mismatches:
            _maybe_emit_verify(verify_cb, None, 0, every=1)
            return

        # Force a full reselect each pass; if a click failed earlier, relying on
        # cached state can keep repainting with the wrong shade.
        last_main: Optional[MainColor] = None
        last_shade: Optional[ShadeButton] = None
        in_shades_panel = False

        last_main, last_shade, in_shades_panel = _select_shade(
            cfg,
            options,
            main,
            shade,
            last_main,
            last_shade,
            in_shades_panel,
            mouse_controller=mouse_controller,
        )

        # Repaint mismatches, using contiguous horizontal runs for speed.
        mismatches.sort(key=lambda xy: (xy[1], xy[0]))
        i = 0
        while i < len(mismatches):
            if should_stop and should_stop():
                return
            x, y = mismatches[i]
            run = [(x, y)]
            j = i + 1
            while j < len(mismatches):
                nx, ny = mismatches[j]
                if ny != y or nx != run[-1][0] + 1:
                    break
                run.append((nx, ny))
                j += 1

            pts = [_cell_center(canvas_rect, grid_w, grid_h, rx, ry) for rx, ry in run]
            if options.enable_drag_strokes and len(pts) >= 2:
                _rapid_click_stroke(pts, options, should_stop=should_stop, mouse_controller=mouse_controller)
            else:
                for p in pts:
                    if should_stop and should_stop():
                        return
                    _tap(p, options, mouse_controller=mouse_controller)

            if progress_cb:
                for rx, ry in run:
                    progress_cb(rx, ry)

            i = j

    if bool(getattr(cfg, "verify_auto_recover_loops", False)):
        if status_cb is not None:
            try:
                status_cb("Verify did not converge for a color; skipping and continuing…")
            except Exception:
                pass
        _maybe_emit_verify(verify_cb, None, 0, every=1)
        try:
            _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
        except Exception:
            pass
        return

    raise RuntimeError(
        "Color verification failed for a shade group. "
        "Try increasing Verify tolerance or timing, or disable verification."
    )


def paint_grid(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    get_pixel: Callable[[int, int], RGB],
    options: Optional[PainterOptions] = None,
    paint_mode: str = "row",
    skip: Optional[Callable[[int, int], bool]] = None,
    allow_bucket_fill: bool = True,
    allow_region_bucket_fill: bool = True,
    resume_base_bucket_key: Optional[Tuple[str, Point]] = None,
    resume_base_bucket_rgb: Optional[RGB] = None,
    bucket_base_cb: Optional[Callable[[str, int, int, int, int, int], None]] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]] = None,
) -> bool:
    """Paints a WxH pixel grid into a canvas rectangle.

    This assumes the game's canvas pixels map evenly into the selected rectangle.
    The actual mapping may need per-game tweaking; this is the first-pass.
    """

    if options is None:
        options = PainterOptions()

    x0, y0, w, h = canvas_rect
    if grid_w <= 0 or grid_h <= 0:
        return True

    if not cfg.main_colors or cfg.shades_panel_button_pos is None or cfg.back_button_pos is None:
        raise RuntimeError("Color configuration incomplete. Set up colors and global buttons first.")

    # Create MouseController if enhanced features are enabled
    mouse_ctrl: Optional["MouseController"] = _create_mouse_controller(options)
    
    # Track session start time for time limit monitoring
    import time
    session_start_time = time.time()
    
    def _check_session_time_limit() -> bool:
        """Check if session time limit has been exceeded. Returns True if should stop."""
        if mouse_ctrl and mouse_ctrl.delay_system:
            try:
                from .config import load_mouse_config
                mouse_config = load_mouse_config()
                if mouse_config.session_time_limit_hours > 0:
                    elapsed_hours = (time.time() - session_start_time) / 3600
                    if elapsed_hours >= mouse_config.session_time_limit_hours:
                        if status_cb:
                            status_cb(f"⏰ Session time limit reached ({mouse_config.session_time_limit_hours} hours)")
                        print(f"[INFO] Session time limit reached: {elapsed_hours:.2f} hours")
                        return True
            except Exception:
                pass
        return False
    
    # Combine original should_stop with session time limit check
    def _combined_should_stop() -> bool:
        """Combined stop check: user stop OR session time limit."""
        if should_stop and should_stop():
            return True
        return _check_session_time_limit()
    
    try:
        # Compute cell centers
        cell_w = w / grid_w
        cell_h = h / grid_h

        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True  # moving mouse to top-left aborts

        mode = (paint_mode or "row").strip().lower()
        if mode in {"color", "colour", "paint by color"}:
            if status_cb is not None:
                try:
                    status_cb("Painting by color…")
                except Exception:
                    pass
            return _paint_grid_by_color(
                cfg=cfg,
                canvas_rect=canvas_rect,
                grid_w=grid_w,
                grid_h=grid_h,
                get_pixel=get_pixel,
                options=options,
                skip=skip,
                allow_bucket_fill=allow_bucket_fill,
                allow_region_bucket_fill=allow_region_bucket_fill,
                resume_base_bucket_key=resume_base_bucket_key,
                resume_base_bucket_rgb=resume_base_bucket_rgb,
                bucket_base_cb=bucket_base_cb,
                progress_cb=progress_cb,
                should_stop=_combined_should_stop,
                status_cb=status_cb,
                verify_cb=verify_cb,
                mouse_controller=mouse_ctrl,
            )

        last_main: Optional[MainColor] = None
        last_shade: Optional[ShadeButton] = None
        in_shades_panel = False

        # Optional streaming verification (verify a few cells behind while painting).
        streaming = bool(getattr(cfg, "verify_streaming_enabled", False))
        lag = max(0, int(getattr(cfg, "verify_streaming_lag", 10)))
        # Clamp lag to something sensible so it doesn't appear "stuck".
        lag = min(lag, 200)
        verify_tol = int(getattr(cfg, "verify_tolerance", 35))
        verify_tol2 = max(0, verify_tol) ** 2
        verify_queue = deque()  # (x, y, main, shade)
        verify_i = 0

        def _stream_verify_flush(force: bool = False) -> None:
            nonlocal last_main, last_shade, in_shades_panel, verify_i
            if not streaming:
                return
            while verify_queue and (force or len(verify_queue) > lag):
                if should_stop and should_stop():
                    return
                x, y, main, shade = verify_queue.popleft()
                cx, cy = _cell_center(canvas_rect, grid_w, grid_h, int(x), int(y))
                verify_i += 1
                # Always update the cursor so streaming verify is visible.
                _maybe_emit_verify(verify_cb, (int(x), int(y)), verify_i, every=1)
                try:
                    actual = get_screen_pixel_rgb(cx, cy)
                except Exception:
                    continue
                if _dist2(actual, shade.rgb) <= verify_tol2:
                    continue

                # Mismatch: select the expected shade and repaint this cell.
                last_main, last_shade, in_shades_panel = _select_shade(
                    cfg=cfg,
                    options=options,
                    main=main,
                    shade=shade,
                    last_main=last_main,
                    last_shade=last_shade,
                    in_shades_panel=in_shades_panel,
                    mouse_controller=mouse_ctrl,
                )
                _tap((cx, cy), options, mouse_controller=mouse_ctrl)
                if progress_cb:
                    progress_cb(int(x), int(y))

            _maybe_emit_verify(verify_cb, None, 0, every=1)

        # Cache best-match results for repeated RGBs.
        match_cache: Dict[RGB, Optional[Tuple[MainColor, ShadeButton]]] = {}

        def get_match(rgb: RGB) -> Optional[Tuple[MainColor, ShadeButton]]:
            if rgb in match_cache:
                return match_cache[rgb]
            m = _find_best_match(rgb, cfg)
            match_cache[rgb] = m
            return m

        # Optional bucket-fill pre-pass: fill the entire canvas with the most-used shade,
        # then skip painting that shade in the per-pixel pass.
        bucket_key: Optional[Tuple[str, Point]] = None
        if allow_bucket_fill and bool(getattr(cfg, "bucket_fill_enabled", False)):
            # Build usage counts.
            counts: Dict[Tuple[str, Point], Tuple[int, MainColor, ShadeButton]] = {}
            for yy in range(grid_h):
                for xx in range(grid_w):
                    if should_stop and should_stop():
                        return False
                    if skip is not None and skip(xx, yy):
                        continue
                    m = get_match(get_pixel(xx, yy))
                    if m is None:
                        continue
                    mc, sh = m
                    k = (mc.name, sh.pos)
                    if k not in counts:
                        counts[k] = (0, mc, sh)
                    counts[k] = (counts[k][0] + 1, counts[k][1], counts[k][2])

            if counts:
                bucket_key, (bucket_n, bucket_main, bucket_shade) = max(
                    ((k, v) for (k, v) in counts.items()),
                    key=lambda kv: kv[1][0],
                )
                min_cells = max(0, int(getattr(cfg, "bucket_fill_min_cells", 50)))
                if bucket_n < min_cells:
                    bucket_key = None
                else:
                    _bucket_fill_canvas_with_shade(
                        cfg=cfg,
                        canvas_rect=canvas_rect,
                        grid_w=grid_w,
                        grid_h=grid_h,
                        main=bucket_main,
                        shade=bucket_shade,
                        options=options,
                        should_stop=should_stop,
                        mouse_controller=mouse_ctrl,
                    )
                    if should_stop and should_stop():
                        return False

                    if status_cb is not None:
                        try:
                            status_cb(f"Bucket-filled base color: {bucket_main.name}/{bucket_shade.name}")
                        except Exception:
                            pass

        for y in range(grid_h):
            if status_cb is not None:
                try:
                    status_cb(f"Painting row {y+1}/{grid_h}…")
                except Exception:
                    pass
            x = 0
            while x < grid_w:
                if should_stop and should_stop():
                    return False

                if skip is not None and skip(x, y):
                    if progress_cb:
                        progress_cb(x, y)
                    x += 1
                    continue

                rgb = get_pixel(x, y)
                match = get_match(rgb)
                if match is None:
                    x += 1
                    continue
                main, shade = match

                if bucket_key is not None and (main.name, shade.pos) == bucket_key:
                    # Already bucket-filled.
                    if progress_cb:
                        progress_cb(x, y)
                    x += 1
                    continue

                # Find run of adjacent same-shade pixels to potentially stroke.
                run_start = x
                run_end = x
                while run_end + 1 < grid_w:
                    if skip is not None and skip(run_end + 1, y):
                        break
                    nxt = get_match(get_pixel(run_end + 1, y))
                    if nxt is None:
                        break
                    nmain, nshade = nxt
                    if nmain.name != main.name or nshade.pos != shade.pos:
                        break
                    run_end += 1

                # Select main color if changed
                last_main, last_shade, in_shades_panel = _select_shade(
                    cfg=cfg,
                    options=options,
                    main=main,
                    shade=shade,
                    last_main=last_main,
                    last_shade=last_shade,
                    in_shades_panel=in_shades_panel,
                    mouse_controller=mouse_ctrl,
                )

                # Paint run
                run_len = run_end - run_start + 1
                if options.enable_drag_strokes and run_len >= 2:
                    pts: List[Point] = []
                    for xx in range(run_start, run_end + 1):
                        cx = int(x0 + (xx + 0.5) * cell_w)
                        cy = int(y0 + (y + 0.5) * cell_h)
                        pts.append((cx, cy))
                    _rapid_click_stroke(pts, options, should_stop=should_stop, mouse_controller=mouse_ctrl)
                    if progress_cb:
                        for xx in range(run_start, run_end + 1):
                            progress_cb(xx, y)
                    if streaming:
                        for xx in range(run_start, run_end + 1):
                            verify_queue.append((int(xx), int(y), main, shade))
                        _stream_verify_flush(force=False)
                else:
                    for xx in range(run_start, run_end + 1):
                        cx = int(x0 + (xx + 0.5) * cell_w)
                        cy = int(y0 + (y + 0.5) * cell_h)
                        _tap((cx, cy), options, mouse_controller=mouse_ctrl)
                        if progress_cb:
                            progress_cb(xx, y)
                        if streaming:
                            verify_queue.append((int(xx), int(y), main, shade))
                            _stream_verify_flush(force=False)

                x = run_end + 1

            if streaming:
                _stream_verify_flush(force=True)

            # Always run the bounded post-row repair pass as a final safety net.
            row_expected: List[Optional[Tuple[MainColor, ShadeButton]]] = [None] * grid_w
            for xx in range(grid_w):
                if skip is not None and skip(xx, y):
                    row_expected[xx] = None
                    continue
                m = get_match(get_pixel(xx, y))
                row_expected[xx] = m
            _verify_and_repair_row(
                    cfg=cfg,
                    canvas_rect=canvas_rect,
                    grid_w=grid_w,
                    grid_h=grid_h,
                    y=y,
                    row_expected=row_expected,
                    options=options,
                    progress_cb=progress_cb,
                    should_stop=should_stop,
                    status_cb=status_cb,
                    verify_cb=verify_cb,
                    mouse_controller=mouse_ctrl,
            )

            if options.row_delay_s > 0:
                if not _sleep_with_stop(options.row_delay_s, should_stop=should_stop):
                    return False

            # Leave the game UI in a predictable state.
            if in_shades_panel:
                _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options, mouse_controller=mouse_ctrl)

        return True
    
    finally:
        # Cleanup: close hardware mouse connection if used
        if mouse_ctrl is not None:
            try:
                mouse_ctrl.close()
            except Exception:
                pass


def _paint_grid_by_color(
    cfg: AppConfig,
    canvas_rect: Tuple[int, int, int, int],
    grid_w: int,
    grid_h: int,
    get_pixel: Callable[[int, int], RGB],
    options: PainterOptions,
    skip: Optional[Callable[[int, int], bool]] = None,
    allow_bucket_fill: bool = True,
    allow_region_bucket_fill: bool = True,
    resume_base_bucket_key: Optional[Tuple[str, Point]] = None,
    resume_base_bucket_rgb: Optional[RGB] = None,
    bucket_base_cb: Optional[Callable[[str, int, int, int, int, int], None]] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
    verify_cb: Optional[Callable[[Optional[Tuple[int, int]]], None]] = None,
    mouse_controller: Optional["MouseController"] = None,
) -> bool:
    """Paint all pixels grouped by shade.

    This minimizes palette switching by selecting a shade once and painting all
    cells that need that shade before moving to the next.
    """

    x0, y0, w, h = canvas_rect
    if grid_w <= 0 or grid_h <= 0:
        return True

    cell_w = w / grid_w
    cell_h = h / grid_h

    # Cache best-match results for repeated RGBs.
    match_cache: Dict[RGB, Optional[Tuple[MainColor, ShadeButton]]] = {}

    def get_match(rgb: RGB) -> Optional[Tuple[MainColor, ShadeButton]]:
        if rgb in match_cache:
            return match_cache[rgb]
        m = _find_best_match(rgb, cfg)
        match_cache[rgb] = m
        return m

    # Group: (main_name, shade_pos) -> (main, shade, [(x,y), ...])
    groups: Dict[Tuple[str, Point], Tuple[MainColor, ShadeButton, List[Tuple[int, int]]]] = {}

    # Preprocess all pixels first so we know what to paint per shade.
    for y in range(grid_h):
        for x in range(grid_w):
            if should_stop and should_stop():
                return False
            if skip is not None and skip(x, y):
                continue
            rgb = get_pixel(x, y)
            match = get_match(rgb)
            if match is None:
                continue
            main, shade = match
            key = (main.name, shade.pos)
            if key not in groups:
                groups[key] = (main, shade, [])
            groups[key][2].append((x, y))

    # Stable order: most-used shades first, then name/pos as tie-breaker.
    ordered = sorted(
        groups.values(),
        key=lambda t: (-len(t[2]), t[0].name, t[1].pos[0], t[1].pos[1]),
    )

    def _sample_base_rgb() -> Optional[RGB]:
        # Sample a few points inside the canvas and take per-channel median.
        try:
            x0, y0, w, h = canvas_rect
            pts = [
                (int(x0 + w * 0.50), int(y0 + h * 0.50)),
                (int(x0 + w * 0.35), int(y0 + h * 0.35)),
                (int(x0 + w * 0.65), int(y0 + h * 0.35)),
                (int(x0 + w * 0.35), int(y0 + h * 0.65)),
                (int(x0 + w * 0.65), int(y0 + h * 0.65)),
            ]
            rgbs: List[RGB] = []
            for px, py in pts:
                try:
                    rgbs.append(get_screen_pixel_rgb(int(px), int(py)))
                except Exception:
                    continue
            if not rgbs:
                return None
            rs = sorted(c[0] for c in rgbs)
            gs = sorted(c[1] for c in rgbs)
            bs = sorted(c[2] for c in rgbs)
            mid = len(rgbs) // 2
            return (int(rs[mid]), int(gs[mid]), int(bs[mid]))
        except Exception:
            return None

    # Optional bucket-fill: fill entire canvas with the most-used shade and then
    # skip painting that shade.
    bucket_key: Optional[Tuple[str, Point]] = None
    base_rgb: Optional[RGB] = None

    # Resume path: allow region fill without redoing the base bucket-fill.
    if resume_base_bucket_key is not None and resume_base_bucket_rgb is not None:
        bucket_key = resume_base_bucket_key
        base_rgb = resume_base_bucket_rgb
    if allow_bucket_fill and bool(getattr(cfg, "bucket_fill_enabled", False)) and ordered:
        main0, shade0, coords0 = ordered[0]
        min_cells = max(0, int(getattr(cfg, "bucket_fill_min_cells", 50)))
        if len(coords0) >= min_cells:
            if status_cb is not None:
                try:
                    status_cb(f"Bucket-filling base canvas: {main0.name}/{shade0.name}…")
                except Exception:
                    pass
            _bucket_fill_canvas_with_shade(
                cfg=cfg,
                canvas_rect=canvas_rect,
                grid_w=grid_w,
                grid_h=grid_h,
                main=main0,
                shade=shade0,
                options=options,
                should_stop=should_stop,
                mouse_controller=mouse_controller,
            )
            if should_stop and should_stop():
                return False
            bucket_key = (main0.name, shade0.pos)
            # Use the actual on-screen base color for region-fill outline verification.
            # Palette RGBs can differ from rendered RGBs in-game.
            base_rgb = _sample_base_rgb() or shade0.rgb
            if bucket_base_cb is not None:
                try:
                    bucket_base_cb(
                        str(main0.name),
                        int(shade0.pos[0]),
                        int(shade0.pos[1]),
                        int(base_rgb[0]),
                        int(base_rgb[1]),
                        int(base_rgb[2]),
                    )
                except Exception:
                    pass
            # Mark these pixels as complete for progress purposes.
            if progress_cb:
                for xx, yy in coords0:
                    progress_cb(xx, yy)

    if allow_region_bucket_fill and bool(getattr(cfg, "bucket_fill_regions_enabled", False)) and bucket_key is None:
        if status_cb is not None:
            try:
                status_cb("Region fill disabled (needs base bucket-fill). Lower Bucket min cells or disable region fill.")
            except Exception:
                pass

    # Optional region bucket fill (outline then fill). Only meaningful if we have a
    # base fill; otherwise bucket fill can leak into other unpainted base-colored areas.
    regions_enabled = (
        allow_region_bucket_fill
        and bucket_key is not None
        and bool(getattr(cfg, "bucket_fill_regions_enabled", False))
        and cfg.paint_tool_button_pos is not None
        and cfg.bucket_tool_button_pos is not None
    )
    regions_min_cells = max(0, int(getattr(cfg, "bucket_fill_regions_min_cells", 200)))
    disable_regions_for_rest = False

    if allow_region_bucket_fill and bool(getattr(cfg, "bucket_fill_regions_enabled", False)) and bucket_key is not None:
        if cfg.paint_tool_button_pos is None or cfg.bucket_tool_button_pos is None:
            if status_cb is not None:
                try:
                    status_cb("Region fill disabled (capture paint tool + bucket tool buttons first).")
                except Exception:
                    pass

    last_main: Optional[MainColor] = None
    last_shade: Optional[ShadeButton] = None
    in_shades_panel = False

    # Optional streaming verification for Paint-by-Color.
    streaming = bool(getattr(cfg, "verify_streaming_enabled", False))
    lag = max(0, int(getattr(cfg, "verify_streaming_lag", 10)))
    lag = min(lag, 200)
    verify_tol = int(getattr(cfg, "verify_tolerance", 35))
    verify_tol2 = max(0, verify_tol) ** 2
    verify_i = 0
    verify_settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))
    verify_settle_s = min(0.10, verify_settle_s)
    verify_max_passes = max(1, int(getattr(cfg, "verify_max_passes", 4)))

    for main, shade, coords in ordered:
        if should_stop and should_stop():
            return False
        
        # Check session time limit (from paint_grid scope)
        # This function is called from paint_grid where _check_session_time_limit is defined
        # We rely on should_stop callback to handle time limit checks gracefully

        if bucket_key is not None and (main.name, shade.pos) == bucket_key:
            continue

        # Use the unified selection logic (includes retries + UI sanity check).
        if status_cb is not None:
            try:
                status_cb(f"Selecting shade: {main.name}/{shade.name}…")
            except Exception:
                pass
        last_main, last_shade, in_shades_panel = _select_shade(
            cfg=cfg,
            options=options,
            main=main,
            shade=shade,
            last_main=last_main,
            last_shade=last_shade,
            in_shades_panel=in_shades_panel,
            mouse_controller=mouse_controller,
        )

        # If enabled, bucket-fill large connected regions by outlining first.
        # This is very fast when the canvas currently has a uniform base color.
        remaining = coords
        if regions_enabled and (not disable_regions_for_rest) and regions_min_cells > 0 and len(coords) >= regions_min_cells:
            coord_set = set(coords)

            bucketed: set[Tuple[int, int]] = set()

            comps_total = 0
            comps_small = 0
            comps_no_interior = 0
            comps_outline_fail = 0
            comps_filled = 0
            regions_total = 0
            regions_filled = 0

            while coord_set:
                if should_stop and should_stop():
                    return False
                start = next(iter(coord_set))
                stack = [start]
                comp: List[Tuple[int, int]] = []
                coord_set.remove(start)
                while stack:
                    px, py = stack.pop()
                    comp.append((px, py))
                    for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                        if (nx, ny) in coord_set:
                            coord_set.remove((nx, ny))
                            stack.append((nx, ny))

                comps_total += 1

                if len(comp) < regions_min_cells:
                    comps_small += 1
                    continue
                # Edge-touching components are allowed; the game canvas boundary
                # acts as a hard stop, and we also verify the outline before
                # bucket-filling to reduce spill risk.

                comp_set = set(comp)
                boundary: List[Tuple[int, int]] = []
                interior: Optional[Tuple[int, int]] = None
                for px, py in comp:
                    is_boundary = False
                    for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                        if (nx, ny) not in comp_set:
                            is_boundary = True
                            break
                    if is_boundary:
                        boundary.append((px, py))
                    elif interior is None:
                        interior = (px, py)

                if interior is None:
                    # No interior (thin shape) -> not worth bucket filling.
                    comps_no_interior += 1
                    continue

                # Outline boundary pixels with the target shade (paint tool).
                if status_cb is not None:
                    try:
                        status_cb(f"Region fill: outlining {len(boundary)} px, filling {len(comp)} px…")
                    except Exception:
                        pass
                # Close the shades panel before painting/verifying on the canvas.
                # Some UI layouts can overlay the canvas and cause clicks to miss.
                if in_shades_panel and cfg.back_button_pos is not None:
                    try:
                        _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
                        in_shades_panel = False
                    except Exception:
                        pass

                # For outline safety clicks, prefer slightly slower, click-only timing.
                outline_opts = PainterOptions(
                    move_duration_s=float(options.move_duration_s),
                    mouse_down_s=max(float(options.mouse_down_s), 0.02),
                    after_click_delay_s=max(float(options.after_click_delay_s), 0.02),
                    panel_open_delay_s=float(options.panel_open_delay_s),
                    shade_select_delay_s=float(options.shade_select_delay_s),
                    row_delay_s=float(options.row_delay_s),
                    enable_drag_strokes=False,
                    drag_step_duration_s=float(options.drag_step_duration_s),
                    after_drag_delay_s=float(options.after_drag_delay_s),
                )

                _tap(_click_target(cfg.paint_tool_button_pos, outline_opts, _randomize_global_button_pos), outline_opts)

                # Optional: stream-verify the outline while painting it, to reduce
                # expensive post-pass outline verification.
                outline_streaming = bool(getattr(cfg, "verify_streaming_enabled", False))
                outline_lag = max(0, int(getattr(cfg, "verify_streaming_lag", 10)))
                outline_lag = min(outline_lag, 60)
                outline_queue = deque()  # (x, y, t_painted)
                outline_verify_settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))
                outline_verify_settle_s = min(0.10, outline_verify_settle_s)

                # Local base sampler: sample a neighbor just outside the component.
                # This is much more reliable than a single global base_rgb.
                local_base_cache: Dict[Tuple[int, int], RGB] = {}

                def _local_base_rgb(px: int, py: int) -> Optional[RGB]:
                    key = (int(px), int(py))
                    if key in local_base_cache:
                        return local_base_cache[key]
                    try:
                        for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                            if (nx, ny) not in comp_set:
                                cx2, cy2 = _cell_center(canvas_rect, grid_w, grid_h, int(nx), int(ny))
                                rgb2 = get_screen_pixel_rgb(cx2, cy2)
                                if base_rgb is not None:
                                    tol = int(getattr(cfg, "verify_tolerance", 35))
                                    base_tol = max(8, int(tol * 0.5))
                                    base_tol2 = max(0, base_tol) ** 2
                                    if _dist2(rgb2, base_rgb) <= base_tol2:
                                        local_base_cache[key] = rgb2
                                        return rgb2
                                break
                    except Exception:
                        return base_rgb
                    return base_rgb

                def _outline_flush(force: bool = False, max_steps: int = 2) -> None:
                    if not outline_streaming:
                        return
                    steps = 0
                    while outline_queue and (force or len(outline_queue) > outline_lag):
                        if not force and steps >= max(1, int(max_steps)):
                            break
                        if should_stop and should_stop():
                            return
                        ox, oy, t_painted = outline_queue[0]
                        if outline_verify_settle_s > 0:
                            now = time.time()
                            ready_in = (float(t_painted) + outline_verify_settle_s) - now
                            if ready_in > 0:
                                if not force:
                                    break
                                if not _sleep_with_stop(min(0.02, ready_in), should_stop=should_stop):
                                    return
                                continue
                        ox, oy, _t = outline_queue.popleft()
                        cx, cy = _cell_center(canvas_rect, grid_w, grid_h, int(ox), int(oy))
                        try:
                            actual = get_screen_pixel_rgb(cx, cy)
                        except Exception:
                            steps += 1
                            continue
                        # Consider it bad only if it still looks like local base AND not like expected shade.
                        tol = int(getattr(cfg, "verify_tolerance", 35))
                        base_tol = max(8, int(tol * 0.5))
                        base_tol2 = max(0, base_tol) ** 2
                        tol2 = max(0, int(tol)) ** 2
                        base_ref = _local_base_rgb(int(ox), int(oy))
                        looks_like_base = False
                        if base_rgb is not None:
                            looks_like_base = looks_like_base or (_dist2(actual, base_rgb) <= base_tol2)
                        if base_ref is not None:
                            looks_like_base = looks_like_base or (_dist2(actual, base_ref) <= base_tol2)
                        looks_like_expected = _dist2(actual, shade.rgb) <= tol2
                        if looks_like_base and (not looks_like_expected):
                            _tap((cx, cy), outline_opts)
                            _tap((cx, cy), outline_opts, extra_delay_s=0.01)
                        steps += 1

                def _outline_progress(x: int, y: int) -> None:
                    if not outline_streaming:
                        return
                    outline_queue.append((int(x), int(y), time.time()))
                    backlog = len(outline_queue) - outline_lag
                    if backlog > 40:
                        step_n = 6
                    elif backlog > 20:
                        step_n = 3
                    else:
                        step_n = 1
                    _outline_flush(force=False, max_steps=step_n)

                _paint_coord_runs(
                    cfg=cfg,
                    canvas_rect=canvas_rect,
                    grid_w=grid_w,
                    grid_h=grid_h,
                    coords=boundary,
                    options=outline_opts,
                    progress_cb=_outline_progress if outline_streaming else None,
                    should_stop=should_stop,
                    mouse_controller=mouse_controller,
                )

                # Large regions can develop tiny holes. A second outline pass helps, but costs time.
                # Only do it for large regions whose shade is close to base (low contrast), since those
                # are more likely to miss/verify poorly and leak.
                do_second_outline_pass = False
                if len(comp) >= (max(1, int(regions_min_cells)) * 2):
                    if base_rgb is None:
                        do_second_outline_pass = True
                    else:
                        tol = int(getattr(cfg, "verify_tolerance", 35))
                        close_thresh = max(60, int(tol * 2))
                        try:
                            do_second_outline_pass = _dist2(shade.rgb, base_rgb) <= (close_thresh * close_thresh)
                        except Exception:
                            do_second_outline_pass = True

                if do_second_outline_pass:
                    _paint_coord_runs(
                        cfg=cfg,
                        canvas_rect=canvas_rect,
                        grid_w=grid_w,
                        grid_h=grid_h,
                        coords=boundary,
                        options=outline_opts,
                        progress_cb=_outline_progress if outline_streaming else None,
                        should_stop=should_stop,
                        mouse_controller=mouse_controller,
                    )

                if outline_streaming:
                    _outline_flush(force=True, max_steps=999999)

                # Verify the outline before bucket-fill to reduce spill risk.
                outline_ok = _verify_outline_then_repair(
                    cfg=cfg,
                    canvas_rect=canvas_rect,
                    grid_w=grid_w,
                    grid_h=grid_h,
                    outline_coords=boundary,
                    expected_rgb=shade.rgb,
                    avoid_rgb=base_rgb,
                    options=outline_opts,
                    should_stop=should_stop,
                    status_cb=status_cb,
                    verify_cb=verify_cb,
                    max_passes_override=1 if outline_streaming else None,
                    local_base_rgb=_local_base_rgb,
                    mouse_controller=mouse_controller,
                )

                # If outline didn't verify, we can still attempt a cautious fill
                # for large, high-contrast regions. We'll run quick spill checks
                # afterwards; if spill is detected, we disable further region fills.
                try:
                    contrast2 = _dist2(shade.rgb, base_rgb) if base_rgb is not None else 0
                except Exception:
                    contrast2 = 0
                allow_cautious_fill = (
                    (not outline_ok)
                    and (base_rgb is not None)
                    and (len(comp) >= max(regions_min_cells, 600))
                    and (contrast2 >= 120 * 120)
                )
                if (not outline_ok) and (not allow_cautious_fill):
                    # Can't guarantee a sealed boundary; skip bucket-fill for safety.
                    comps_outline_fail += 1
                    if status_cb is not None:
                        try:
                            status_cb("Region fill skipped (outline didn't verify)")
                        except Exception:
                            pass
                    continue
                if (not outline_ok) and allow_cautious_fill and status_cb is not None:
                    try:
                        status_cb("Outline didn't verify; attempting cautious region fill with spill checks…")
                    except Exception:
                        pass

                if should_stop and should_stop():
                    return False

                boundary_set = set(boundary)
                interior_set = set(comp_set) - boundary_set
                if not interior_set:
                    comps_no_interior += 1
                    continue

                # Find interior connected components (tight outlines can split interior
                # into multiple enclosed regions that need multiple bucket clicks).
                interior_components: List[List[Tuple[int, int]]] = []
                while interior_set:
                    seed = next(iter(interior_set))
                    stack2 = [seed]
                    interior_set.remove(seed)
                    sub: List[Tuple[int, int]] = []
                    while stack2:
                        qx, qy = stack2.pop()
                        sub.append((qx, qy))
                        for nx, ny in ((qx - 1, qy), (qx + 1, qy), (qx, qy - 1), (qx, qy + 1)):
                            if (nx, ny) in interior_set:
                                interior_set.remove((nx, ny))
                                stack2.append((nx, ny))
                    interior_components.append(sub)

                # Bucket-fill each enclosed interior subregion.
                tol = int(getattr(cfg, "verify_tolerance", 35))
                tol2 = max(0, tol) ** 2
                # Base similarity should be stricter than general verify tolerance.
                # If verify_tolerance is high, using it here can cause false "no effect"
                # results even when the bucket fill succeeded.
                base_tol = max(8, int(tol * 0.5))
                base_tol2 = max(0, base_tol) ** 2
                settle_s = max(0.0, float(getattr(cfg, "verify_settle_s", 0.05)))

                _tap(_click_target(cfg.bucket_tool_button_pos, options, _randomize_global_button_pos), options)
                filled_cells: set[Tuple[int, int]] = set(boundary)

                regions_total += len(interior_components)
                filled_any = False
                spill_detected = False
                for sub in interior_components:
                    if should_stop and should_stop():
                        return False
                    if not sub:
                        continue
                    fx, fy = sub[0]
                    _tap(_cell_center(canvas_rect, grid_w, grid_h, fx, fy), options)
                    if settle_s > 0:
                        if not _sleep_with_stop(settle_s, should_stop=should_stop):
                            return False

                    ok = True
                    # Spot-check that the click actually filled (cell should not remain base).
                    if base_rgb is not None:
                        cx, cy = _cell_center(canvas_rect, grid_w, grid_h, fx, fy)
                        actual = get_screen_pixel_rgb(cx, cy)
                        if _dist2(actual, base_rgb) <= base_tol2:
                            ok = False

                    if ok:
                        filled_any = True
                        regions_filled += 1
                        filled_cells |= set(sub)

                        if allow_cautious_fill:
                            # Spill check: sample a few neighbor cells just outside the component.
                            # If any are no longer close to base, consider it spill.
                            samples = 0
                            changed = 0
                            # Deterministic sampling: a few boundary pixels spread out.
                            stride = max(1, len(boundary) // 7)
                            for bi in range(0, len(boundary), stride):
                                if samples >= 6:
                                    break
                                bx, by = boundary[bi]
                                # Find an outside neighbor.
                                out_pt = None
                                for nx, ny in ((bx - 1, by), (bx + 1, by), (bx, by - 1), (bx, by + 1)):
                                    if (nx, ny) not in comp_set:
                                        out_pt = (nx, ny)
                                        break
                                if out_pt is None:
                                    continue
                                ox, oy = out_pt
                                cx2, cy2 = _cell_center(canvas_rect, grid_w, grid_h, int(ox), int(oy))
                                try:
                                    a2 = get_screen_pixel_rgb(cx2, cy2)
                                except Exception:
                                    continue
                                samples += 1
                                if base_rgb is not None and _dist2(a2, base_rgb) > base_tol2:
                                    changed += 1
                            if samples > 0 and changed > 0:
                                spill_detected = True
                                if status_cb is not None:
                                    try:
                                        status_cb(
                                            f"Region fill spill detected (outside changed {changed}/{samples}); disabling further region fills"
                                        )
                                    except Exception:
                                        pass
                                break

                _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options)

                if filled_any:
                    comps_filled += 1
                    bucketed |= filled_cells
                    if progress_cb:
                        for xx, yy in filled_cells:
                            progress_cb(xx, yy)
                else:
                    # Nothing filled; leave these cells for normal painting.
                    if status_cb is not None:
                        try:
                            status_cb("Region fill warning: fill click(s) had no effect; painting region normally")
                        except Exception:
                            pass
                    # Defensive: ensure we are back on the paint tool before the
                    # subsequent normal-paint pass (avoid accidentally painting
                    # with the bucket tool if the tool switch didn't register).
                    try:
                        _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options, extra_delay_s=0.02)
                    except Exception:
                        pass

                if spill_detected:
                    disable_regions_for_rest = True
                    # Don't trust subsequent region fills; leave remaining for normal painting.
                    # We also stop processing more components of this shade.
                    break

            if status_cb is not None:
                try:
                    status_cb(
                        f"Region fill summary: comps={comps_total}, filled={comps_filled}, "
                        f"skipped_small={comps_small}, skipped_thin={comps_no_interior}, skipped_outline={comps_outline_fail}"
                    )
                except Exception:
                    pass
            if status_cb is not None and regions_total > 0:
                try:
                    status_cb(f"Region fill subregions: filled={regions_filled}/{regions_total}")
                except Exception:
                    pass

            if bucketed:
                remaining = [xy for xy in coords if xy not in bucketed]
        elif regions_enabled and regions_min_cells > 0 and len(coords) < regions_min_cells:
            if status_cb is not None:
                try:
                    status_cb(f"Region fill not attempted for {main.name}/{shade.name} ({len(coords)} < {regions_min_cells})")
                except Exception:
                    pass

        # Paint remaining cells for this shade.
        # Prefer horizontal strokes across adjacent pixels (same shade).
        if status_cb is not None:
            try:
                if streaming:
                    status_cb(
                        f"Painting shade: {main.name}/{shade.name} ({len(remaining)} px) … "
                        f"[stream verify lag={lag}]"
                    )
                else:
                    status_cb(f"Painting shade: {main.name}/{shade.name} ({len(remaining)} px) …")
            except Exception:
                pass

        # Defensive: ensure the paint tool is active before doing normal pixel
        # painting. Region bucket-fill uses the bucket tool and, very rarely,
        # the switch back can fail to register, which would cause catastrophic
        # bucket-painting during the normal pass.
        try:
            if cfg.paint_tool_button_pos is not None:
                _tap(_click_target(cfg.paint_tool_button_pos, options, _randomize_global_button_pos), options, extra_delay_s=0.02)
        except Exception:
            pass

        # Streaming verify for this shade: verify a few cells behind as we paint,
        # then flush at the end of the shade.
        verify_queue = deque()  # (x, y, t_painted, repair_pass)

        def flush_verify(force: bool = False, max_steps: int = 1) -> None:
            nonlocal verify_i
            if not streaming:
                return
            steps = 0
            while verify_queue and (force or len(verify_queue) > lag):
                if not force and steps >= max(1, int(max_steps)):
                    break
                if should_stop and should_stop():
                    return
                x, y, t_painted, repair_pass = verify_queue[0]
                # Don't verify too early; let the game render the paint.
                if verify_settle_s > 0:
                    now = time.time()
                    ready_in = (float(t_painted) + verify_settle_s) - now
                    if ready_in > 0:
                        if not force:
                            break
                        # Force-flush: wait a tiny amount and keep going.
                        if not _sleep_with_stop(min(0.02, ready_in), should_stop=should_stop):
                            return
                        continue
                x, y, _t, repair_pass = verify_queue.popleft()
                cx, cy = _cell_center(canvas_rect, grid_w, grid_h, int(x), int(y))
                verify_i += 1
                _maybe_emit_verify(verify_cb, (int(x), int(y)), verify_i, every=1)
                try:
                    actual = get_screen_pixel_rgb(cx, cy)
                except Exception:
                    steps += 1
                    continue
                if _dist2(actual, shade.rgb) <= verify_tol2:
                    steps += 1
                    continue
                # Mismatch: we expect the currently-selected shade, so just tap again.
                _tap((cx, cy), options, mouse_controller=mouse_controller)
                _tap((cx, cy), options, extra_delay_s=0.01, mouse_controller=mouse_controller)
                if progress_cb:
                    progress_cb(int(x), int(y))
                if repair_pass + 1 < verify_max_passes:
                    verify_queue.append((int(x), int(y), time.time(), repair_pass + 1))
                steps += 1
            if force:
                # If this takes a while, keep the user informed in the status overlay.
                if status_cb is not None:
                    try:
                        status_cb(
                            f"Streaming verify flush: {main.name}/{shade.name} … remaining={len(verify_queue)}"
                        )
                    except Exception:
                        pass
                _maybe_emit_verify(verify_cb, None, 0, every=1)

        def progress_and_stream(x: int, y: int) -> None:
            if progress_cb:
                progress_cb(int(x), int(y))
            if streaming:
                verify_queue.append((int(x), int(y), time.time(), 0))
                backlog = len(verify_queue) - lag
                # Adaptive: if verification is falling behind, verify a bit more per paint click
                # to avoid large end-of-shade flush pauses.
                if backlog > 60:
                    steps = 6
                elif backlog > 30:
                    steps = 3
                else:
                    steps = 1
                flush_verify(force=False, max_steps=steps)

        _paint_coord_runs(
            cfg=cfg,
            canvas_rect=canvas_rect,
            grid_w=grid_w,
            grid_h=grid_h,
            coords=list(remaining),
            options=options,
            progress_cb=progress_and_stream if streaming else progress_cb,
            should_stop=should_stop,
            mouse_controller=mouse_controller,
        )
        if should_stop and should_stop():
            return False

        if streaming:
            flush_verify(force=True)
            if should_stop and should_stop():
                return False

        # Keep the post-pass even when streaming verification is enabled; this
        # catches misses caused by a delayed game render or repair click.
        _verify_and_repair_color_group(
                cfg=cfg,
                canvas_rect=canvas_rect,
                grid_w=grid_w,
                grid_h=grid_h,
                main=main,
                shade=shade,
                coords=list(remaining),
                options=options,
                progress_cb=progress_cb,
                should_stop=should_stop,
                status_cb=status_cb,
                verify_cb=verify_cb,
                mouse_controller=mouse_controller,
        )
        if should_stop and should_stop():
            return False

        # Keep UI state and our state in sync. The shades panel is typically left
        # open after selecting a shade; close it between groups so the next main
        # selection is reliable.
        if in_shades_panel:
            _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
            in_shades_panel = False
        last_main = None
        last_shade = None

        if options.row_delay_s > 0:
            if not _sleep_with_stop(options.row_delay_s, should_stop=should_stop):
                return False

    if in_shades_panel:
        _tap(_click_target(cfg.back_button_pos, options, _randomize_global_button_pos), options)
    return True
