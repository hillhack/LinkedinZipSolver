"""Tkinter visualization for Zip Game solutions."""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple
from models import GridParseResult

class ZipGameVisualizer:
    def __init__(self, root, parse_result: GridParseResult, solution_path: List[Tuple[int, int]]):
        self.root = root
        self.grid = parse_result.grid
        self.rows = parse_result.rows
        self.cols = parse_result.cols
        self.blocked_edges = parse_result.blocked_edges
        self.solution_path = solution_path or []
        self.cell_size = 55
        self.margin = 40
        self.current_step = 0
        self.animation_speed = 350
        self.playing = False
        self.build_ui()
        self.draw_grid()

    def build_ui(self):
        self.top = tk.Toplevel(self.root)
        self.top.title("Zip Game Solution")
        canvas_w = self.cols * self.cell_size + 2 * self.margin
        canvas_h = self.rows * self.cell_size + 2 * self.margin
        self.top.geometry(f"{canvas_w + 60}x{canvas_h + 220}")
        
        main = ttk.Frame(self.top, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(main, width=canvas_w, height=canvas_h, bg='white')
        self.canvas.pack(pady=(0, 15))
        
        ctrl = ttk.Frame(main)
        ctrl.pack(fill=tk.X, pady=5)
        
        btns = ttk.Frame(ctrl)
        btns.pack(fill=tk.X, pady=5)
        
        ttk.Button(btns, text="⏮️ Start", command=self.go_to_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="⏪ Prev", command=self.previous_step).pack(side=tk.LEFT, padx=2)
        self.play_btn = ttk.Button(btns, text="▶️ Play", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="⏩ Next", command=self.next_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="⏭️ End", command=self.go_to_end).pack(side=tk.LEFT, padx=2)
        
        sp = ttk.Frame(ctrl)
        sp.pack(fill=tk.X, pady=5)
        ttk.Label(sp, text="Speed:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.IntVar(value=self.animation_speed)
        ttk.Scale(sp, from_=100, to=1000, variable=self.speed_var, 
                 command=lambda v: setattr(self, 'animation_speed', int(float(v)))).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        info = ttk.Frame(ctrl)
        info.pack(fill=tk.X, pady=5)
        self.step_label = ttk.Label(info, text="Step: 0/0", font=("Arial", 10, "bold"))
        self.step_label.pack()
        self.detail_label = ttk.Label(info, text="Position: (0,0)", font=("Arial", 9))
        self.detail_label.pack()
        
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(ctrl, variable=self.progress_var, maximum=100).pack(fill=tk.X, pady=5)
        self.status_label = ttk.Label(ctrl, text="Ready", font=("Arial", 9))
        self.status_label.pack()

    def draw_grid(self):
        self.canvas.delete("all")
        
        # Draw cells
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = self.margin + c * self.cell_size
                y1 = self.margin + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                val = self.grid[r][c]
                if val > 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e3f2fd", outline="#2196f3", width=2)
                    self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2, 
                                          text=str(val), font=("Arial", 14, "bold"), fill="#1976d2")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#f5f5f5", outline="#cccccc", width=1)
        
        # Draw walls
        for edge in self.blocked_edges:
            a, b = tuple(edge)
            (r1, c1), (r2, c2) = a, b
            x1 = self.margin + c1 * self.cell_size + self.cell_size / 2
            y1 = self.margin + r1 * self.cell_size + self.cell_size / 2
            x2 = self.margin + c2 * self.cell_size + self.cell_size / 2
            y2 = self.margin + r2 * self.cell_size + self.cell_size / 2
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=6)
        
        # Draw solution path
        if self.solution_path and self.current_step > 0:
            self.draw_solution_path()
        
        self.update_display()

    def draw_solution_path(self):
        path = self.solution_path[:self.current_step + 1]
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            x1 = self.margin + c1 * self.cell_size + self.cell_size // 2
            y1 = self.margin + r1 * self.cell_size + self.cell_size // 2
            x2 = self.margin + c2 * self.cell_size + self.cell_size // 2
            y2 = self.margin + r2 * self.cell_size + self.cell_size // 2
            arrow = tk.LAST if i == len(path) - 2 else None
            self.canvas.create_line(x1, y1, x2, y2, fill="#4caf50", width=3, arrow=arrow)
        
        for i, (r, c) in enumerate(path):
            x1 = self.margin + c * self.cell_size + 8
            y1 = self.margin + r * self.cell_size + 8
            x2 = x1 + self.cell_size - 16
            y2 = y1 + self.cell_size - 16
            if i == len(path) - 1:
                self.canvas.create_oval(x1, y1, x2, y2, fill="#f44336", outline="#d32f2f", width=2)
            else:
                self.canvas.create_oval(x1, y1, x2, y2, fill="#c8e6c9", outline="#388e3c", width=1)

    def update_display(self):
        if not self.solution_path:
            return
            
        total_steps = len(self.solution_path) - 1
        progress = (self.current_step / total_steps * 100) if total_steps > 0 else 0
        
        self.step_label.config(text=f"Step: {self.current_step}/{total_steps}")
        self.progress_var.set(progress)
        
        if self.current_step < len(self.solution_path):
            pos = self.solution_path[self.current_step]
            val = self.grid[pos[0]][pos[1]]
            self.detail_label.config(text=f"Position: {pos} | Value: {val if val > 0 else 'Path'}")
        
        if self.current_step == total_steps:
            self.status_label.config(text="✅ Complete!", foreground="green")
        elif self.playing:
            self.status_label.config(text="🔴 Playing...", foreground="red")
        else:
            self.status_label.config(text="⏸️ Paused", foreground="orange")

    def toggle_play(self):
        if self.playing:
            self.pause()
        else:
            self.play()

    def play(self):
        if not self.solution_path or self.playing:
            return
        self.playing = True
        self.play_btn.config(text="⏸️ Pause")
        self.animate_step()

    def pause(self):
        self.playing = False
        self.play_btn.config(text="▶️ Play")

    def animate_step(self):
        if not self.playing or self.current_step >= len(self.solution_path) - 1:
            self.pause()
            return
            
        self.current_step += 1
        self.draw_grid()
        
        if self.playing and self.current_step < len(self.solution_path) - 1:
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