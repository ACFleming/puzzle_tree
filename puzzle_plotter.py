"""
Puzzle Component Plotter
========================
A desktop app to map out puzzle game components and their directional
connections (edges). Built with Python's built-in tkinter — no third-party
dependencies required.

Controls
--------
  Left-click node     Select it
  Drag node           Move it around the canvas
  C (with selection)  Enter connect mode, then click a target node
  Double-click node   Edit its label
  Double-click edge   Delete that edge
  Right-click node    Context menu (edit / connect / change type / delete)
  Delete key          Delete the selected node
  Ctrl+Z              Undo the last action
  Ctrl+S              Save (overwrites current file; prompts if unsaved)
  Ctrl+Shift+S        Save As (always prompts for a new path)
  Escape              Cancel connect mode

File management
---------------
  The title bar shows the current filename and a '*' when there are unsaved
  changes.  Closing or loading over an unsaved map prompts for confirmation.
  The last 5 opened/saved files are remembered in a small config file stored
  next to the script and accessible via File → Open Recent.
"""

import json
import math
import os
import random                                        
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
# FIX: removed unused 'colorchooser' import

# ── Node type definitions ─────────────────────────────────────────────────────
# Each entry defines the display label, fill colour, and text colour for that
# category of puzzle component.
NODE_TYPES = {
    "start":  {"label": "Start",        "color": "#185FA5", "text": "#ffffff"},
    "clue":   {"label": "Clue",         "color": "#BA7517", "text": "#ffffff"},
    "puzzle": {"label": "Puzzle piece", "color": "#534AB7", "text": "#ffffff"},
    "key":    {"label": "Key / unlock", "color": "#0F6E56", "text": "#ffffff"},
    "goal":   {"label": "Goal",         "color": "#993C1D", "text": "#ffffff"},
}

# ── Layout constants ──────────────────────────────────────────────────────────
NODE_W = 140          # Width of each node rectangle in canvas pixels
NODE_H = 52           # Height of each node rectangle in canvas pixels
SHADOW_OFFSET = 3     # Pixel offset for the drop-shadow rectangle
EDGE_HIT_RADIUS = 8   # Distance in pixels within which a click registers on an edge
DRAG_THRESHOLD = 3    # Min pixel movement before a click is treated as a drag

# Visual colours used across the app
COLOR_BG       = "#f1efe8"   # App background / sidebar
COLOR_PANEL    = "#d3d1c7"   # Toolbar buttons, status bar
COLOR_DIVIDER  = "#b4b2a9"   # Separator lines
COLOR_SHADOW   = "#b4b2a9"   # Node drop-shadow
COLOR_EDGE     = "#888780"   # Default arrow colour
COLOR_EDGE_HOV = "#534AB7"   # Arrow colour when hovered
COLOR_SEL_OUT  = "#2C2C2A"   # Node outline when selected
COLOR_CONN_OUT = "#0F6E56"   # Node outline when in connect-source mode
COLOR_TIP_FG   = "#5f5e5a"   # Sidebar tip text

# ── Recent-files config ───────────────────────────────────────────────────────
# Stored as a small JSON file next to the script so it persists between runs.
RECENT_FILE_LIMIT = 5
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           ".puzzle_plotter_config.json")


class PuzzlePlotter(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Puzzle Component Plotter")
        self.geometry("1100x700")
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)

        # ── Data model ────────────────────────────────────────────────────────
        self.nodes: dict = {}   # nid -> {id, type, label, x, y}
        self.edges: list = []   # list of (from_nid, to_nid)
        self.node_count: int = 0  # monotonically increasing id counter

        # ── Interaction state ─────────────────────────────────────────────────
        self.selected = None          # currently selected node id
        self.connecting_from = None   # node id we're drawing an edge from
        self.drag_data: dict = {}     # active drag state (see on_canvas_click)
        self.hover_edge = None        # FIX: now actually used to highlight edges

        # ── Undo stack ────────────────────────────────────────────────────────
        # Each entry is a snapshot: (nodes_copy, edges_copy).  We push before
        # every mutating action so Ctrl+Z can restore the previous state.
        self._undo_stack: list = []

        # ── File state ────────────────────────────────────────────────────────
        # _current_file  – absolute path of the file currently open, or None
        # _unsaved       – True when the canvas has changes not yet written to disk
        self._current_file: str | None = None
        self._unsaved: bool = False

        self._build_ui()
        self._seed_example()

        # Intercept the window-close button so we can warn about unsaved work
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Undo helpers ──────────────────────────────────────────────────────────

    def _push_undo(self):
        """Snapshot the current nodes and edges onto the undo stack."""
        import copy
        self._undo_stack.append((
            copy.deepcopy(self.nodes),
            list(self.edges),
        ))
        # Keep the stack from growing without bound
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        # Any mutation makes the map "dirty" (unsaved changes)
        self._mark_unsaved()

    def undo(self, event=None):
        """Restore the previous snapshot from the undo stack."""
        if not self._undo_stack:
            self.set_status("Nothing to undo.")
            return
        self.nodes, self.edges = self._undo_stack.pop()
        # Clear interaction state so nothing is left pointing at a deleted node
        self.selected = None
        self.connecting_from = None
        self.drag_data = {}
        self.hover_edge = None
        self.redraw()
        self._mark_unsaved()
        self.set_status("Undo.")

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construct all widgets. Called once during __init__."""

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=COLOR_BG, pady=6, padx=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(toolbar, text="Add node:", bg=COLOR_BG,
                 font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(0, 8))

        # One coloured button per node type
        for ntype, cfg in NODE_TYPES.items():
            tk.Button(
                toolbar, text=cfg["label"],
                bg=cfg["color"], fg=cfg["text"],
                activebackground=cfg["color"], activeforeground=cfg["text"],
                font=("Helvetica", 10), relief="flat", padx=10, pady=4,
                cursor="hand2",
                command=lambda t=ntype: self.add_node(t)
            ).pack(side=tk.LEFT, padx=4)

        # Flexible spacer pushes file buttons to the right
        tk.Frame(toolbar, bg=COLOR_BG).pack(side=tk.LEFT, expand=True, fill=tk.X)

        for text, cmd in [("↩ Undo",  self.undo),
                          ("🗑 Clear", self.clear_all)]:
            tk.Button(toolbar, text=text, font=("Helvetica", 10),
                      relief="flat", padx=8, pady=4, bg=COLOR_PANEL,
                      cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=4)

        # ── Menu bar ──────────────────────────────────────────────────────────
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New",           accelerator="Ctrl+N",
                              command=self.new_map)
        file_menu.add_command(label="Open…",         accelerator="Ctrl+O",
                              command=self.load_map)
        file_menu.add_command(label="Save",          accelerator="Ctrl+S",
                              command=self.save_map)
        file_menu.add_command(label="Save As…",      accelerator="Ctrl+Shift+S",
                              command=self.save_map_as)
        file_menu.add_separator()

        # Recent files submenu — rebuilt every time File is posted
        self._recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self._recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q",
                              command=self._on_close)

        # Populate recent files now (and again whenever the menu is opened)
        file_menu.bind("<<MenuSelect>>", lambda e: self._rebuild_recent_menu())
        self._rebuild_recent_menu()

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Click a node to select it. Drag to move.")
        tk.Label(self, textvariable=self.status_var, bg=COLOR_PANEL,
                 anchor="w", padx=10, font=("Helvetica", 10),
                 fg="#444441").pack(side=tk.BOTTOM, fill=tk.X)

        # ── Sidebar ───────────────────────────────────────────────────────────
        # Pack the sidebar BEFORE the canvas so it has priority when resizing.
        sidebar = tk.Frame(self, bg=COLOR_BG, width=200, padx=12, pady=12)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar.pack_propagate(False)   # prevent children from resizing the frame

        tk.Label(sidebar, text="Legend", bg=COLOR_BG,
                 font=("Helvetica", 12, "bold"), anchor="w").pack(fill=tk.X)
        tk.Frame(sidebar, bg=COLOR_DIVIDER, height=1).pack(fill=tk.X, pady=6)

        for cfg in NODE_TYPES.values():
            row = tk.Frame(sidebar, bg=COLOR_BG)
            row.pack(fill=tk.X, pady=2)
            # Coloured dot
            dot = tk.Canvas(row, width=14, height=14, bg=COLOR_BG,
                            highlightthickness=0)
            dot.pack(side=tk.LEFT, padx=(0, 6))
            dot.create_oval(2, 2, 12, 12, fill=cfg["color"], outline="")
            tk.Label(row, text=cfg["label"], bg=COLOR_BG,
                     font=("Helvetica", 10), anchor="w").pack(side=tk.LEFT)

        tk.Frame(sidebar, bg=COLOR_DIVIDER, height=1).pack(fill=tk.X, pady=12)
        tk.Label(sidebar, text="Tips", bg=COLOR_BG,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(fill=tk.X)

        tips = [
            "• Click node → select",
            "• Drag node → move",
            "• Select → press C → click target to connect",
            "• Double-click edge → delete it",
            "• Double-click node → edit label",
            "• Right-click node → options",
            "• Ctrl+Z → undo",
            "• Ctrl+S → save",
            "• Ctrl+Shift+S → save as",
        ]
        for tip in tips:
            tk.Label(sidebar, text=tip, bg=COLOR_BG, font=("Helvetica", 9),
                     anchor="w", justify="left", wraplength=175,
                     fg=COLOR_TIP_FG).pack(fill=tk.X, pady=1)

        # ── Canvas ────────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(self, bg="#ffffff", cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mouse bindings on the canvas
        self.canvas.bind("<ButtonPress-1>",   self.on_canvas_click)
        self.canvas.bind("<B1-Motion>",       self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-3>",        self.on_right_click)
        self.canvas.bind("<Motion>",          self.on_motion)
        self.canvas.bind("<Configure>",       lambda e: self.redraw())

        # Keyboard bindings on the root window so they work regardless of focus
        self.bind("<KeyPress-c>",      self.start_connect_key)
        self.bind("<Escape>",          self.cancel_connect)
        self.bind("<Delete>",          self.delete_selected)
        self.bind("<Control-z>",       self.undo)
        self.bind("<Control-s>",       self.save_map)
        self.bind("<Control-S>",       self.save_map_as)   # Ctrl+Shift+S
        self.bind("<Control-o>",       lambda e: self.load_map())
        self.bind("<Control-n>",       lambda e: self.new_map())
        self.bind("<Control-q>",       lambda e: self._on_close())

    # ── Node management ───────────────────────────────────────────────────────

    def add_node(self, ntype: str):
        """Prompt the user for a label and add a new node of the given type."""
        label = simpledialog.askstring(
            "New node",
            f"Label for this {NODE_TYPES[ntype]['label']}:",
            initialvalue=f"{NODE_TYPES[ntype]['label']} {self.node_count + 1}",
            parent=self
        )
        if not label:
            return   # user cancelled the dialog

        self._push_undo()
        self.node_count += 1
        nid = f"n{self.node_count}"

        # Place the new node near the canvas centre with a small random offset
        # so multiple adds don't stack on top of each other.
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 550
        x = cw // 2 + random.randint(-150, 150)
        y = ch // 2 + random.randint(-100, 100)

        self.nodes[nid] = {"id": nid, "type": ntype, "label": label,
                           "x": x, "y": y}
        self.redraw()
        self.set_status(f"Added '{label}'. Select it and press C to connect.")

    def delete_node(self, nid: str):
        """Remove a node and all edges that reference it."""
        self._push_undo()
        self.nodes.pop(nid, None)
        self.edges = [e for e in self.edges if e[0] != nid and e[1] != nid]
        if self.selected == nid:
            self.selected = None
        if self.connecting_from == nid:
            self.connecting_from = None
        self.redraw()

    def edit_node(self, nid: str):
        """Open a dialog to rename a node."""
        n = self.nodes[nid]
        label = simpledialog.askstring("Edit label", "New label:",
                                       initialvalue=n["label"], parent=self)
        if label:
            self._push_undo()
            n["label"] = label
            self.redraw()

    def change_type(self, nid: str):
        """Open a small popup to reassign the type of a node."""
        win = tk.Toplevel(self)
        win.title("Change type")
        # FIX: height is now calculated from the number of types so it never clips
        win.geometry(f"200x{40 * len(NODE_TYPES) + 60}")
        win.configure(bg=COLOR_BG)
        win.resizable(False, False)
        win.grab_set()   # make it modal

        tk.Label(win, text="Choose type:", bg=COLOR_BG,
                 font=("Helvetica", 11)).pack(pady=8)

        for ntype, cfg in NODE_TYPES.items():
            def pick(t=ntype):
                self._push_undo()
                self.nodes[nid]["type"] = t
                self.redraw()
                win.destroy()

            tk.Button(win, text=cfg["label"], bg=cfg["color"], fg=cfg["text"],
                      font=("Helvetica", 10), relief="flat", padx=8, pady=4,
                      cursor="hand2", command=pick).pack(fill=tk.X, padx=16, pady=2)

    # ── Edge management ───────────────────────────────────────────────────────

    def add_edge(self, from_id: str, to_id: str):
        """Add a directed edge if it doesn't already exist."""
        if from_id == to_id:
            return  # no self-loops
        if (from_id, to_id) not in self.edges:
            self._push_undo()
            self.edges.append((from_id, to_id))

    def delete_edge_at(self, x: float, y: float) -> bool:
        """Delete the first edge whose drawn line passes within EDGE_HIT_RADIUS
        of the point (x, y). Returns True if an edge was deleted."""
        for edge in list(self.edges):
            a = self.nodes.get(edge[0])
            b = self.nodes.get(edge[1])
            if not a or not b:
                continue
            dist = _point_to_segment_dist(x, y, a["x"], a["y"], b["x"], b["y"])
            if dist < EDGE_HIT_RADIUS:
                self._push_undo()
                self.edges.remove(edge)
                self.redraw()
                return True
        return False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def redraw(self):
        """Clear and fully repaint the canvas."""
        self.canvas.delete("all")
        self._draw_edges()
        for nid in self.nodes:
            self._draw_node(nid)

    def _draw_edges(self):
        """Draw all directed edges as arrows between node boundaries."""
        for from_id, to_id in self.edges:
            a = self.nodes.get(from_id)
            b = self.nodes.get(to_id)
            if not a or not b:
                continue

            ax, ay = a["x"], a["y"]
            bx, by = b["x"], b["y"]
            angle = math.atan2(by - ay, bx - ax)

            # FIX: use proper per-axis rectangular intersection so arrows meet
            # the node boundary cleanly at all angles, not just at corners.
            x1, y1 = _rect_edge_point(ax, ay, NODE_W, NODE_H, angle)
            x2, y2 = _rect_edge_point(bx, by, NODE_W, NODE_H, angle + math.pi)

            # FIX: hover_edge is now checked here to draw a highlighted arrow
            is_hovered = (self.hover_edge == (from_id, to_id))
            color = COLOR_EDGE_HOV if is_hovered else COLOR_EDGE
            width = 3 if is_hovered else 2

            self.canvas.create_line(
                x1, y1, x2, y2,
                arrow=tk.LAST, arrowshape=(12, 14, 5),
                fill=color, width=width, smooth=True,
                tags=(f"edge_{from_id}_{to_id}", "edge")
            )

    def _draw_node(self, nid: str):
        """Draw a single node: shadow rectangle, filled rectangle, and text."""
        n = self.nodes[nid]
        cfg = NODE_TYPES[n["type"]]
        x, y = n["x"], n["y"]
        x0, y0 = x - NODE_W // 2, y - NODE_H // 2
        x1, y1 = x + NODE_W // 2, y + NODE_H // 2

        is_selected   = (self.selected == nid)
        is_connecting = (self.connecting_from == nid)

        # Drop shadow (drawn first so it sits behind the node)
        self.canvas.create_rectangle(
            x0 + SHADOW_OFFSET, y0 + SHADOW_OFFSET,
            x1 + SHADOW_OFFSET, y1 + SHADOW_OFFSET,
            fill=COLOR_SHADOW, outline="", tags=nid
        )

        # Main node rectangle; outline and border width change based on state
        if is_selected:
            outline, border = COLOR_SEL_OUT, 3
        elif is_connecting:
            outline, border = COLOR_CONN_OUT, 3
        else:
            outline, border = cfg["color"], 1.5

        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=cfg["color"], outline=outline, width=border,
            tags=nid
        )

        # Small type label near the top of the node
        self.canvas.create_text(
            x, y - 10,
            text=cfg["label"].upper(),
            font=("Helvetica", 8), fill="#ffffff", tags=nid
        )

        # Main label, centred, wraps if the text is too long for the node width
        self.canvas.create_text(
            x, y + 8,
            text=n["label"],
            font=("Helvetica", 11, "bold"), fill="#ffffff",
            width=NODE_W - 16, tags=nid
        )

        # Hint text below the node while it is the active connect source
        if is_connecting:
            self.canvas.create_text(
                x, y1 + 14, text="▶ click a target",
                font=("Helvetica", 8, "italic"), fill=COLOR_CONN_OUT, tags=nid
            )

    # ── Interaction ───────────────────────────────────────────────────────────

    def _node_at(self, x: float, y: float):
        """Return the id of the topmost node under canvas point (x, y), or None.
        Iterates in reverse insertion order so nodes drawn later (on top) are
        hit-tested first."""
        for nid in reversed(list(self.nodes)):
            n = self.nodes[nid]
            if abs(x - n["x"]) <= NODE_W // 2 and abs(y - n["y"]) <= NODE_H // 2:
                return nid
        return None

    def on_canvas_click(self, event):
        """Handle left mouse button press on the canvas."""
        x, y = event.x, event.y
        nid = self._node_at(x, y)

        # ── Connect mode: finish the edge ────────────────────────────────────
        if self.connecting_from:
            if nid and nid != self.connecting_from:
                self.add_edge(self.connecting_from, nid)
                src = self.nodes[self.connecting_from]["label"]
                dst = self.nodes[nid]["label"]
                self.set_status(f"Connected '{src}' → '{dst}'.")
            else:
                self.set_status("Connect cancelled — click a different node.")
            self.connecting_from = None
            self.selected = nid
            self.redraw()
            return

        # ── Normal click: select node or deselect ────────────────────────────
        if nid:
            self.selected = nid
            # Capture the original position so dragging computes an absolute
            # delta rather than accumulating floating-point drift each event.
            self.drag_data = {
                "id": nid,
                "sx": x, "sy": y,
                "ox": self.nodes[nid]["x"],
                "oy": self.nodes[nid]["y"],
                "moved": False,
            }
            self.set_status(
                f"Selected '{self.nodes[nid]['label']}'. "
                "Press C to connect, Delete to remove."
            )
        else:
            self.selected = None
            self.drag_data = {}
            self.set_status("Click a node to select it. Drag to move.")

        self.redraw()

    def on_drag(self, event):
        """Move the currently dragged node, clamped to the canvas bounds."""
        if not self.drag_data:
            return

        nid = self.drag_data["id"]
        dx = event.x - self.drag_data["sx"]
        dy = event.y - self.drag_data["sy"]

        # Only mark as a genuine drag once the pointer moves a few pixels,
        # so small wobbles during a click don't suppress selection logic.
        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
            self.drag_data["moved"] = True

        # FIX: clamp to canvas bounds so nodes can't be dragged off-screen
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        half_w, half_h = NODE_W // 2, NODE_H // 2
        new_x = max(half_w, min(cw - half_w, self.drag_data["ox"] + dx))
        new_y = max(half_h, min(ch - half_h, self.drag_data["oy"] + dy))

        self.nodes[nid]["x"] = new_x
        self.nodes[nid]["y"] = new_y
        self.redraw()

    def on_release(self, event):
        """Clear drag state when the mouse button is released."""
        self.drag_data = {}

    def on_double_click(self, event):
        """Double-clicking a node opens the edit dialog; double-clicking on
        empty space tries to delete an edge under the cursor."""
        x, y = event.x, event.y
        nid = self._node_at(x, y)
        if nid:
            self.edit_node(nid)
        else:
            deleted = self.delete_edge_at(x, y)
            if deleted:
                self.set_status("Edge deleted.")

    def on_right_click(self, event):
        """Show a context menu for the node under the cursor."""
        x, y = event.x, event.y
        nid = self._node_at(x, y)
        if not nid:
            return

        self.selected = nid
        self.redraw()

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏  Edit label",
                         command=lambda: self.edit_node(nid))
        menu.add_command(label="🔗 Connect to…",
                         command=lambda: self.start_connect(nid))
        menu.add_command(label="🎨 Change type",
                         command=lambda: self.change_type(nid))
        menu.add_separator()
        menu.add_command(label="🗑 Delete node",
                         command=lambda: self.delete_node(nid))
        menu.tk_popup(event.x_root, event.y_root)

    def on_motion(self, event):
        """Update the cursor and hover_edge highlight as the mouse moves.
        FIX: hover_edge is now set/cleared here and used in _draw_edges()."""
        x, y = event.x, event.y

        for edge in self.edges:
            a = self.nodes.get(edge[0])
            b = self.nodes.get(edge[1])
            if not a or not b:
                continue
            dist = _point_to_segment_dist(x, y, a["x"], a["y"], b["x"], b["y"])
            if dist < EDGE_HIT_RADIUS:
                if self.hover_edge != edge:
                    self.hover_edge = edge
                    self.canvas.configure(cursor="X_cursor")
                    self.redraw()   # repaint so the highlighted edge shows
                return

        # No edge nearby — clear hover state if it was previously set
        if self.hover_edge is not None:
            self.hover_edge = None
            self.canvas.configure(cursor="crosshair")
            self.redraw()

    def start_connect_key(self, event=None):
        """Keyboard shortcut (C) — enter connect mode for the selected node."""
        if self.selected:
            self.start_connect(self.selected)

    def start_connect(self, nid: str):
        """Enter connect mode: the next node the user clicks will be linked from nid."""
        self.connecting_from = nid
        label = self.nodes[nid]["label"]
        self.set_status(
            f"Connect mode: click a target node to link from '{label}'. "
            "Press Esc to cancel."
        )
        self.redraw()

    def cancel_connect(self, event=None):
        """Exit connect mode without creating an edge."""
        if self.connecting_from:
            self.connecting_from = None
            self.set_status("Connect mode cancelled.")
            self.redraw()

    def delete_selected(self, event=None):
        """Delete the currently selected node (bound to the Delete key)."""
        if self.selected:
            name = self.nodes[self.selected]["label"]
            self.delete_node(self.selected)
            self.set_status(f"Deleted '{name}'.")

    def set_status(self, msg: str):
        """Update the status bar text."""
        self.status_var.set(msg)

    # ── File state helpers ────────────────────────────────────────────────────

    def _mark_unsaved(self):
        """Flag the map as having unsaved changes and update the title bar."""
        self._unsaved = True
        self._update_title()

    def _mark_saved(self, path: str):
        """Record that the map was just saved to 'path' and update the title."""
        self._current_file = path
        self._unsaved = False
        self._update_title()
        self._add_recent(path)

    def _update_title(self):
        """Reflect the current filename and dirty state in the window title."""
        if self._current_file:
            name = os.path.basename(self._current_file)
        else:
            name = "Untitled"
        dirty = " *" if self._unsaved else ""
        self.title(f"Puzzle Component Plotter — {name}{dirty}")

    def _confirm_discard(self) -> bool:
        """Return True if it's safe to discard the current map.

        If there are no unsaved changes, returns True immediately.
        Otherwise asks the user; returns True only if they confirm.
        """
        if not self._unsaved:
            return True
        answer = messagebox.askyesnocancel(
            "Unsaved changes",
            "You have unsaved changes. Save before continuing?",
            parent=self,
        )
        if answer is None:        # Cancel — abort the operation
            return False
        if answer:                # Yes — save first, then proceed
            if not self._do_save(self._current_file):
                return False      # save was cancelled or failed
        return True               # No — discard and continue

    def _on_close(self):
        """Handle the window-close button with an unsaved-changes guard."""
        if self._confirm_discard():
            self.destroy()

    # ── Recent-files helpers ──────────────────────────────────────────────────

    def _load_config(self) -> dict:
        """Read the config file from disk, returning {} on any error."""
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_config(self, cfg: dict):
        """Write the config dict to disk, silently ignoring errors."""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except OSError:
            pass

    def _add_recent(self, path: str):
        """Prepend path to the recent-files list and persist it."""
        cfg = self._load_config()
        recent: list = cfg.get("recent_files", [])
        # Remove duplicates then insert at the front
        recent = [p for p in recent if p != path]
        recent.insert(0, path)
        cfg["recent_files"] = recent[:RECENT_FILE_LIMIT]
        self._save_config(cfg)
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        """Repopulate the Open Recent submenu from the config file."""
        self._recent_menu.delete(0, "end")
        cfg = self._load_config()
        recent: list = cfg.get("recent_files", [])
        # Filter out paths that no longer exist on disk
        recent = [p for p in recent if os.path.isfile(p)]
        if not recent:
            self._recent_menu.add_command(label="(no recent files)",
                                          state="disabled")
            return
        for path in recent:
            # Show just the filename in the menu, but pass the full path to open
            label = os.path.basename(path)
            self._recent_menu.add_command(
                label=label,
                command=lambda p=path: self._open_file(p),
            )
        self._recent_menu.add_separator()
        self._recent_menu.add_command(label="Clear recent files",
                                      command=self._clear_recent)

    def _clear_recent(self):
        """Wipe the recent-files list from the config."""
        cfg = self._load_config()
        cfg["recent_files"] = []
        self._save_config(cfg)
        self._rebuild_recent_menu()

    # ── Save / Load ───────────────────────────────────────────────────────────

    def new_map(self):
        """Clear everything and start a fresh, unnamed map."""
        if not self._confirm_discard():
            return
        self._push_undo()
        self.nodes.clear()
        self.edges.clear()
        self.selected = None
        self.connecting_from = None
        self.hover_edge = None
        self._current_file = None
        self._unsaved = False
        self._undo_stack.clear()
        self._update_title()
        self.redraw()
        self.set_status("New map. Add nodes to get started.")

    def save_map(self, event=None):
        """Save to the current file.  If no file is open, fall back to Save As."""
        self._do_save(self._current_file)

    def save_map_as(self, event=None):
        """Always prompt for a new file path regardless of current state."""
        self._do_save(None)

    def _do_save(self, path) -> bool:
        """Write the map to 'path'.  If path is None, prompt for one first.

        Returns True on success, False if the user cancels or an error occurs.
        """
        if not path:
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save puzzle map",
                parent=self,
            )
        if not path:
            return False   # user cancelled the dialog

        data = {
            "version": 1,           # schema version for future compatibility
            "nodes": self.nodes,
            "edges": self.edges,
            "node_count": self.node_count,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            messagebox.showerror("Save failed", str(e), parent=self)
            return False

        self._mark_saved(path)
        self.set_status(f"Saved to {os.path.basename(path)}.")
        return True

    def load_map(self, event=None):
        """Prompt for a file path and open it."""
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open puzzle map",
            parent=self,
        )
        if path:
            self._open_file(path)

    def _open_file(self, path: str):
        """Load a map from 'path', with validation and error handling."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            # Basic schema validation before accepting the data
            if not isinstance(data.get("nodes"), dict):
                raise ValueError("'nodes' must be a dict.")
            if not isinstance(data.get("edges"), list):
                raise ValueError("'edges' must be a list.")

            # Validate each node has the required fields and a known type
            for nid, n in data["nodes"].items():
                for field in ("id", "type", "label", "x", "y"):
                    if field not in n:
                        raise ValueError(
                            f"Node '{nid}' is missing required field '{field}'."
                        )
                if n["type"] not in NODE_TYPES:
                    raise ValueError(
                        f"Node '{nid}' has unknown type '{n['type']}'."
                    )

        except (json.JSONDecodeError, ValueError, OSError) as e:
            messagebox.showerror("Load failed",
                                 f"Could not load map:\n{e}", parent=self)
            return

        self._push_undo()
        self.nodes = data["nodes"]
        self.edges = [tuple(e) for e in data["edges"]]
        self.node_count = data.get("node_count", len(self.nodes))
        self.selected = None
        self.connecting_from = None
        self.hover_edge = None
        self.drag_data = {}
        self._mark_saved(path)   # clears the dirty flag and updates the title
        self.redraw()
        self.set_status(f"Opened {os.path.basename(path)}.")

    def clear_all(self):
        """Ask for confirmation, then wipe all nodes and edges."""
        if not messagebox.askyesno("Clear all",
                                   "Remove all nodes and connections?",
                                   parent=self):
            return
        self._push_undo()
        self.nodes.clear()
        self.edges.clear()
        self.selected = None
        self.connecting_from = None
        self.hover_edge = None
        self.redraw()
        self.set_status("Cleared.")

    # ── Example seed ─────────────────────────────────────────────────────────

    def _seed_example(self):
        """Schedule example placement after the window is fully drawn so that
        winfo_width/height return real pixel values."""
        self.after(100, self._place_example)

    def _place_example(self):
        """Populate the canvas with a small illustrative dungeon puzzle."""
        cw = self.canvas.winfo_width() or 900
        ch = self.canvas.winfo_height() or 550
        cx, cy = cw // 2, ch // 2

        example_nodes = [
            ("n1", "start",  "Enter dungeon",   cx - 340, cy),
            ("n2", "clue",   "Riddle on wall",  cx - 160, cy - 100),
            ("n3", "puzzle", "Pressure plate",  cx - 160, cy + 100),
            ("n4", "key",    "Bronze key",      cx + 40,  cy - 100),
            ("n5", "puzzle", "Locked chest",    cx + 40,  cy + 100),
            ("n6", "goal",   "Exit door opens", cx + 260, cy),
        ]
        for nid, ntype, label, x, y in example_nodes:
            self.nodes[nid] = {
                "id": nid, "type": ntype, "label": label, "x": x, "y": y
            }
        self.node_count = 6
        self.edges = [
            ("n1", "n2"), ("n1", "n3"),
            ("n2", "n4"), ("n3", "n5"),
            ("n4", "n5"), ("n5", "n6"),
        ]
        self.redraw()
        self.set_status(
            "Example loaded. Click a node to select, drag to move, press C to connect."
        )


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


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PuzzlePlotter()
    app.mainloop()
