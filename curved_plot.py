"""
curved_shapes_demo.py
Demonstrates ways to draw curved/smooth shapes in tkinter:
  1. create_polygon with smooth=True  (B-spline auto-smoothing)
  2. Rounded rect via arc point generation
  3. Cubic bezier connectors (node-graph style)
  4. Concave curves: smooth=True on a star
  5. Concave curves: inward-bowing bezier edges
  6. Concave curves: composite overlap (bite-out) technique
"""

import math
import tkinter as tk

# ── helpers ──────────────────────────────────────────────────────────────────

def arc_points(cx, cy, rx, ry, start_deg, end_deg, steps=12):
    pts = []
    for i in range(steps + 1):
        t = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


def rounded_rect_points(x, y, w, h, r, steps=10):
    pts = []
    pts += arc_points(x + r,     y + r,     r, r, 180, 270, steps)
    pts += arc_points(x + w - r, y + r,     r, r, 270, 360, steps)
    pts += arc_points(x + w - r, y + h - r, r, r,   0,  90, steps)
    pts += arc_points(x + r,     y + h - r, r, r,  90, 180, steps)
    return [coord for pt in pts for coord in pt]


def cubic_bezier_points(p0, p1, p2, p3, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.extend([x, y])
    return pts


def star_points(cx, cy, r_outer, r_inner, n=5):
    """Alternating outer/inner vertices for a star polygon."""
    pts = []
    for i in range(n):
        a_out = math.radians(-90 + i * 360 / n)
        a_in  = math.radians(-90 + (i + 0.5) * 360 / n)
        pts += [cx + r_outer * math.cos(a_out), cy + r_outer * math.sin(a_out)]
        pts += [cx + r_inner * math.cos(a_in),  cy + r_inner * math.sin(a_in)]
    return pts


def concave_edge_points(p0, p3, pull=30, steps=20):
    """
    A single cubic bezier segment that bows *inward* (concave).
    Control points are offset along the inward normal of the chord.
    Negate pull for a convex bow.
    """
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    length = math.hypot(dx, dy) or 1
    # unit normal (perpendicular, pointing "left" of direction of travel)
    nx, ny = -dy / length, dx / length
    mx, my = (p0[0] + p3[0]) / 2, (p0[1] + p3[1]) / 2
    cx_, cy_ = mx + nx * pull, my + ny * pull
    p1 = (p0[0] * 0.5 + cx_ * 0.5, p0[1] * 0.5 + cy_ * 0.5)
    p2 = (p3[0] * 0.5 + cx_ * 0.5, p3[1] * 0.5 + cy_ * 0.5)
    return cubic_bezier_points(p0, p1, p2, p3, steps)


def concave_polygon_points(*vertices, pull=30):
    """
    Build a closed polygon outline where every edge bows inward.
    vertices: sequence of (x, y) tuples.
    Returns a flat list suitable for create_polygon / create_line.
    """
    n = len(vertices)
    pts = []
    for i in range(n):
        p0 = vertices[i]
        p3 = vertices[(i + 1) % n]
        seg = concave_edge_points(p0, p3, pull=pull)
        pts.extend(seg[:-2])   # drop last point (== first of next segment)
    return pts


# ── drawing ───────────────────────────────────────────────────────────────────

def draw_demo(canvas):

    # ── Section 1: smooth=True ────────────────────────────────────────────────
    label(canvas, 40, 20, "① create_polygon  smooth=True  (B-spline)")

    raw = [100,80,  160,50,  220,90,  240,150,  180,180,  110,160,  80,120]
    canvas.create_polygon(raw, fill="", outline="#bbb", dash=(3,3))
    canvas.create_polygon(raw, smooth=True, fill="#dbeafe", outline="#3b82f6", width=2)
    for i in range(0, len(raw), 2):
        canvas.create_oval(raw[i]-3, raw[i+1]-3, raw[i]+3, raw[i+1]+3,
                           fill="#94a3b8", outline="")

    diamond = [340,55,  430,100,  430,160,  340,205,  250,160,  250,100]
    canvas.create_polygon(diamond, fill="", outline="#bbb", dash=(3,3))
    canvas.create_polygon(diamond, smooth=True, fill="#fef9c3", outline="#ca8a04", width=2)
    for i in range(0, len(diamond), 2):
        canvas.create_oval(diamond[i]-3, diamond[i+1]-3, diamond[i]+3, diamond[i+1]+3,
                           fill="#94a3b8", outline="")

    note(canvas, 260, 220, "dashed = raw points · filled = smoothed result")
    divider(canvas, 245)

    # ── Section 2: arc-generated rounded rects ────────────────────────────────
    label(canvas, 40, 260, "② Arc-generated rounded rectangles")

    for (x, y, w, h, r, fill, outline), rl in zip(
        [(60,300,130,70, 6,"#dcfce7","#16a34a"),
         (220,300,130,70,18,"#fce7f3","#db2777"),
         (380,300,100,70,35,"#ede9fe","#7c3aed")],
        ["r=6","r=18","r=35"]
    ):
        pts = rounded_rect_points(x, y, w, h, r)
        canvas.create_polygon(pts, fill=fill, outline=outline, width=2)
        canvas.create_text(x+w//2, y+h//2, text=rl, fill=outline,
                           font=("Helvetica", 11, "bold"))

    note(canvas, 260, 390, "same helper, different corner radii")
    divider(canvas, 405)

    # ── Section 3: cubic bezier connectors ───────────────────────────────────
    label(canvas, 40, 418, "③ Cubic bezier connectors")

    def node_box(x, y, text, fill, outline):
        pts = rounded_rect_points(x, y, 110, 44, 10)
        canvas.create_polygon(pts, fill=fill, outline=outline, width=2)
        canvas.create_text(x+55, y+22, text=text, fill=outline,
                           font=("Helvetica", 10, "bold"))
        return (x+110, y+22), (x, y+22)

    r_a, _ = node_box( 60, 455, "AND gate", "#dbeafe", "#1d4ed8")
    r_b, _ = node_box( 60, 520, "OR gate",  "#dcfce7", "#15803d")
    _, l_c  = node_box(330, 487, "Output",   "#fef9c3", "#a16207")

    def bezier_edge(src, dst, color):
        dx = abs(dst[0]-src[0]) * 0.5
        pts = cubic_bezier_points(src, (src[0]+dx, src[1]),
                                       (dst[0]-dx, dst[1]), dst)
        canvas.create_line(pts, fill=color, width=2)
        canvas.create_oval(dst[0]-4, dst[1]-4, dst[0]+4, dst[1]+4,
                           fill=color, outline="")

    bezier_edge(r_a, l_c, "#1d4ed8")
    bezier_edge(r_b, l_c, "#15803d")

    note(canvas, 260, 590, "control points offset horizontally → natural S-curve")
    divider(canvas, 605)

    # ── Section 4: concave — smooth=True on a star ───────────────────────────
    label(canvas, 40, 618, "④ Concave: smooth=True on a star")

    # sharp star (reference)
    sp = star_points(120, 690, 55, 22, 5)
    canvas.create_polygon(sp, fill="", outline="#bbb", dash=(3,3))

    # smoothed → concave valleys curve inward naturally
    canvas.create_polygon(sp, smooth=True, fill="#fef9c3", outline="#ca8a04", width=2)
    canvas.create_text(120, 690, text="smooth", fill="#a16207",
                       font=("Helvetica", 9))

    # more points = more dramatic concavity
    sp6 = star_points(270, 690, 55, 15, 6)
    canvas.create_polygon(sp6, smooth=True, fill="#fce7f3", outline="#db2777", width=2)
    canvas.create_text(270, 690, text="6-pt", fill="#9d174d",
                       font=("Helvetica", 9))

    # inner radius ratio controls depth of concavity
    sp_deep = star_points(420, 690, 55, 8, 5)
    canvas.create_polygon(sp_deep, smooth=True, fill="#ede9fe", outline="#7c3aed", width=2)
    canvas.create_text(420, 690, text="deep", fill="#5b21b6",
                       font=("Helvetica", 9))

    note(canvas, 270, 760, "inner radius controls concavity depth")
    divider(canvas, 775)

    # ── Section 5: concave — inward-bowing bezier edges ──────────────────────
    label(canvas, 40, 788, "⑤ Concave: inward-bowing bezier edges")

    # triangle with all edges bowing inward
    tri = [(270, 810), (370, 960), (170, 960)]
    pts = concave_polygon_points(*tri, pull=35)
    canvas.create_polygon(tri, fill="", outline="#bbb", dash=(3,3))
    canvas.create_polygon(pts, fill="#dbeafe", outline="#3b82f6", width=2)
    canvas.create_text(270, 895, text="all edges\nconcave", fill="#1d4ed8",
                       font=("Helvetica", 9), justify="center")

    # mix: some edges convex, some concave
    quad = [(420, 815), (510, 850), (510, 950), (420, 970)]
    mixed_pts = []
    for i, (p0, p3, pull) in enumerate([
        (quad[0], quad[1], -25),   # top: convex bow
        (quad[1], quad[2],  30),   # right: concave
        (quad[2], quad[3], -25),   # bottom: convex
        (quad[3], quad[0],  30),   # left: concave
    ]):
        seg = concave_edge_points(p0, p3, pull=pull)
        mixed_pts.extend(seg[:-2])
    canvas.create_polygon(mixed_pts, fill="#dcfce7", outline="#16a34a", width=2)
    canvas.create_text(465, 892, text="mixed\nconvex+concave", fill="#15803d",
                       font=("Helvetica", 9), justify="center")

    note(canvas, 270, 985, "pull > 0 = inward · pull < 0 = outward · mix per edge")
    divider(canvas, 1000)

    # ── Section 6: composite overlap (bite-out) ───────────────────────────────
    label(canvas, 40, 1013, "⑥ Concave: composite overlap (bite-out)")

    BG = "#f8fafc"   # must match canvas background

    # speech bubble: rounded rect + triangle notch bitten out
    bx, by, bw, bh = 60, 1040, 200, 90
    pts = rounded_rect_points(bx, by, bw, bh, 12)
    canvas.create_polygon(pts, fill="#dbeafe", outline="#3b82f6", width=2)
    # notch: upward triangle at bottom-left, smoothed into a curved cutout
    notch = [bx+30, by+bh,  bx+55, by+bh-22,  bx+80, by+bh]
    canvas.create_polygon(notch, smooth=True, fill=BG, outline=BG, width=3)
    canvas.create_text(bx+bw//2, by+bh//2-5, text="speech bubble",
                       fill="#1d4ed8", font=("Helvetica", 10))

    # tab shape: rect with a curved bite out of the bottom centre
    tx, ty, tw, th = 310, 1040, 180, 90
    pts2 = rounded_rect_points(tx, ty, tw, th, 10)
    canvas.create_polygon(pts2, fill="#fce7f3", outline="#db2777", width=2)
    bite = [tx+50, ty+th,  tx+tw//2, ty+th-30,  tx+tw-50, ty+th]
    canvas.create_polygon(bite, smooth=True, fill=BG, outline=BG, width=3)
    canvas.create_text(tx+tw//2, ty+th//2-10, text="tab cutout",
                       fill="#db2777", font=("Helvetica", 10))

    note(canvas, 270, 1155, "base shape + filled overlay in bg colour = instant concavity")


# ── layout helpers ────────────────────────────────────────────────────────────

def label(canvas, x, y, text):
    canvas.create_text(x, y, text=text, anchor="w",
                       font=("Helvetica", 12, "bold"), fill="#1e293b")

def note(canvas, x, y, text):
    canvas.create_text(x, y, text=text, anchor="center",
                       font=("Helvetica", 9), fill="#64748b")

def divider(canvas, y, W=540):
    canvas.create_line(30, y, W-30, y, fill="#e2e8f0", width=1)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title("Tkinter Curved Shapes Demo")
    root.resizable(False, False)

    W, H = 540, 1180
    canvas = tk.Canvas(root, width=W, height=H, bg="#f8fafc",
                       highlightthickness=0)

    # scrollable if screen is small
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set, scrollregion=(0, 0, W, H))
    canvas.pack(side="left", padx=(12,0), pady=12)
    vsb.pack(side="left", fill="y", pady=12, padx=(0,8))

    # mousewheel scroll
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    canvas.bind_all("<Button-4>",
                    lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>",
                    lambda e: canvas.yview_scroll( 1, "units"))

    root.update_idletasks()
    draw_demo(canvas)
    root.mainloop()


if __name__ == "__main__":
    main()