import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heartopia_painter.delays import random_click_delay, random_click_hold
from heartopia_painter.paint import interpolate_points


def test_click_timing_ranges():
    assert all(0.03 <= random_click_hold() <= 0.05 for _ in range(200))
    assert all(0.15 <= random_click_delay() <= 0.23 for _ in range(200))


def test_interpolation_includes_endpoint_and_is_monotonic():
    points = interpolate_points((0, 10), (100, 50), 10)
    assert len(points) == 10
    assert points[-1] == (100, 50)
    assert all(a[0] <= b[0] and a[1] <= b[1] for a, b in zip(points, points[1:]))
