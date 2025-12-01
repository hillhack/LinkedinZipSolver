"""
Tkinter visualization for Zip Game solutions.
Clean, optimized rewrite.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple
from models import GridParseResult


class ZipGameVisualizer:
    def __init__(self, root, parse_result: GridParseResult, solution_path: List[Tuple[int, int]]):
        self.root = root

        # Game data
        self.grid = parse_result.grid
        self.rows = parse_result.rows
        self.cols = parse_result.cols
        self.blocked_edges = parse_result.blocked_edges
        self.solution_path = solution_path or []

        # UI state
        self.cell_size = 55
        self.margin = 40
        self.current_step = 0
        self.animation_speed = 350
        self.playing = False

        self.build_ui()
        self.draw_grid()

    # -------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------
    def build_ui(self):
        self.top = tk.Toplevel(self.root)
        self.top.title("Zip Game Solution")

        canvas_w = self.cols * self.cell_size + 2 * self.margin
        canvas_h = self.rows * self.cell_size + 2 * self.margin
        self.top.geometry(f"{canvas_w + 60}x{canvas_h + 220}")

        main = ttk.Frame(self.top, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # Canvas (grid area)
        self.canvas = tk.Canvas(main, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack(pady=(0, 12))

        # --- Controls ---
        ctrl = ttk.Frame(main)
        ctrl.pack(fill=tk.X)

        # Navigation buttons
        btn_row = ttk.Frame(ctrl)
        btn_row.pack(pady=4)

        ttk.Button(btn_row, text="⏮ Start", command=self.go_to_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="⏪ Prev", command=self.previous_step).pack(side=tk.LEFT, padx=2)

        self.play_btn = ttk.Button(btn_row, text="▶ Play", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_row, text="⏩ Next", command=self.next_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="⏭ End", command=self.go_to_end).pack(side=tk.LEFT, padx=2)

        # Speed slider
        speed_row = ttk.Frame(ctrl)
        speed_row.pack(fill=tk.X, pady=4)
        ttk.Label(speed_row, text="Speed:").pack(side=tk.LEFT)

        self.speed_var = tk.IntVar(value=self.animation_speed)
        ttk.Scale(
            speed_row, from_=100, to=1000, variable=self.speed_var,
            command=lambda v: setattr(self, 'animation_speed', int(float(v)))
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Status area
        info_row = ttk.Frame(ctrl)
        info_row.pack(fill=tk.X, pady=6)

        self.step_label = ttk.Label(info_row, text="Step: 0/0", font=("Arial", 10, "bold"))
        self.step_label.pack()

        self.detail_label = ttk.Label(info_row, text="Position: (0,0)", font=("Arial", 9))
        self.detail_label.pack()

        # Progress
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(ctrl, variable=self.progress_var, maximum=100).pack(fill=tk.X, pady=4)

        self.status_label = ttk.Label(ctrl, text="Ready", font=("Arial", 9))
        self.status_label.pack()

    # -------------------------------------------------------
    # DRAWING
    # -------------------------------------------------------
    def draw_grid(self):
        self.canvas.delete("all")

        # Draw cells + numbers + walls + path
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = self.margin + c * self.cell_size
                y1 = self.margin + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                val = self.grid[r][c]

                if val > 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 fill="#e3f2fd", outline="#2196f3", width=2)
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                            text=str(val), font=("Arial", 14, "bold"), fill="#1976d2")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 fill="#f5f5f5", outline="#bbbbbb", width=1)

        # Inline walls
        for edge in self.blocked_edges:
            (r1, c1), (r2, c2) = list(edge)
            if r1 == r2:  # Vertical
                col = max(c1, c2)
                x = self.margin + col * self.cell_size
                y1_ = self.margin + r1 * self.cell_size
                y2_ = y1_ + self.cell_size
                self.canvas.create_line(x, y1_, x, y2_, fill="black", width=4)
            elif c1 == c2:  # Horizontal
                row = max(r1, r2)
                y = self.margin + row * self.cell_size
                x1_ = self.margin + c1 * self.cell_size
                x2_ = x1_ + self.cell_size
                self.canvas.create_line(x1_, y, x2_, y, fill="black", width=4)

        # Draw path
        if self.solution_path and self.current_step > 0:
            self.draw_solution_path()

        # Inline update_display
        if self.solution_path:
            total = len(self.solution_path) - 1
            progress = (self.current_step / total * 100) if total > 0 else 0
            self.step_label.config(text=f"Step: {self.current_step}/{total}")
            self.progress_var.set(progress)
            pos = self.solution_path[self.current_step]
            val = self.grid[pos[0]][pos[1]]
            self.detail_label.config(text=f"Position: {pos} | Value: {val if val > 0 else 'Path'}")
            if self.current_step == total:
                self.status_label.config(text="✅ Complete!", foreground="green")
            elif self.playing:
                self.status_label.config(text="▶ Playing...", foreground="blue")
            else:
                self.status_label.config(text="⏸ Paused", foreground="orange")


    # -------------------------------------------------------
    # PATH RENDERING
    # -------------------------------------------------------
    def draw_solution_path(self):
        path = self.solution_path[:self.current_step + 1]

        # Lines first
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            x1 = self.margin + c1 * self.cell_size + self.cell_size // 2
            y1 = self.margin + r1 * self.cell_size + self.cell_size // 2
            x2 = self.margin + c2 * self.cell_size + self.cell_size // 2
            y2 = self.margin + r2 * self.cell_size + self.cell_size // 2

            self.canvas.create_line(x1, y1, x2, y2, fill="#4caf50", width=3)

        # Draw small center dots
        for i, (r, c) in enumerate(path):
            cx = self.margin + c * self.cell_size + self.cell_size // 2
            cy = self.margin + r * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 4
            if i == len(path) - 1:
                fill, outline = "#f44336", "#d32f2f"
            else:
                fill, outline = "#c8e6c9", "#388e3c"
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=fill, outline=outline, width=2
            )

        # Redraw numbers on top for visited numbered cells
        for r, c in path:
            val = self.grid[r][c]
            if val > 0:
                x1 = self.margin + c * self.cell_size
                y1 = self.margin + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_text(
                    (x1 + x2)/2, (y1 + y2)/2,
                    text=str(val), font=("Arial", 14, "bold"), fill="#1976d2"
                )


    # -------------------------------------------------------
    # CONTROLS (concise)
    # -------------------------------------------------------
    def toggle_play(self):
        if self.playing:
            self.playing = False
            self.play_btn.config(text="▶ Play")
        else:
            if self.solution_path and not self.playing:
                self.playing = True
                self.play_btn.config(text="⏸ Pause")
                self.animate_step()

    def animate_step(self):
        if not self.playing or self.current_step >= len(self.solution_path) - 1:
            self.playing = False
            self.play_btn.config(text="▶ Play")
            return
        self.current_step += 1
        self.draw_grid()
        if self.playing:
            self.top.after(self.animation_speed, self.animate_step)

    def next_step(self):
        if self.current_step < len(self.solution_path) - 1:
            self.current_step += 1
            self.draw_grid()

    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.draw_grid()

    def go_to_start(self):
        self.current_step = 0
        self.draw_grid()

    def go_to_end(self):
        self.current_step = len(self.solution_path) - 1
        self.draw_grid()
