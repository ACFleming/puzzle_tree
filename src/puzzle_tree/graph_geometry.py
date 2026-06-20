import math
# ── Module-level geometry helpers ─────────────────────────────────────────────
# Pure functions with no state — kept outside the class for clarity.

def _point_to_segment_dist(px, py, ax, ay, bx, by) -> float:
    """Return the shortest distance from point (px, py) to the line segment
    from (ax, ay) to (bx, by)."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        # Degenerate segment — treat as a single point
        return math.hypot(px - ax, py - ay)
    # Parameter t of the closest point on the infinite line, clamped to [0, 1]
    t = max(0.0, min(1.0,
            ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _rect_edge_point(cx, cy, w, h, angle) -> tuple:
    """Return the point on the boundary of an axis-aligned rectangle centred
    at (cx, cy) with size (w x h) in the direction given by angle (radians).

    FIX: replaces the old uniform-radius approach that caused arrow endpoints
    to overshoot node corners. This uses per-axis half-extents for a proper
    rectangular intersection, so arrows always touch the box edge cleanly.
    """
    half_w, half_h = w / 2.0, h / 2.0
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Handle perfectly horizontal or vertical arrows to avoid division by zero
    if abs(cos_a) < 1e-9:
        return cx, cy + math.copysign(half_h, sin_a)
    if abs(sin_a) < 1e-9:
        return cx + math.copysign(half_w, cos_a), cy

    # Find the scale factor t for each axis and take the minimum (first hit)
    t_x = half_w / abs(cos_a)
    t_y = half_h / abs(sin_a)
    t = min(t_x, t_y)
    return cx + cos_a * t, cy + sin_a * t
